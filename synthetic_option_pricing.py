import os
import math
import re
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from numba_utils import process_synthetic_strikes_loop, black_price, black_iv

# Initialize rqdatac for trading calendar

# --- Configuration ---
UNDERLYINGS = ['510050.XSHG', '510300.XSHG', '510500.XSHG']
SYMBOL_MAP = {
    '510050.XSHG': '50ETF',
    '510300.XSHG': '300ETF',
    '510500.XSHG': '500ETF',
}
DATA_DIR = 'data'
RFR_FILE = os.path.join(DATA_DIR, 'interest_free_rate.csv')
SLIPPAGE = 0.02

# --- Calendar Logic ---
class TargetExpiryGenerator:
    WEEKDAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    _trading_dates_cache = None

    @staticmethod
    def get_trading_dates():
        """Retrieve and cache trading dates for fast lookup."""
        if TargetExpiryGenerator._trading_dates_cache is None:
            # Load a wide range of trading dates to handle all historical and near-future targets
            dates = pd.date_range(start='2015-01-01', end='2027-12-31', freq='B')
            TargetExpiryGenerator._trading_dates_cache = sorted([pd.Timestamp(d) for d in dates])
        return TargetExpiryGenerator._trading_dates_cache

    @staticmethod
    def get_tag(date):
        wd = date.weekday()
        if wd > 4: return None
        n = (date.day - 1) // 7 + 1
        return f"{n}{'st' if n==1 else 'nd' if n==2 else 'rd' if n==3 else 'th'} {TargetExpiryGenerator.WEEKDAY_NAMES[wd][:3]}"

    @staticmethod
    def get_date_by_n_weekday(year, month, n, weekday):
        """Find the n-th occurrence of a weekday in a given month."""
        first_day = datetime(year, month, 1)
        first_occurrence_offset = (weekday - first_day.weekday()) % 7
        target_date = first_day + timedelta(days=first_occurrence_offset + (n - 1) * 7)
        if target_date.month == month:
            return target_date
        return None

    @staticmethod
    def get_target_expiries(current_date):
        """Implement 'Same Tag Next Month' logic with holiday handling."""
        tag = TargetExpiryGenerator.get_tag(current_date)
        if not tag: return []

        # Match tag (e.g., '3rd Fri') to n=3, weekday=4
        match = re.search(r'(\d+)\w+ (\w+)', tag)
        if not match: return []
        n = int(match.group(1))
        wd_str = match.group(2)
        wd_idx = [name[:3] for name in TargetExpiryGenerator.WEEKDAY_NAMES].index(wd_str)

        # Determine target month
        if current_date.month == 12:
            next_month, next_year = 1, current_date.year + 1
        else:
            next_month, next_year = current_date.month + 1, current_date.year

        target_date = TargetExpiryGenerator.get_date_by_n_weekday(next_year, next_month, n, wd_idx)

        # If target doesn't exist (e.g., 5th Monday in Feb), discard
        if not target_date:
            return []
            
        # Holiday handling: use next nearest trading date
        all_trading_dates = TargetExpiryGenerator.get_trading_dates()
        target_ts = pd.Timestamp(target_date)

        import bisect
        idx = bisect.bisect_left(all_trading_dates, target_ts)
        if idx < len(all_trading_dates):
            final_target = all_trading_dates[idx]
        else:
            return [] # fallback
            
        days = (final_target - current_date).days
        return [{
            'expiry_date': final_target,
            'tag': tag,
            'T_star': days / 365.0,
            'days': days
        }]

