import os
import glob
import re
import argparse
import pandas as pd
import numpy as np
import itertools
from datetime import datetime
from dateutil.relativedelta import relativedelta

from scipy.stats import norm
from numba import njit, float64, int64, boolean
import math

DEFAULT_CARRY = -0.01  # -1 % annual continuously-compounded
COMMISSION = 1.0       # Per contract, per leg
MULTIPLIER = 100       # IO options multiplier is 100 RMB per point

# Margin and Sizing Constants
MARGIN_RATE = 0.15
CAPITAL_PER_SET = 10000 * 100 
SL_MULTIPLIER = 5.0    # More realistic Stop Loss
MAX_NET_DELTA = 0.1
MAX_ABS_SPREAD = 2.0
MIN_SCORE = 0.005     
TAKE_PROFIT_POINTS = 2.0

def get_third_friday(year, month):
    """Calculate the third Friday of a given month and year."""
    first_day = datetime(year, month, 1)
    first_friday = first_day + relativedelta(days=(4 - first_day.weekday()) % 7)
    third_friday = first_friday + relativedelta(days=14)
    return third_friday

def parse_ticker(ticker):
    """
    Parse a ticker like IO2604C3950.
    Returns: underlying, year, month, type, strike
    """
    match = re.match(r'([A-Z]+)(\d{2})(\d{2})([CP])(\d+)', ticker)
    if match:
        und, yy, mm, typ, strike = match.groups()
        year = 2000 + int(yy)
        month = int(mm)
        return und, year, month, typ, float(strike)
    return None, None, None, None, None

def load_and_align_data(data_dir, underlying='IO'):
    """
    Load all parquet files for a given underlying in the directory,
    extract a1 (ask) and b1 (bid), resample to 1-minute intervals,
    and forward-fill.
    """
    print(f"Loading data from {data_dir} for {underlying}...")
    parquet_files = glob.glob(os.path.join(data_dir, underlying, '*.parquet'))
    
    if not parquet_files:
        print(f"No parquet files found in {os.path.join(data_dir, underlying)}")
        return pd.DataFrame()
    
    all_series = []
    
    for f in parquet_files:
        ticker = os.path.basename(f).replace('.parquet', '')
        und, year, month, typ, strike = parse_ticker(ticker)
        if not und: continue
        
        try:
            df = pd.read_parquet(f)
            # Ensure index is datetime
            if 'datetime' in df.index.names:
                df = df.reset_index()
            elif 'datetime' not in df.columns:
                print(f"No datetime column in {f}")
                continue
                
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.set_index('datetime').sort_index()
            
            # Keep only a1 and b1
            df = df[['a1', 'b1']].rename(columns={'a1': f'{ticker}_ask', 'b1': f'{ticker}_bid'})
            
            # Drop duplicates if any
            df = df[~df.index.duplicated(keep='last')]
            
            all_series.append(df)
        except Exception as e:
            print(f"Error loading {f}: {e}")
            
    print(f"Loaded {len(all_series)} files. Merging and resampling to 1-minute...")
    
    if not all_series:
        return pd.DataFrame()
        
    merged_df = pd.concat(all_series, axis=1)
    resampled_df = merged_df.resample('1min').ffill().dropna(how='all')
    
    return resampled_df

