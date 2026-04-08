import os
import glob
import re
import argparse
import math
import pandas as pd
import numpy as np
from datetime import datetime

def parse_ticker(ticker):
    match = re.match(r'([A-Z]+)(\d{2})(\d{2})([CP])(\d+)', ticker)
    if match:
        und, yy, mm, typ, strike = match.groups()
        return und, 2000 + int(yy), int(mm), typ, float(strike)
    return None, None, None, None, None

def load_and_align_data(data_dir, symbol='IO'):
    print(f"Loading data for {symbol} from {data_dir}...")
    path = os.path.join(data_dir, symbol, '*.parquet')
    parquet_files = glob.glob(path)
    if not parquet_files:
        return pd.DataFrame()
    
    all_series = []
    for f in parquet_files:
        ticker = os.path.basename(f).replace('.parquet', '')
        und, *_ = parse_ticker(ticker)
        if not und: continue
        try:
            df = pd.read_parquet(f)
            if 'datetime' in df.index.names: df = df.reset_index()
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.set_index('datetime').sort_index()
            # Use 'a1' and 'b1' from parquet
            df = df[['a1', 'b1']].rename(columns={'a1': f'{ticker}_ask', 'b1': f'{ticker}_bid'})
            df = df[~df.index.duplicated(keep='last')]
            all_series.append(df)
        except: continue

    if not all_series: return pd.DataFrame()
    merged_df = pd.concat(all_series, axis=1)
    # Using your preferred limit=2 for freshness
    resampled_df = merged_df.resample('1min').ffill(limit=2).dropna(how='all')
    return resampled_df

def scan_butterfly(df, min_profit=0.1):
    tickers = set(col.split('_')[0] for col in df.columns)
    ticker_info = {}
    for t in tickers:
        und, yy, mm, typ, strike = parse_ticker(t)
        expiry = f"{yy}{mm:02d}"
        ticker_info[t] = {'type': typ, 'strike': strike, 'expiry': expiry}

    violations = []
    print(f"Scanning {len(df)} 1-minute snapshots...")

    for current_time, row in df.iterrows():
        # Session filter
        h, m = current_time.hour, current_time.minute
        if h < 9 or (h == 9 and m < 30) or (h == 11 and m > 30) or h == 12 or (h == 14 and m >= 55) or h >= 15:
            continue

        # Group components by Expiry and Type
        expiry_groups = {}
        for t, info in ticker_info.items():
            ask = row.get(f"{t}_ask")
            bid = row.get(f"{t}_bid")
            if pd.isna(ask) or pd.isna(bid) or ask <= 0 or bid <= 0: continue
            
            key = (info['expiry'], info['type'])
            if key not in expiry_groups: expiry_groups[key] = []
            expiry_groups[key].append({'t': t, 'k': info['strike'], 'a': ask, 'b': bid})

        for (expiry, otype), options in expiry_groups.items():
            if len(options) < 3: continue
            # Sort by strike
            opts = sorted(options, key=lambda x: x['k'])
            n = len(opts)
            
            for i in range(n):
                for j in range(i + 1, n):
                    for k in range(j + 1, n):
                        o1, o2, o3 = opts[i], opts[j], opts[k]
                        k1, k2, k3 = o1['k'], o2['k'], o3['k']
                        
                        # Convexity weight: k2 = w*k1 + (1-w)*k3
                        w = (k3 - k2) / (k3 - k1)
                        
                        # Butterfly Arb (Worst Case Logic):
                        # 1. Sell K2 (at min of bid/ask)
                        # 2. Buy w*K1 (at max of bid/ask)
                        # 3. Buy (1-w)*K3 (at max of bid/ask)
                        
                        sell_k2 = min(o2['b'], o2['a'])
                        buy_k1 = max(o1['b'], o1['a'])
                        buy_k3 = max(o3['b'], o3['a'])
                        
                        # Upfront credit (min profit)
                        min_p = sell_k2 - (w * buy_k1 + (1 - w) * buy_k3)
                        
                        if min_p > min_profit:
                            # Peak intrinsic value at K2
                            h_val = w * (k2 - k1)
                            max_p = min_p + h_val
                            
                            violations.append({
                                'time': current_time,
                                'expiry': expiry,
                                'type': otype,
                                'k1': k1, 'k2': k2, 'k3': k3,
                                'min_profit': round(min_p, 4),
                                'max_profit': round(max_p, 4),
                                'leg1': o1['t'], 'leg2': o2['t'], 'leg3': o3['t']
                            })

    return pd.DataFrame(violations)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date-dir', type=str, required=True, help='e.g. data-deep/2026-03-24')
    parser.add_argument('--symbol', type=str, default='IO')
    parser.add_argument('--min-profit', type=float, default=0.1)
    args = parser.parse_args()

    df = load_and_align_data(args.date_dir, args.symbol)
    if df.empty: return
    
    viols = scan_butterfly(df, args.min_profit)
    if not viols.empty:
        print("\n" + "="*80)
        print(f"FOUND {len(viols)} BUTTERFLY ARBITRAGE OPPORTUNITIES")
        print("="*80)
        
        # Sort by min_profit and print
        viols = viols.sort_values('min_profit', ascending=False)
        pd.set_option('display.max_rows', 100)
        pd.set_option('display.width', 1000)
        print(viols.to_string(index=False))
        
        date_str = os.path.basename(os.path.normpath(args.date_dir))
        out_name = f"butterfly_violations_{args.symbol}_{date_str}.csv"
        viols.to_csv(out_name, index=False)
        print(f"\nResult also saved to {out_name}.")
    else:
        print("\nNo butterfly arbitrage found.")

if __name__ == "__main__":
    main()
