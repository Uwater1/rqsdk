import pandas as pd
import numpy as np
from datetime import timedelta
import math
from alpha_finder import AlphaFinder
import spread

# We will implement the skeleton of the backtest loop here first
class JEPICNStrategy:
    def __init__(self, start_date='2025-12-23', end_date='2026-03-23'):
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)

        # Portfolio setup
        self.shares = 20000
        self.cash = 100000  # Initial cash buffer for margin/put spread
        self.positions = []
        self.alpha_finder = AlphaFinder()

        self.initial_equity = None
        self.portfolio_history = []

        self.load_data()

    def load_data(self):
        print("Loading data...")
        self.etf_prices = pd.read_parquet('data/510300_1d.parquet')
        self.etf_prices['date'] = pd.to_datetime(self.etf_prices['date'])
        self.etf_prices = self.etf_prices[(self.etf_prices['date'] >= self.start_date) &
                                          (self.etf_prices['date'] <= self.end_date)]
        self.etf_prices = self.etf_prices.sort_values('date').reset_index(drop=True)

        self.inst = pd.read_parquet('data/300ETF_instruments.parquet')

        self.opt_prices = pd.read_parquet('data/300ETF_historical_prices.parquet')
        self.opt_prices['date'] = pd.to_datetime(self.opt_prices['date'])
        self.opt_prices = self.opt_prices[(self.opt_prices['date'] >= self.start_date) &
                                          (self.opt_prices['date'] <= self.end_date)]

        # Merge option prices with instruments to get strike, maturity, etc.
        # strike_price is in both, so we drop from historical_prices
        self.opt_prices = self.opt_prices.drop(columns=['strike_price'], errors='ignore')
        self.merged_opt = self.opt_prices.merge(
            self.inst[['order_book_id', 'symbol', 'strike_price', 'maturity_date', 'option_type']],
            on='order_book_id', how='left'
        )
        self.merged_opt['maturity_date'] = pd.to_datetime(self.merged_opt['maturity_date'])
        print("Data loaded successfully.")

    def run_backtest(self):
        print("Running backtest loop...")

        last_trade_date = None

        for idx, row in self.etf_prices.iterrows():
            current_date = row['date']
            current_price = row['close']

            # Monthly rollover check
            # We open positions if we have none, or if our previous options are expiring within 7 days
            needs_rollover = False

            if not self.positions:
                needs_rollover = True
            else:
                # Check closest maturity
                maturities = [pos['maturity_date'] for pos in self.positions]
                closest_maturity = min(maturities)
                days_to_expiry = (closest_maturity - current_date).days
                if days_to_expiry <= 5: # Rollover 5 days before expiry
                    needs_rollover = True

            if needs_rollover:
                # 1. Close existing positions
                self._close_positions(current_date, current_price)

                # 2. Open new positions
                self._open_positions(current_date, current_price)

                last_trade_date = current_date

            # Record Portfolio History
            equity = self.shares * current_price + self.cash

            # Mark-to-Market: dynamically estimate open option positions value using today's prices
            options_value = 0
            options_today = self.merged_opt[self.merged_opt['date'] == current_date]

            for pos in self.positions:
                opt_data = options_today[options_today['order_book_id'] == pos['order_book_id']]

                # Default to entry price if no market data today
                current_val = pos['entry_price']

                if not opt_data.empty:
                    midprice = opt_data['close'].values[0]
                    days_to_expire = (pos['maturity_date'] - current_date).days

                    is_short = pos['contracts'] < 0

                    try:
                        res = spread.predict_spread(midprice, pos['order_book_id'], pos['type'],
                                                    pos['strike'], days_to_expire, current_price)
                        if res:
                            _, bid, ask = res
                        else:
                            bid = ask = midprice
                    except:
                        bid = ask = midprice

                    # If we are short, it costs us 'ask' to close. Thus our liability is negative 'ask' * contracts
                    # Since contracts is already negative, we multiply by 'ask' to get the negative liability.
                    current_val = ask if is_short else bid

                options_value += pos['contracts'] * current_val * pos['multiplier']

            total_equity = equity + options_value

            if self.initial_equity is None:
                self.initial_equity = total_equity

            self.portfolio_history.append({
                'date': current_date,
                'etf_price': current_price,
                'stock_value': self.shares * current_price,
                'cash': self.cash,
                'options_value': options_value,
                'total_equity': total_equity
            })

        print("\nBacktest completed.")
        final_equity = self.portfolio_history[-1]['total_equity']
        return_pct = (final_equity / self.initial_equity - 1) * 100
        print(f"Initial Equity: {self.initial_equity:,.2f}")
        print(f"Final Equity:   {final_equity:,.2f}")
        print(f"Total Return:   {return_pct:.2f}%")

    def _close_positions(self, current_date, current_price):
        """Close existing options."""
        close_pnl = 0
        for pos in self.positions:
            # Find current price of this option to close it
            # We must buy back sold options (Ask), and sell bought options (Bid)
            options_today = self.merged_opt[self.merged_opt['date'] == current_date]
            opt_data = options_today[options_today['order_book_id'] == pos['order_book_id']]

            if opt_data.empty:
                # If option data is missing, we assume it expired worthless (if out of money)
                # For a rough approximation, we'll check intrinsic value
                is_call = pos['type'] == 'C'
                intrinsic = max(0, current_price - pos['strike']) if is_call else max(0, pos['strike'] - current_price)
                close_price = intrinsic
            else:
                midprice = opt_data['close'].values[0]
                days_to_expire = (pos['maturity_date'] - current_date).days

                # We sold this option -> we must buy it back at ASK
                # We bought this option -> we must sell it at BID
                is_sell_to_close = pos['contracts'] > 0 # We own > 0 contracts, so we sell to close

                try:
                    res = spread.predict_spread(midprice, pos['order_book_id'], pos['type'],
                                                pos['strike'], days_to_expire, current_price)
                    if res:
                        _, bid, ask = res
                    else:
                        bid = ask = midprice
                except:
                    bid = ask = midprice

                close_price = bid if is_sell_to_close else ask

            # Calculate cash flow to close the position
            # If contracts < 0 (we are short), we need to buy back -> cash decreases
            # If contracts > 0 (we are long), we sell -> cash increases
            cash_flow = pos['contracts'] * close_price * pos['multiplier']
            self.cash += cash_flow

            pnl = cash_flow + (-pos['contracts'] * pos['entry_price'] * pos['multiplier'])
            close_pnl += pnl

            print(f"[{current_date.date()}] Closing {pos['type']} (K={pos['strike']}). Close Price: {close_price:.4f}. Cash Flow: {cash_flow:.2f}. PnL: {pnl:.2f}")

        self.positions = []

    def _find_available_options(self, current_date, target_maturity=None):
        """Find option chain available on current_date."""
        options_today = self.merged_opt[self.merged_opt['date'] == current_date].copy()
        if options_today.empty:
            return None

        # Filter by maturity date
        maturities = options_today['maturity_date'].unique()
        maturities = np.sort(maturities)

        # We want options expiring roughly in ~30 days, or the nearest next month contract
        valid_maturities = [m for m in maturities if (m - current_date).days >= 15]

        if not valid_maturities:
            return None

        selected_maturity = valid_maturities[0]
        return options_today[options_today['maturity_date'] == selected_maturity]

    def _open_positions(self, current_date, current_price):
        """Open new options."""
        print(f"[{current_date.date()}] ETF price: {current_price:.3f}. Finding strikes via Alpha Finder...")

        # 1. Use Alpha Finder to select strikes
        target_strikes = self.alpha_finder.select_strikes(current_price, current_date)

        # 2. Find available options for the next month
        options_chain = self._find_available_options(current_date)

        if options_chain is None or options_chain.empty:
            print(f"[{current_date.date()}] No options available to open.")
            return

        maturity_date = options_chain['maturity_date'].iloc[0]
        days_to_expire = (maturity_date - current_date).days

        # Find closest match for strikes in the options chain
        def find_closest_strike(chain, opt_type, target_strike):
            subset = chain[chain['option_type'] == opt_type]
            if subset.empty:
                return None
            idx = (subset['strike_price'] - target_strike).abs().idxmin()
            return subset.loc[idx]

        call_A = find_closest_strike(options_chain, 'C', target_strikes['call_strike_A'])
        call_B = find_closest_strike(options_chain, 'C', target_strikes['call_strike_B'])
        put_sell = find_closest_strike(options_chain, 'P', target_strikes['put_strike_sell'])
        put_buy = find_closest_strike(options_chain, 'P', target_strikes['put_strike_buy'])

        def execute_trade(opt, amount, is_sell):
            if opt is None:
                return

            # Use Mid-price
            # In rqdatac data, close is typically settlement or close. Let's use close.
            midprice = opt['close']
            ticker = opt['symbol']  # or order_book_id

            # Predict Bid-Ask Spread
            # spread.predict_spread(midprice, ticker, option_type, strike, days_to_expire, future_price)
            # using current_price as proxy for future_price
            try:
                # spread.predict_spread needs the order_book_id and extract_ticker_prefix handles it
                res = spread.predict_spread(midprice, opt['order_book_id'], opt['option_type'],
                                            opt['strike_price'], days_to_expire, current_price)
                if res:
                    _, bid, ask = res
                else:
                    bid = ask = midprice
            except Exception as e:
                bid = ask = midprice

            # If selling, we hit the Bid price. If buying, we hit the Ask price.
            execution_price = bid if is_sell else ask

            if pd.isna(execution_price) or execution_price <= 0:
                execution_price = midprice

            multiplier = 10000 # 300ETF multiplier
            if 'contract_multiplier' in opt:
                multiplier = opt['contract_multiplier']

            # Update cash
            trade_value = execution_price * multiplier * abs(amount)
            if is_sell:
                self.cash += trade_value
                print(f"  -> Sold {abs(amount)}x {opt['symbol']} (K={opt['strike_price']}) at {execution_price:.4f} [Mid:{midprice:.4f}]")
            else:
                self.cash -= trade_value
                print(f"  -> Bought {abs(amount)}x {opt['symbol']} (K={opt['strike_price']}) at {execution_price:.4f} [Mid:{midprice:.4f}]")

            self.positions.append({
                'symbol': opt['symbol'],
                'order_book_id': opt['order_book_id'],
                'type': opt['option_type'],
                'strike': opt['strike_price'],
                'maturity_date': maturity_date,
                'contracts': -amount if is_sell else amount,
                'multiplier': multiplier,
                'entry_price': execution_price
            })

        # Covered Call: Sell 1 of Call A, Sell 1 of Call B
        # ETF shares = 20,000. 1 contract = 10,000 shares. Total 2 contracts.
        execute_trade(call_A, 1, is_sell=True)
        execute_trade(call_B, 1, is_sell=True)

        # Bull Put Spread: Sell 1 Put (support), Buy 1 Put (further OTM)
        execute_trade(put_sell, 1, is_sell=True)
        execute_trade(put_buy, 1, is_sell=False)

if __name__ == '__main__':
    strategy = JEPICNStrategy()
    strategy.run_backtest()
