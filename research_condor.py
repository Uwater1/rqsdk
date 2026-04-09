import os
import glob
import re
import argparse
import pandas as pd
import numpy as np
import calendar
from datetime import datetime, timedelta

def get_third_friday(year, month):
    """Returns the 3rd Friday of a given month/year."""
    c = calendar.monthcalendar(year, month)
    fridays = [week[calendar.FRIDAY] for week in c if week[calendar.FRIDAY] != 0]
    # Handle edge case where first week has no Friday
    if len(fridays) < 3:
        return datetime(year, month, 20) # Fallback
    day = fridays[2]
    return datetime(year, month, day)

def parse_ticker(ticker):
    """
    Parses a ticker string into its components.
    Example: IO2604C4000
    """
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
        print(f"No parquet files found in {path}")
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
            # Use 'a1' and 'b1' for ask and bid
            if 'a1' not in df.columns or 'b1' not in df.columns:
                df['a1'] = df['close']
                df['b1'] = df['close']
            
            # Select relevant columns and rename
            cols = ['a1', 'b1']
            if 'open_interest' in df.columns: cols.append('open_interest')
            
            sub_df = df[cols].rename(columns={
                'a1': f'{ticker}_ask', 
                'b1': f'{ticker}_bid',
                'open_interest': f'{ticker}_oi'
            })
            sub_df = sub_df[~sub_df.index.duplicated(keep='last')]
            all_series.append(sub_df)
        except Exception as e:
            print(f"Error loading {f}: {e}")
            continue

    if not all_series: return pd.DataFrame()
    merged_df = pd.concat(all_series, axis=1)
    # Using limit=2 for freshness
    resampled_df = merged_df.resample('1min').ffill(limit=2).dropna(how='all')
    return resampled_df

def scan_iron_condor(df, opt):
    """
    df: aligned dataframe
    opt: options from argparse (min_profit, max_spread, otm_only, spot, min_oi, min_ann_return)
    """
    tickers = set(col.split('_')[0] for col in df.columns)
    ticker_info = {}
    for t in tickers:
        und, yy, mm, typ, strike = parse_ticker(t)
        if und:
            expiry_str = f"{yy}{mm:02d}"
            try:
                expiry_date = get_third_friday(yy, mm)
            except:
                expiry_date = datetime(yy, mm, 20)
            ticker_info[t] = {'type': typ, 'strike': strike, 'expiry': expiry_str, 'expiry_date': expiry_date}

    violations = []
    print(f"Scanning {len(df)} snapshots...")

    for current_time, row in df.iterrows():
        # Session filter
        h, m = current_time.hour, current_time.minute
        if h < 9 or (h == 9 and m < 30) or (h == 11 and m > 30) or h == 12 or (h == 14 and m >= 55) or h >= 15:
            continue

        # Group components by Expiry
        expiry_groups = {}
        for t, info in ticker_info.items():
            ask = row.get(f"{t}_ask")
            bid = row.get(f"{t}_bid")
            oi = row.get(f"{t}_oi", 0)
            
            if pd.isna(ask) or pd.isna(bid) or ask <= 0 or bid <= 0: continue
            
            # Liquidity Filters: Spread % and Min OI
            mid = (ask + bid) / 2.0
            spread_pct = (ask - bid) / mid
            if spread_pct > opt.max_spread: continue
            if oi < opt.min_oi: continue
            
            exp = info['expiry']
            if exp not in expiry_groups: 
                expiry_groups[exp] = {'P': [], 'C': []}
            expiry_groups[exp][info['type']].append({
                't': t, 'k': info['strike'], 'a': ask, 'b': bid, 'spread': round(spread_pct, 4)
            })

        for exp, types in expiry_groups.items():
            puts = sorted(types['P'], key=lambda x: x['k'])
            calls = sorted(types['C'], key=lambda x: x['k'])
            
            if len(puts) < 2 or len(calls) < 2: continue
            
            # OTM Filtering
            if opt.otm_only and opt.spot > 0:
                puts = [p for p in puts if p['k'] < opt.spot]
                calls = [c for c in calls if c['k'] > opt.spot]
                if len(puts) < 2 or len(calls) < 2: continue

            # Find Put Spreads (K1 < K2)
            put_spreads = []
            for i in range(len(puts)):
                for j in range(i + 1, len(puts)):
                    p1, p2 = puts[i], puts[j] # k1 < k2
                    p2_sell = min(p2['b'], p2['a'])
                    p1_buy = max(p1['b'], p1['a'])
                    put_credit = p2_sell - p1_buy
                    put_spreads.append({
                        'k1': p1['k'], 'k2': p2['k'], 
                        'p1_t': p1['t'], 'p2_t': p2['t'],
                        'credit': put_credit, 'width': p2['k'] - p1['k']
                    })
            
            # Find Call Spreads (K3 < K4)
            call_spreads = []
            for i in range(len(calls)):
                for j in range(i + 1, len(calls)):
                    c3, c4 = calls[i], calls[j] # k3 < k4
                    c3_sell = min(c3['b'], c3['a'])
                    c4_buy = max(c4['b'], c4['a'])
                    call_credit = c3_sell - c4_buy
                    call_spreads.append({
                        'k3': c3['k'], 'k4': c4['k'], 
                        'c3_t': c3['t'], 'c4_t': c4['t'],
                        'credit': call_credit, 'width': c4['k'] - c3['k']
                    })
            
            # Combine into Iron Condors
            for ps in put_spreads:
                for cs in call_spreads:
                    if ps['k2'] >= cs['k3']: continue 
                    
                    # Total Credit (Worst Case): Sell bid/ask min, Buy bid/ask max
                    total_credit = ps['credit'] + cs['credit']
                    
                    # Deduct Commissions (4 legs * per-trade commission)
                    commissions = 4 * opt.commission
                    net_credit = total_credit - commissions
                    
                    max_width = max(ps['width'], cs['width'])
                    min_width = min(ps['width'], cs['width'])
                    
                    # DTM and Annual Return
                    exp_date = ticker_info[ps['p1_t']]['expiry_date']
                    dtm = (exp_date - current_time).days
                    if dtm < 0: continue
                    
                    risk = max_width - net_credit
                    if risk <= 0:
                        ann_return = 9.99 
                    elif dtm > 0:
                        ann_return = (net_credit / risk) * (365.0 / dtm)
                    else:
                        ann_return = 0
                    
                    # Core Arbitrage + Return Filter (Using Net Credit)
                    if net_credit > min_width + opt.min_profit and ann_return >= opt.min_ann_return:
                        violations.append({
                            'time': current_time,
                            'expiry': exp,
                            'dtm': dtm,
                            'k1': ps['k1'], 'k2': ps['k2'], 'k3': cs['k3'], 'k4': cs['k4'],
                            'credit': round(net_credit, 4),
                            'min_width': round(min_width, 4),
                            'risk': round(risk, 4),
                            'ann_return': round(ann_return, 4),
                            'p1': ps['p1_t'], 'p2': ps['p2_t'], 'c3': cs['c3_t'], 'c4': cs['c4_t']
                        })

    return pd.DataFrame(violations)

