import os
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
        for i in range(28, 36): # Only checks dates in [28, 35] days away
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
    full_data = prices_df.merge(inst_df[['order_book_id', 'maturity_date', 'option_type']], on='order_book_id')
    full_data['maturity_date'] = pd.to_datetime(full_data['maturity_date'])

    # Deduplicate: adjusted-strike contracts can share (date, strike, type, maturity)
    # with different order_book_ids. Keep the highest-volume contract to avoid pivot crash.
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
        # Index: (strike, type), Column: maturity
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
            
            # Use only strikes available at BOTH bracketed maturities
            shared_mats = price_pivot[[t1_dt, t2_dt]].dropna()
            if shared_mats.empty or s0 <= 0: continue
            
            # Group by strike to ensure we have both Call and Put for Forward calculation
            strikes = shared_mats.index.get_level_values('strike_price').unique()
            
            # Group by strike to ensure we have both Call and Put for Forward calculation
            shared_strikes = sorted(shared_mats.index.get_level_values('strike_price').unique())
            
            # Prepare arrays for Numba
            num_s = len(shared_strikes)
            c1_arr = np.zeros(num_s)
            p1_arr = np.zeros(num_s)
            c2_arr = np.zeros(num_s)
            p2_arr = np.zeros(num_s)
            valid_mask = np.ones(num_s, dtype=np.bool_)
            
            for idx, k in enumerate(shared_strikes):
                try:
                    c1_arr[idx] = shared_mats.loc[(k, 'C'), t1_dt]
                    p1_arr[idx] = shared_mats.loc[(k, 'P'), t1_dt]
                    c2_arr[idx] = shared_mats.loc[(k, 'C'), t2_dt]
                    p2_arr[idx] = shared_mats.loc[(k, 'P'), t2_dt]
                except KeyError:
                    valid_mask[idx] = False
            
            # Filter to valid strikes only
            strikes_vec = np.array(shared_strikes)[valid_mask]
            c1_vec = c1_arr[valid_mask]
            p1_vec = p1_arr[valid_mask]
            c2_vec = c2_arr[valid_mask]
            p2_vec = p2_arr[valid_mask]
            
            if len(strikes_vec) == 0: continue
            
            # Execute Numba core loop
            # Returns a matrix [num_strikes, 5] --> [Price_C, Price_P, IV_C, IV_P, F_star]
            batch_results = process_synthetic_strikes_loop(
                strikes_vec, c1_vec, p1_vec, c2_vec, p2_vec,
                s0, r, T1, T2, t_star
            )
            
            # The current process_synthetic_strikes_loop calculates F1, F2 per strike 
            # as it did in the original loop.
            
            for idx in range(len(strikes_vec)):
                k = strikes_vec[idx]
                price_c, price_p, iv_c, iv_p, F_star = batch_results[idx]
                
                # Append Call result
                if price_c > 0 and iv_c > 1e-4:
                    results.append([
                        dt_pd.strftime('%Y-%m-%d'), t_star_dt.strftime('%Y-%m-%d'), tgt['tag'],
                        round(t_star * 365, 2), k, 'C', round(price_c, 4), round(iv_c, 4), round(F_star, 4)
                    ])
                
                # Append Put result
                if price_p > 0 and iv_p > 1e-4:
                    results.append([
                        dt_pd.strftime('%Y-%m-%d'), t_star_dt.strftime('%Y-%m-%d'), tgt['tag'],
                        round(t_star * 365, 2), k, 'P', round(price_p, 4), round(iv_p, 4), round(F_star, 4)
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
