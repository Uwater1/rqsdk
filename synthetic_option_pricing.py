import os
import math
import re
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from numba_utils import process_synthetic_strikes_loop, black_price, black_iv

# Initialize rqdatac for trading calendar - removed as it's no longer needed for real cycle extraction

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
def get_real_cycles(opt, etf):
    trading_days_set = set(etf.index.normalize())
    opt_trading_days = sorted(opt["date"].unique())

    expiries_cp = (
        opt.groupby(["maturity_date", "option_type"])["order_book_id"]
        .nunique()
        .unstack("option_type")
        .dropna()
        .index.tolist()
    )
    expiries_cp = sorted(expiries_cp)

    cycles = []

    for i, expiry in enumerate(expiries_cp):
        if i == 0:
            entry = opt_trading_days[0]
        else:
            prev_expiry = expiries_cp[i - 1]
            candidates = [d for d in opt_trading_days if d > prev_expiry]
            if not candidates:
                continue
            entry = candidates[0]

        if entry >= expiry:
            continue
            
        entry_norm = pd.Timestamp(entry).normalize()
        if entry_norm not in trading_days_set:
            continue
            
        days = (expiry - entry).days

        cycles.append({
            "entry_date": entry,
            "expiry_date": expiry,
            "T_star": days / 365.0,
            "days": days,
            "tag": "Real Option Cycle"
        })

    return cycles

# --- Core Processor ---
def process_underlying(underlying_symbol):
    prefix = SYMBOL_MAP[underlying_symbol]
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Processing {prefix} ({underlying_symbol})...")
    
    # Load and clean Data
    inst_df = pd.read_parquet(os.path.join(DATA_DIR, f"{prefix}_instruments.parquet"))
    prices_df = pd.read_parquet(os.path.join(DATA_DIR, f"{prefix}_historical_prices.parquet"))

    # Handle spot_df depending on the underlying prefix
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
    
    # Find exact matching cycles from real options
    cycles = get_real_cycles(full_data, spot_df)

    results = []
    total_cycles = len(cycles)
    
    for i, tgt in enumerate(cycles):
        dt_pd = pd.Timestamp(tgt['entry_date'])
        t_star_dt = pd.Timestamp(tgt['expiry_date'])
        t_star = tgt['T_star']

        s0 = spot_map.get(dt_pd)
        r = rfr_map.get(dt_pd)
        if s0 is None or r is None: continue
        
        # Get data for this day
        day_data = full_data[full_data['date'] == dt_pd]
        listed_mats = sorted(day_data['maturity_date'].unique())
        
        # Pre-pivot prices for fast lookup
        price_pivot = day_data.pivot(index=['strike_price', 'option_type'], columns='maturity_date', values='close')
        
        # If T* is EXACTLY a listed maturity, we can just use it.
        # But `process_synthetic_strikes_loop` assumes interpolation `T1 < T_star < T2`.
        # To avoid division by zero in interpolation, if it matches exactly, we pick t1_dt as the exact match,
        # and t2_dt as the next available maturity, and set t_star = t1_dt (so w1 = 1, w2 = 0).
        # We also need to add a tiny epsilon to T2 so T2 - T1 > 0 just in case.
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

        # Get the latest spot price on or before expiry
        etf_expiry_dates = spot_df.index[spot_df.index <= t_star_dt]
        if etf_expiry_dates.empty:
            st = None
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
        
        if (i+1) % 10 == 0:
            print(f"  Progress: {i+1}/{total_cycles} ({(i+1)/total_cycles*100:.1f}%) | Entry Date: {dt_pd.date()} | Results: {len(results)}")

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
    for und in UNDERLYINGS:
        process_underlying(und)