# --- Core Processor ---
def process_underlying(underlying_symbol):
    prefix = SYMBOL_MAP[underlying_symbol]
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Processing {prefix} ({underlying_symbol})...")
    
    # Load and clean Data
    inst_df = pd.read_parquet(os.path.join(DATA_DIR, f"{prefix}_instruments.parquet"))
    prices_df = pd.read_parquet(os.path.join(DATA_DIR, f"{prefix}_historical_prices.parquet"))
    spot_file = f"{underlying_symbol.split('.')[0]}_1d.parquet" if prefix == '300ETF' else f"{prefix}_1d.parquet"
    spot_df = pd.read_parquet(os.path.join(DATA_DIR, spot_file))
    rfr_df = pd.read_csv(RFR_FILE, parse_dates=['trading_date'])
    
    rfr_map = rfr_df.set_index('trading_date')['1Y'].to_dict()
    prices_df['date'] = pd.to_datetime(prices_df['date'])
    spot_df['date'] = pd.to_datetime(spot_df['date'])
    spot_map = spot_df.set_index('date')['close'].to_dict()
    spot_df = spot_df.set_index('date').sort_index()
    
    # Add maturity info
    if 'strike_price' in prices_df.columns:
        prices_df = prices_df.drop(columns=['strike_price'])
    full_data = prices_df.merge(inst_df[['order_book_id', 'maturity_date', 'option_type', 'strike_price']], on='order_book_id')
    full_data['maturity_date'] = pd.to_datetime(full_data['maturity_date'])

    # Deduplicate
    full_data = (full_data
                 .sort_values('volume', ascending=False)
                 .drop_duplicates(subset=['date', 'strike_price', 'option_type', 'maturity_date'], keep='first'))
    
    results = []
    trading_dates = sorted(full_data['date'].unique())
    total_dates = len(trading_dates)
    
    for i, dt in enumerate(trading_dates):
        dt_pd = pd.Timestamp(dt)
        s0 = spot_map.get(dt_pd)
        r = rfr_map.get(dt_pd)
        if s0 is None or r is None: continue
        
        targets = TargetExpiryGenerator.get_target_expiries(dt_pd)
        if not targets: continue

        # Get data for this day
        day_data = full_data[full_data['date'] == dt_pd]
        listed_mats = sorted(day_data['maturity_date'].unique())
        
        # Pre-pivot prices for fast lookup
        price_pivot = day_data.pivot(index=['strike_price', 'option_type'], columns='maturity_date', values='close')
        
        for tgt in targets:
            t_star_dt = tgt['expiry_date']
            t_star = tgt['T_star']

            # Find bracketing: T1 <= T* < T2 or T1 < T* <= T2
            t1_dt = None
            t2_dt = None
            exact_match = False
            for lm in listed_mats:
                if lm == t_star_dt:
                    exact_match = True
                    t1_dt = lm
                    t2_dt = lm
                    break
                elif lm < t_star_dt:
                    t1_dt = lm
                elif lm > t_star_dt:
                    t2_dt = lm
                    break

            if t1_dt is None or t2_dt is None: continue

            etf_expiry_dates = spot_df.index[spot_df.index <= t_star_dt] if 'spot_df' in locals() and hasattr(spot_df, 'index') else pd.DatetimeIndex([])
            if etf_expiry_dates.empty:
                st = spot_map.get(t_star_dt)
            else:
                st = spot_df.loc[etf_expiry_dates[-1], 'close']

            T1 = max((t1_dt - dt_pd).days / 365.0, 1e-6)
            T2 = (t2_dt - dt_pd).days / 365.0

            if T1 == T2:
                T2 = T1 + 1e-6

            # Robust Forward calculation (Median of near-ATM strikes)
            def get_robust_forward(mat_dt, T, spot):
                mask = (price_pivot.index.get_level_values('strike_price') >= spot * 0.9) & \
                       (price_pivot.index.get_level_values('strike_price') <= spot * 1.1)
                atm_data = price_pivot.loc[mask, mat_dt].unstack()
                if 'C' not in atm_data or 'P' not in atm_data:
                    return spot * math.exp(r * T)

                atm_pairs = atm_data.dropna(subset=['C', 'P'])
                if atm_pairs.empty: return spot * math.exp(r * T)

                k_vec = atm_pairs.index.values
                c_vec = atm_pairs['C'].values
                p_vec = atm_pairs['P'].values
                f_vec = k_vec + (c_vec - p_vec) * math.exp(r * T)
                return np.median(f_vec)

            F1 = get_robust_forward(t1_dt, T1, s0)
            F2 = get_robust_forward(t2_dt, T2, s0)

            # Pre-filter strikes available at BOTH maturities
            avail_c1 = price_pivot.xs('C', level='option_type')[t1_dt].dropna().index
            avail_p1 = price_pivot.xs('P', level='option_type')[t1_dt].dropna().index
            if exact_match:
                avail_c2 = avail_c1
                avail_p2 = avail_p1
            else:
                avail_c2 = price_pivot.xs('C', level='option_type')[t2_dt].dropna().index
                avail_p2 = price_pivot.xs('P', level='option_type')[t2_dt].dropna().index
            
            shared_strikes = sorted(set(avail_c1) & set(avail_p1) & set(avail_c2) & set(avail_p2))
            if not shared_strikes: continue
            
            # Prepare arrays for Numba
            num_s = len(shared_strikes)
            c1_vec = np.array([price_pivot.loc[(k, 'C'), t1_dt] for k in shared_strikes])
            p1_vec = np.array([price_pivot.loc[(k, 'P'), t1_dt] for k in shared_strikes])
            c2_vec = np.array([price_pivot.loc[(k, 'C'), t2_dt] for k in shared_strikes])
            p2_vec = np.array([price_pivot.loc[(k, 'P'), t2_dt] for k in shared_strikes])
            strikes_vec = np.array(shared_strikes)
            
            # Execute Numba core loop
            batch_results = process_synthetic_strikes_loop(
                strikes_vec, c1_vec, p1_vec, c2_vec, p2_vec,
                s0, r, T1, T2, t_star, F1, F2
            )

            for idx in range(len(strikes_vec)):
                k = strikes_vec[idx]
                price_c, price_p, iv_star, F_star, _ = batch_results[idx]
                
                if iv_star > 1e-4 and F_star > 1e-3:
                    # Calculate Returns and Worthless Flag
                    # Note: We use st (Expiry Price) which might be None
                    
                    def calc_metrics(opt_price, payoff):
                        if st is None or opt_price <= 0:
                            return None, None, None, None

                        buy_p = opt_price * (1 + SLIPPAGE)
                        sell_p = opt_price * (1 - SLIPPAGE)

                        expire_worthless = 1 if payoff <= 0 else 0
                        ret_long = (payoff - buy_p) / buy_p
                        ret_short = (sell_p - payoff) / sell_p
                        return round(st, 4), expire_worthless, round(ret_long, 4), round(ret_short, 4)

                    # Call
                    st_val, c_worthless, c_ret_l, c_ret_s = calc_metrics(price_c, max(st - k, 0) if st is not None else 0)
                    results.append([
                        dt_pd.strftime('%Y-%m-%d'), t_star_dt.strftime('%Y-%m-%d'), tgt['tag'],
                        round(t_star * 365, 2), k, 'C', round(price_c, 4), round(iv_star, 4), round(F_star, 4),
                        round(s0, 4), st_val, c_worthless, c_ret_l, c_ret_s
                    ])
                    
                    # Put
                    st_val, p_worthless, p_ret_l, p_ret_s = calc_metrics(price_p, max(k - st, 0) if st is not None else 0)
                    results.append([
                        dt_pd.strftime('%Y-%m-%d'), t_star_dt.strftime('%Y-%m-%d'), tgt['tag'],
                        round(t_star * 365, 2), k, 'P', round(price_p, 4), round(iv_star, 4), round(F_star, 4),
                        round(s0, 4), st_val, p_worthless, p_ret_l, p_ret_s
                    ])
        
        if (i+1) % 100 == 0:
            print(f"  Progress: {i+1}/{total_dates} ({(i+1)/total_dates*100:.1f}%) | Date: {dt_pd.date()} | Results: {len(results)}")

    output_file = f"synthetic_options_{prefix}.parquet"
    columns = [
        'Date', 'Target Expiry', 'Weekday Tag', 'DaysToExpiry', 'Strike', 'Option Type', 'Price', 'IV', 'Forward',
        'Underlying Price at Date', 'Underlying Price at Expiry', 'Expire_worthless', 'Exp Ret Long', 'Exp Ret Short'
    ]
    df_results = pd.DataFrame(results, columns=columns)
    df_results['Date'] = pd.to_datetime(df_results['Date'])
    df_results['Target Expiry'] = pd.to_datetime(df_results['Target Expiry'])
    df_results.to_parquet(output_file, index=False)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Finished {prefix}. Saved to {output_file}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--etf', type=str, default='all', choices=['50', '300', '500', 'all'])
    args = parser.parse_args()

    if args.etf == 'all':
        for und in UNDERLYINGS:
            process_underlying(und)
    else:
        symbol = {'50': '510050.XSHG', '300': '510300.XSHG', '500': '510500.XSHG'}[args.etf]
        process_underlying(symbol)