def main():
    parser = argparse.ArgumentParser(description="Advanced Iron Condor Research Scan")
    parser.add_argument('--date-dir', type=str, required=True, help='e.g. data-deep/2026-03-24')
    parser.add_argument('--symbol', type=str, default='IO')
    parser.add_argument('--min-profit', type=float, default=0.1)
    parser.add_argument('--spot', type=float, default=0, help='Underlying spot for OTM filter')
    parser.add_argument('--max-spread', type=float, default=0.1, help='Max relative spread (0.1 = 10%)')
    parser.add_argument('--otm-only', action='store_true', help='Only consider OTM legs')
    parser.add_argument('--min-oi', type=float, default=0, help='Minimum open interest')
    parser.add_argument('--min-ann-return', type=float, default=0.01, help='Minimum annual return (0.01 = 1%)')
    parser.add_argument('--commission', type=float, default=0.1, help='Commission per trade/leg')
    args = parser.parse_args()

    df = load_and_align_data(args.date_dir, args.symbol)
    if df.empty: return
    
    viols = scan_iron_condor(df, args)
    if not viols.empty:
        print("\n" + "="*95)
        print(f"FOUND {len(viols)} FILTERED IRON CONDOR OPPORTUNITIES")
        print("="*95)
        
        viols = viols.sort_values('ann_return', ascending=False)
        pd.set_option('display.max_rows', 100)
        pd.set_option('display.width', 1000)
        print(viols.head(100).to_string(index=False))
        
        if len(viols) > 100:
            print(f"\n... and {len(viols) - 100} more opportunities.")
        
        date_str = os.path.basename(os.path.normpath(args.date_dir))
        out_name = f"condor_filtered_{args.symbol}_{date_str}.csv"
        viols.to_csv(out_name, index=False)
        print(f"\nResults saved to {out_name}.")
    else:
        print("\nNo filtered Iron Condor opportunities found.")

if __name__ == "__main__":
    main()
