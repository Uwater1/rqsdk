import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy.stats import norm
from scipy.optimize import brentq

# --- Configuration ---
UNDERLYINGS = ['510050.XSHG', '510300.XSHG', '510500.XSHG']
SYMBOL_MAP = {
    '510050.XSHG': '50ETF',
    '510300.XSHG': '300ETF',
    '510500.XSHG': '500ETF',
}
DATA_DIR = 'data'
RFR_FILE = os.path.join(DATA_DIR, 'interest_free_rate.csv')

# --- Black-Scholes Engine ---
class BlackScholesEngine:
    @staticmethod
    def price(F, K, T, sigma, r, option_type='C'):
        if T <= 0:
            return max(0.0, F - K if option_type == 'C' else K - F) * np.exp(-r * T)
        if sigma <= 0:
            return max(0.0, F - K if option_type == 'C' else K - F) * np.exp(-r * T)
        
        d1 = (np.log(F / K) + 0.5 * sigma**2 * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        if option_type == 'C':
            price = np.exp(-r * T) * (F * norm.cdf(d1) - K * norm.cdf(d2))
        else:
            price = np.exp(-r * T) * (K * norm.cdf(-d2) - F * norm.cdf(-d1))
        return price

    @staticmethod
    def implied_vol(market_price, F, K, T, r, option_type='C'):
        if T <= 0: return 0.0
        
        intrinsic = max(0.0, (F - K if option_type == 'C' else K - F) * np.exp(-r * T))
        if market_price <= intrinsic + 1e-7:
            return 0.0001
            
        def func(s):
            return BlackScholesEngine.price(F, K, T, s, r, option_type) - market_price
        
        try:
            return brentq(func, 1e-6, 5.0, xtol=1e-6)
        except:
            return 0.0

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
            
            for k in strikes:
                try:
                    c1 = shared_mats.loc[(k, 'C'), t1_dt]
                    p1 = shared_mats.loc[(k, 'P'), t1_dt]
                    c2 = shared_mats.loc[(k, 'C'), t2_dt]
                    p2 = shared_mats.loc[(k, 'P'), t2_dt]
                except KeyError:
                    continue # Need both C and P
                
                # F = K + (C - P) * e^rT
                F1 = k + (c1 - p1) * np.exp(r * T1)
                F2 = k + (c2 - p2) * np.exp(r * T2)
                
                # Sanity check for F (must be within 20% of spot theoretically for ETFs)
                if F1 <= 1e-3 or F2 <= 1e-3 or abs(F1/s0 - 1) > 0.2 or abs(F2/s0 - 1) > 0.2:
                    continue
                
                # q = r - ln(F/S0)/T. If T is too small, use q2 to avoid noise
                q2 = r - np.log(F2 / s0) / T2
                q1 = (r - np.log(F1 / s0) / T1) if T1 > (2/365.0) else q2
                
                # Clip yield to reasonable range [-100%, 100%]
                q1 = np.clip(q1, -1.0, 1.0)
                q2 = np.clip(q2, -1.0, 1.0)
                
                # Interpolate r, q, F_star
                q_star = ((T2 - t_star) / (T2 - T1)) * q1 + ((t_star - T1) / (T2 - T1)) * q2
                F_star = s0 * np.exp((r - q_star) * t_star)
                
                for opt_type in ['C', 'P']:
                    mkt1 = c1 if opt_type == 'C' else p1
                    mkt2 = c2 if opt_type == 'C' else p2
                    
                    iv1 = BlackScholesEngine.implied_vol(mkt1, F1, k, T1, r, opt_type)
                    iv2 = BlackScholesEngine.implied_vol(mkt2, F2, k, T2, r, opt_type)
                    
                    if iv1 <= 0 or iv2 <= 0: continue
                    
                    # Interpolate in Total Variance
                    w_star = ((T2 - t_star) / (T2 - T1)) * (iv1**2 * T1) + ((t_star - T1) / (T2 - T1)) * (iv2**2 * T2)
                    iv_star = np.sqrt(w_star / t_star)
                    
                    price_star = BlackScholesEngine.price(F_star, k, t_star, iv_star, r, opt_type)
                    
                    results.append([
                        dt_pd.strftime('%Y-%m-%d'),
                        t_star_dt.strftime('%Y-%m-%d'),
                        tgt['tag'],
                        round(t_star * 365, 2),
                        k,
                        opt_type,
                        round(price_star, 4),
                        round(iv_star, 4),
                        round(F_star, 4)
                    ])
        
        if (i+1) % 100 == 0:
            print(f"  Progress: {i+1}/{total_dates} ({(i+1)/total_dates*100:.1f}%) | Current Date: {dt_pd.date()} | Results: {len(results)}")

    output_file = f"synthetic_options_{prefix}.csv"
    columns = ['Date', 'Target Expiry', 'Weekday Tag', 'DaysToExpiry', 'Strike', 'Option Type', 'Price', 'IV', 'Forward']
    pd.DataFrame(results, columns=columns).to_csv(output_file, index=False)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Finished {prefix}. Saved to {output_file}")

if __name__ == "__main__":
    for und in UNDERLYINGS:
        process_underlying(und)