@njit(cache=True)
def _numba_cdf(x):
    """Fast Numba-compatible CDF approximation."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

@njit(cache=True)
def _numba_pdf(x):
    """Fast Numba-compatible PDF."""
    return math.exp(-0.5 * x**2) / math.sqrt(2.0 * math.pi)

@njit(cache=True)
def bs_price_numba(S, K, T, r, sigma, is_call):
    if T <= 0 or sigma <= 0:
        return max(0.0, S - K) if is_call else max(0.0, K - S)
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    if is_call:
        return S * _numba_cdf(d1) - K * math.exp(-r * T) * _numba_cdf(d2)
    else:
        return K * math.exp(-r * T) * _numba_cdf(-d2) - S * _numba_cdf(-d1)

@njit(cache=True)
def implied_vol_newton(price_target, S, K, T, r, is_call):
    """5-iteration Newton-Raphson implied volatility backsolver."""
    if T <= 0 or price_target <= 0:
        return 0.20
    sigma = 0.20
    for _ in range(5):
        d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
        price = bs_price_numba(S, K, T, r, sigma, is_call)
        vega = S * _numba_pdf(d1) * math.sqrt(T)
        if vega < 1e-8:
            break
        diff = price - price_target
        if abs(diff) < 1e-4:
            break
        sigma -= diff / vega
        if sigma <= 0.005:
            sigma = 0.005
            break
    return sigma

@njit(cache=True)
def calculate_greeks_numba(S, K, T, r, sigma, is_call):
    """Numba-accelerated Delta and Vega calculation."""
    if T <= 0 or sigma <= 0:
        return 0.0, 0.0
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    if is_call:
        delta = _numba_cdf(d1)
    else:
        delta = _numba_cdf(d1) - 1.0
    vega = S * _numba_pdf(d1) * math.sqrt(T) / 100.0
    return delta, vega

@njit(cache=True)
def find_tp2_signals_numba(
    strikes, dtes, asks, bids, deltas, 
    carry, min_score, commission_cost, multiplier,
    max_qty=10, max_net_delta=0.10, is_call=True
):
    """
    Numba-accelerated TP2 quadruplet search and Delta-neutral solver.
    Returns: Array of [k1_idx, k2_idx, t1_idx, t2_idx, q11, q22, q12, q21, net_delta, cashflow]
    """
    num_k = len(strikes)
    num_t = len(dtes)
    results = np.zeros((100, 10)) # Max 100 signals per minute for performance
    count = 0
    
    for t1_idx in range(num_t):
        for t2_idx in range(t1_idx + 1, num_t):
            t1, t2 = dtes[t1_idx], dtes[t2_idx]
            df1 = math.exp(-carry * (t1 / 365.0))
            df2 = math.exp(-carry * (t2 / 365.0))
            
            for k1_idx in range(num_k):
                for k2_idx in range(k1_idx + 1, num_k):
                    # Fetch all 8 prices for the 4 legs
                    a11, b11 = asks[k1_idx, t1_idx], bids[k1_idx, t1_idx]
                    a12, b12 = asks[k1_idx, t2_idx], bids[k1_idx, t2_idx]
                    a21, b21 = asks[k2_idx, t1_idx], bids[k2_idx, t1_idx]
                    a22, b22 = asks[k2_idx, t2_idx], bids[k2_idx, t2_idx]
                    
                    if math.isnan(a11) or math.isnan(a22) or math.isnan(a12) or math.isnan(a21): continue
                    if math.isnan(b11) or math.isnan(b22) or math.isnan(b12) or math.isnan(b21): continue
                    
                    # TP2 Multiplicative Violation Check
                    # Expected: V11*V22 >= V12*V21 for both Calls and Puts
                    cost_adj = a11 * a22
                    rev_adj = b12 * b21
                    
                    if cost_adj > 0 and (rev_adj - cost_adj) / cost_adj > min_score:
                        d11, d12, d21, d22 = deltas[k1_idx, t1_idx], deltas[k1_idx, t2_idx], deltas[k2_idx, t1_idx], deltas[k2_idx, t2_idx]
                        
                        best_cashflow = -999.0
                        best_delta = 999.0
                        best_q = (1, 1, 1, 1)
                        
                        for q_buy1 in range(1, max_qty + 1):
                            for q_buy2 in range(1, max_qty + 1):
                                for q_sell1 in range(1, max_qty + 1):
                                    for q_sell2 in range(1, max_qty + 1):
                                        # Buy (11, 22), Sell (12, 21) for both Calls and Puts
                                        net_d = q_buy1*d11 + q_buy2*d22 - q_sell1*d12 - q_sell2*d21
                                        cashflow = q_sell1*b12 + q_sell2*b21 - q_buy1*a11 - q_buy2*a22
                                            
                                        if abs(net_d) <= max_net_delta:
                                            total_legs = q_buy1 + q_buy2 + q_sell1 + q_sell2
                                            comms_pts = (total_legs * 2 * commission_cost) / multiplier
                                            cf_net = cashflow - comms_pts
                                            
                                            if cf_net > 0.1:
                                                metric = cf_net / total_legs
                                                if metric > best_cashflow:
                                                    best_cashflow, best_delta, best_q = metric, net_d, (q_buy1, q_buy2, q_sell1, q_sell2)
                        
                        if best_cashflow > 0.0 and count < 100:
                            results[count, 0] = k1_idx
                            results[count, 1] = k2_idx
                            results[count, 2] = t1_idx
                            results[count, 3] = t2_idx
                            results[count, 4:8] = np.array(best_q)
                            results[count, 8] = best_delta
                            results[count, 9] = best_cashflow # This becomes base_cashflow in points
                            count += 1
    return results[:count]

def run_backtest(data_dirs, underlying='IO', carry=DEFAULT_CARRY, take_profit_points=TAKE_PROFIT_POINTS, min_score=MIN_SCORE, max_spread_pct=0.2):
    """
    Run the backtest over multiple data directories to allow longer holding.
    """
    all_dfs = []
    if isinstance(data_dirs, str):
        data_dirs = [data_dirs]
        
    for d in data_dirs:
        df_day = load_and_align_data(d, underlying)
        if not df_day.empty:
            all_dfs.append(df_day)
            
    if not all_dfs:
        print("No data found.")
        return
        
    df = pd.concat(all_dfs).sort_index()
    # Limit ffill to prevent stale weekend/afternoon data from bleeding into the next morning
    df = df.resample('1min').ffill(limit=10).dropna(how='all')
    
    tickers = set()
    for col in df.columns:
        tickers.add(col.split('_')[0])
        
    calls, puts = [], []
    ticker_info = {}
    
    for t in tickers:
        und, year, month, typ, strike = parse_ticker(t)
        expiry_date = get_third_friday(year, month)
        ticker_info[t] = {'type': typ, 'strike': strike, 'expiry_date': expiry_date}
        if typ == 'C': calls.append(t)
        else: puts.append(t)
        
    print(f"Found {len(calls)} Calls and {len(puts)} Puts. Backtesting {len(all_dfs)} days.")
    
    positions, closed_trades = [], []
    stop_loss_points = take_profit_points * SL_MULTIPLIER
    
    def get_mtm(pos, row):
        mtm = 0.0
        for leg in pos['legs']:
            p = row.get(f"{leg['ticker']}_{'bid' if leg['side']==1 else 'ask'}", np.nan)
            if pd.isna(p) or p <= 0: return np.nan
            mtm += leg['side'] * p * leg['qty']
        return mtm

    for current_time, row in df.iterrows():
        # 0. Skip non-trading hours for both management and entry (CFFEX: 09:30-11:30, 13:00-15:00)
        h, m = current_time.hour, current_time.minute
        if h < 9 or (h == 9 and m < 30) or (h == 11 and m > 30) or h == 12 or (h == 14 and m >= 55) or h >= 15:
            continue

        # 1. Management
        for pos in positions[:]:
            val = get_mtm(pos, row)
            if pd.isna(val): continue
            
            pnl = val + pos['initial_cashflow']
            min_dte_days = min((ticker_info[leg['ticker']]['expiry_date'].date() - current_time.date()).days for leg in pos['legs'])
            
            # Check bounds relative to total leg quantities to avoid quantity skew
            norm_pnl = pnl / pos['total_qty']
            if norm_pnl > take_profit_points or norm_pnl < -stop_loss_points or min_dte_days <= 1:
                # Commissions were already processed into 'initial_cashflow' via cf_net in Numba
                pos.update({'close_time': current_time, 'pnl': pnl, 'net_pnl': pnl * MULTIPLIER})
                closed_trades.append(pos)
                positions.remove(pos)

        fwd_prices = {}
        for dte in set((ticker_info[t]['expiry_date'].date() - current_time.date()).days for t in tickers if (ticker_info[t]['expiry_date'].date() - current_time.date()).days > 0):
            tkrs = [t for t in tickers if (ticker_info[t]['expiry_date'].date() - current_time.date()).days == dte]
            min_diff, atm_k = np.inf, None
            for k in set(ticker_info[t]['strike'] for t in tkrs):
                c = [t for t in tkrs if ticker_info[t]['type']=='C' and ticker_info[t]['strike']==k]
                p = [t for t in tkrs if ticker_info[t]['type']=='P' and ticker_info[t]['strike']==k]
                if c and p:
                    ca, pa = row.get(f"{c[0]}_ask", 0), row.get(f"{p[0]}_ask", 0)
                    if ca > 0 and pa > 0 and abs(ca-pa) < min_diff:
                        min_diff, atm_k = abs(ca-pa), k + ca - pa
            if atm_k: fwd_prices[dte] = atm_k

        # Active Keys to prevent duplicates
        active_keys = {frozenset([leg['ticker'] for leg in p['legs']]) for p in positions}

        for otype, olist in [('C', calls), ('P', puts)]:
            active = []
            for t in olist:
                a, b = row.get(f"{t}_ask", 0), row.get(f"{t}_bid", 0)
                # Ensure minimum viability through absolute spread and bid check
                if a > 0 and b > 0.5 and (a-b)/((a+b)/2) <= max_spread_pct and (a-b) <= MAX_ABS_SPREAD:
                    info = ticker_info[t]
                    dte = (info['expiry_date'].date() - current_time.date()).days
                    if dte in fwd_prices and dte > 1: # Explicitly skip very near DTE entry
                        fwd = fwd_prices[dte]
                        if (otype=='C' and info['strike']>fwd) or (otype=='P' and info['strike']<fwd):
                            mid_price = (a + b) / 2.0
                            sigma_iv = implied_vol_newton(mid_price, fwd, info['strike'], dte/365.0, -carry, otype=='C')
                            d, v = calculate_greeks_numba(fwd, info['strike'], dte/365.0, -carry, sigma_iv, otype=='C')
                            active.append({'t': t, 'k': info['strike'], 'dte': dte, 'a': a, 'b': b, 'd': d})
            
            if len(active) < 4: continue
            act_df = pd.DataFrame(active)
            strikes = np.sort(act_df['k'].unique())
            dtes = np.sort(act_df['dte'].unique())
            k_to_idx = {k: i for i, k in enumerate(strikes)}
            t_to_idx = {t: i for i, t in enumerate(dtes)}
            
            asks_m = np.full((len(strikes), len(dtes)), np.nan)
            bids_m = np.full((len(strikes), len(dtes)), np.nan)
            deltas_m = np.full((len(strikes), len(dtes)), np.nan)
            tick_m = np.empty((len(strikes), len(dtes)), dtype=object)
            
            for _, r in act_df.iterrows():
                ki, ti = k_to_idx[r['k']], t_to_idx[r['dte']]
                asks_m[ki, ti], bids_m[ki, ti], deltas_m[ki, ti], tick_m[ki, ti] = r['a'], r['b'], r['d'], r['t']
            
            signals = find_tp2_signals_numba(
                strikes, dtes, asks_m, bids_m, deltas_m, 
                carry, min_score, COMMISSION, MULTIPLIER,
                max_qty=10, max_net_delta=MAX_NET_DELTA,
                is_call=(otype == 'C')
            )
            
            if len(signals) > 0:
                # Rank: Highest Net Cashflow per Contract first
                signals = signals[signals[:, 9].argsort()[::-1]]
                
                for s in signals:
                    k1i, k2i, t1i, t2i = int(s[0]), int(s[1]), int(s[2]), int(s[3])
                    q_base = s[4:8]
                    base_cf_net = s[9]
                    
                    # For both calls and puts: Buy (11, 22), Sell (12, 21)
                    sig_tickers = [tick_m[k1i,t1i], tick_m[k2i,t2i], tick_m[k1i,t2i], tick_m[k2i,t1i]]
                        
                    sig_key = frozenset(sig_tickers)
                    if sig_key in active_keys: continue
                    
                    # Kelly Scaled Sizing (targeting ~ CAPITAL_PER_SET margin)
                    # For IO, short margin is roughly ~ Strike * 0.15 * 100
                    # Shorts are q_base[2] and q_base[3] (sell1 and sell2)
                    ticker_s1, ticker_s2 = sig_tickers[2], sig_tickers[3]
                    margin_per_base_qty = (ticker_info[ticker_s1]['strike'] * q_base[2] + ticker_info[ticker_s2]['strike'] * q_base[3]) * MULTIPLIER * MARGIN_RATE
                    
                    kelly_scale = min(1.0, max(0.05, (base_cf_net * MULTIPLIER) / (0.005 * CAPITAL_PER_SET)))
                    target_margin = CAPITAL_PER_SET * kelly_scale
                    final_multiplier = max(1, int(target_margin / margin_per_base_qty))
                    
                    q = q_base * final_multiplier
                    total_qty = np.sum(q)
                    # base_cf_net is points per leg, so multiply by total_qty to get total position cashflow
                    actual_cf_points = base_cf_net * total_qty
                    
                    # Construct Legs
                    pos_legs = []
                    # First two are BUYS
                    for i in range(2):
                        tkr = sig_tickers[i]
                        pos_legs.append({'ticker': tkr, 'side': 1, 'qty': q[i], 'entry_price': row[f"{tkr}_ask"]})
                    # Next two are SELLS
                    for i in range(2, 4):
                        tkr = sig_tickers[i]
                        pos_legs.append({'ticker': tkr, 'side': -1, 'qty': q[i], 'entry_price': row[f"{tkr}_bid"]})
                    
                    positions.append({
                        'open_time': current_time, 'type': otype, 'initial_cashflow': actual_cf_points, # Points
                        'total_qty': total_qty, 
                        'commission': total_qty * 2 * COMMISSION, 
                        'pnl': 0.0, 'net_pnl': 0.0,
                        'sig_key': sig_key,
                        'legs': pos_legs
                    })
                    active_keys.add(sig_key)
                    break 

            
    # Reporting
    print("\n" + "="*80)
    print("BACKTEST RESULTS")
    print("="*80)
    if not closed_trades:
        print("No trades executed.")
        return
        
    res_df = pd.DataFrame(closed_trades)
    wins = len(res_df[res_df['net_pnl'] > 0])
    total = len(res_df)
    win_rate = wins / total
    total_net_pnl = res_df['net_pnl'].sum()
    total_gross = (res_df['pnl'] * MULTIPLIER).sum()
    total_comm = res_df['commission'].sum()
    
    res_df['hold_minutes'] = (res_df['close_time'] - res_df['open_time']).dt.total_seconds() / 60
    daily_pnl = res_df.groupby(res_df['close_time'].dt.date)['net_pnl'].sum()
    
    sharpe = 0.0
    if len(daily_pnl) > 1 and daily_pnl.std() != 0:
        sharpe = daily_pnl.mean() / daily_pnl.std() * np.sqrt(252)
        
    max_dd = (daily_pnl.cumsum() - daily_pnl.cumsum().cummax()).min() if len(daily_pnl) > 0 else 0.0
    
    print(f"Total Trades: {total}")
    print(f"Win Rate:     {win_rate:.2%}")
    print(f"Gross PnL:    {total_gross:.2f} RMB")
    print(f"Total Comm:   {total_comm:.2f} RMB")
    print(f"Net PnL:      {total_net_pnl:.2f} RMB")
    print(f"Sharpe Ratio: {sharpe:.2f}")
    print(f"Max Drawdown: {max_dd:.2f} RMB")
    print(f"Avg Hold:     {res_df['hold_minutes'].mean():.1f} min")
    print("="*80)
    
    res_df.to_csv('tp2_backtest_results.csv', index=False)
    print("Detailed trade log saved to tp2_backtest_results.csv")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="TP2 Backtest")
    parser.add_argument('data_dirs', type=str, nargs='+', help='Directories containing the tick data (e.g. data-deep/2026-03-24 data-deep/2026-03-25)')
    parser.add_argument('--take-profit', type=float, default=2.0, help='Take profit in points (default: 2.0)')
    parser.add_argument('--min-score', type=float, default=0.005, help='Minimum TP2 violation rate (default: 0.005)')
    parser.add_argument('--max-spread', type=float, default=0.2, help='Maximum relative spread pct (default: 0.2)')
    args = parser.parse_args()
    
    run_backtest(args.data_dirs, take_profit_points=args.take_profit, min_score=args.min_score, max_spread_pct=args.max_spread)
