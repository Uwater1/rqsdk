import os
import math
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from numba_utils import process_synthetic_strikes_loop, black_price, black_iv

# --- Configuration ---
UNDERLYINGS = ['510050.XSHG', '510300.XSHG', '510500.XSHG']
SYMBOL_MAP = {
    '510050.XSHG': '50ETF',
    '510300.XSHG': '300ETF',
    '510500.XSHG': '500ETF',
}
DATA_DIR = 'data'
RFR_FILE = os.path.join(DATA_DIR, 'interest_free_rate.csv')

# Black-Scholes functions are now imported from numba_utils

# --- Calendar Logic ---
class TargetExpiryGenerator:
    WEEKDAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    
    @staticmethod
    def get_tag(date):
        wd = date.weekday()
        if wd > 4: return None
        n = (date.day - 1) // 7 + 1
        return f"{n}{'st' if n==1 else 'nd' if n==2 else 'rd' if n==3 else 'th'} {TargetExpiryGenerator.WEEKDAY_NAMES[wd]}"

    @staticmethod
    def get_target_expiries(current_date):
        targets = []
        # Widen range to [25, 42] days to handle month variance and holidays (Bug 5)
        for i in range(25, 43): 
            future_date = current_date + timedelta(days=i)
            tag = TargetExpiryGenerator.get_tag(future_date)
            if tag:
                targets.append({
                    'expiry_date': future_date,
                    'tag': tag,
                    'T_star': i / 365.0,
                    'days': i
                })
        return targets

# --- Core Processor ---
def process_underlying(underlying_symbol):
    prefix = SYMBOL_MAP[underlying_symbol]
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Processing {prefix} ({underlying_symbol})...")
    
    # Load and clean Data
    inst_df = pd.read_parquet(os.path.join(DATA_DIR, f"{prefix}_instruments.parquet"))
    prices_df = pd.read_parquet(os.path.join(DATA_DIR, f"{prefix}_historical_prices.parquet"))
    spot_df = pd.read_parquet(os.path.join(DATA_DIR, f"{prefix}_1d.parquet"))
    rfr_df = pd.read_csv(RFR_FILE, parse_dates=['trading_date'])
    
    rfr_map = rfr_df.set_index('trading_date')['1Y'].to_dict()
    prices_df['date'] = pd.to_datetime(prices_df['date'])
    spot_map = spot_df.set_index(pd.to_datetime(spot_df['date']))['close'].to_dict()
    
    # Add maturity info
    # Ensure strike_price is pulled from inst_df as source of truth (Bug 1)
    if 'strike_price' in prices_df.columns:
        prices_df = prices_df.drop(columns=['strike_price'])
    full_data = prices_df.merge(inst_df[['order_book_id', 'maturity_date', 'option_type', 'strike_price']], on='order_book_id')
    full_data['maturity_date'] = pd.to_datetime(full_data['maturity_date'])

    # Deduplicate: kept from previous bugfix
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
            
            # Find bracketing: T1 < T* < T2
            t1_dt = None
            t2_dt = None
            for lm in listed_mats:
                if lm < t_star_dt: t1_dt = lm
                elif lm > t_star_dt:
                    t2_dt = lm
                    break
            
            if t1_dt is None or t2_dt is None: continue
            
            T1 = max((t1_dt - dt_pd).days / 365.0, 1e-6)
            T2 = (t2_dt - dt_pd).days / 365.0
            
            # --- Robust Forward Price Calculation (Bug 2) ---
            def get_robust_forward(mat_dt, T, spot):
                # Filter to near-ATM strikes (±10%)
                mask = (price_pivot.index.get_level_values('strike_price') >= spot * 0.9) & \
                       (price_pivot.index.get_level_values('strike_price') <= spot * 1.1)
                atm_data = price_pivot.loc[mask, mat_dt].unstack()
                if 'C' not in atm_data or 'P' not in atm_data: 
                    return spot * math.exp(r * T) # dummy fallback
                
                atm_pairs = atm_data.dropna(subset=['C', 'P'])
                if atm_pairs.empty: 
                    return spot * math.exp(r * T)
                
                k_vec = atm_pairs.index.values
                c_vec = atm_pairs['C'].values
                p_vec = atm_pairs['P'].values
                # F = K + (C - P) * e^(rT)
                f_vec = k_vec + (c_vec - p_vec) * math.exp(r * T)
                return np.median(f_vec) # Use median for robustness against outliers

            F1 = get_robust_forward(t1_dt, T1, s0)
            F2 = get_robust_forward(t2_dt, T2, s0)

            # --- PRE-FILTERING (Bug 6) ---
            # We need strikes with C and P available at BOTH maturities
            avail_c1 = price_pivot.xs('C', level='option_type')[t1_dt].dropna().index
            avail_p1 = price_pivot.xs('P', level='option_type')[t1_dt].dropna().index
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
            # Returns a matrix [num_strikes, 5] --> [Price_C, Price_P, IV_star, F_star, _]
            batch_results = process_synthetic_strikes_loop(
                strikes_vec, c1_vec, p1_vec, c2_vec, p2_vec,
                s0, r, T1, T2, t_star, F1, F2
            )
            
            for idx in range(len(strikes_vec)):
                k = strikes_vec[idx]
                price_c, price_p, iv_star, F_star, _ = batch_results[idx]
                
                if iv_star > 1e-4 and F_star > 1e-3:
                    # Save both to maintain parity
                    results.append([
                        dt_pd.strftime('%Y-%m-%d'), t_star_dt.strftime('%Y-%m-%d'), tgt['tag'],
                        round(t_star * 365, 2), k, 'C', round(price_c, 4), round(iv_star, 4), round(F_star, 4)
                    ])
                    results.append([
                        dt_pd.strftime('%Y-%m-%d'), t_star_dt.strftime('%Y-%m-%d'), tgt['tag'],
                        round(t_star * 365, 2), k, 'P', round(price_p, 4), round(iv_star, 4), round(F_star, 4)
                    ])
        
        if (i+1) % 100 == 0:
            print(f"  Progress: {i+1}/{total_dates} ({(i+1)/total_dates*100:.1f}%) | Current Date: {dt_pd.date()} | Results: {len(results)}")

    output_file = f"synthetic_options_{prefix}.parquet"
    columns = ['Date', 'Target Expiry', 'Weekday Tag', 'DaysToExpiry', 'Strike', 'Option Type', 'Price', 'IV', 'Forward']
    df_results = pd.DataFrame(results, columns=columns)
    df_results['Date'] = pd.to_datetime(df_results['Date'])
    df_results['Target Expiry'] = pd.to_datetime(df_results['Target Expiry'])
    df_results.to_parquet(output_file, index=False)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Finished {prefix}. Saved to {output_file}")

if __name__ == "__main__":
    for und in UNDERLYINGS:
        process_underlying(und)
