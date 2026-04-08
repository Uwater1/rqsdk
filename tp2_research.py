import os
import glob
import re
import argparse
import math
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta

def get_third_friday(year, month):
    first_day = datetime(year, month, 1)
    first_friday = first_day + relativedelta(days=(4 - first_day.weekday()) % 7)
    return first_friday + relativedelta(days=14)

def parse_ticker(ticker):
    match = re.match(r'([A-Z]+)(\d{2})(\d{2})([CP])(\d+)', ticker)
    if match:
        und, yy, mm, typ, strike = match.groups()
        year = 2000 + int(yy)
        month = int(mm)
        return und, year, month, typ, float(strike)
    return None, None, None, None, None

def load_and_align_data(data_dir, underlying='IO'):
    print(f"Loading data from {data_dir} for {underlying}...")
    path = os.path.join(data_dir, underlying, '*.parquet')
    parquet_files = glob.glob(path)
    
    if not parquet_files:
        print(f"No parquet files found in {path}")
        return pd.DataFrame()
    
    all_series = []
    
    for f in parquet_files:
        ticker = os.path.basename(f).replace('.parquet', '')
        und, year, month, typ, strike = parse_ticker(ticker)
        if not und: continue
        
        try:
            df = pd.read_parquet(f)
            if 'datetime' in df.index.names:
                df = df.reset_index()
            elif 'datetime' not in df.columns:
                continue
                
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.set_index('datetime').sort_index()
            
            df = df[['a1', 'b1']].rename(columns={'a1': f'{ticker}_ask', 'b1': f'{ticker}_bid'})
            df = df[~df.index.duplicated(keep='last')]
            
            all_series.append(df)
        except Exception as e:
            print(f"Error loading {f}: {e}")
            
    print(f"Loaded {len(all_series)} files. Merging and resampling to 1-minute...")
    if not all_series:
        return pd.DataFrame()
        
    merged_df = pd.concat(all_series, axis=1)
    resampled_df = merged_df.resample('1min').ffill(limit=10).dropna(how='all')
    
    return resampled_df

def main():
    parser = argparse.ArgumentParser(description="Find TP2 Arbitrage Violations")
    parser.add_argument('--date-dir', type=str, required=True, help='Directory of the date, e.g., data-deep/2026-03-24')
    parser.add_argument('--symbol', type=str, required=True, help='Underlying symbol, e.g., IO')
    parser.add_argument('--min-score', type=float, default=0.01, help='Minimum score in price units (default: 0.01)')
    parser.add_argument('--net-carry', type=float, default=-0.01,
                        help='Net carry rate r-q annualised (default: -0.01, i.e. -1%% as observed for IO futures options)')
    args = parser.parse_args()

    df = load_and_align_data(args.date_dir, args.symbol)
    if df.empty:
        print("No data loaded. Exiting.")
        return

    # Collect ticker info
    tickers = set()
    for col in df.columns:
        tickers.add(col.split('_')[0])
        
    ticker_info = {}
    for t in tickers:
        und, year, month, typ, strike = parse_ticker(t)
        expiry_date = get_third_friday(year, month)
        ticker_info[t] = {'type': typ, 'strike': strike, 'expiry_date': expiry_date}

    violations = []
    print(f"Scanning {len(df)} 1-minute frames for TP2 violations...")

    for current_time, row in df.iterrows():
        # filter out non-trading hours (CFFEX: 09:30-11:30, 13:00-15:00)
        h, m = current_time.hour, current_time.minute
        if h < 9 or (h == 9 and m < 30) or (h == 11 and m > 30) or h == 12 or (h == 14 and m >= 55) or h >= 15:
            continue
            
        calls = []
        puts = []

        for t in tickers:
            info = ticker_info[t]
            dte_days = (info['expiry_date'].date() - current_time.date()).days
            if dte_days <= 1:
                continue

            a = row.get(f"{t}_ask", np.nan)
            b = row.get(f"{t}_bid", np.nan)

            if pd.isna(a) or pd.isna(b) or a <= 0 or b <= 0.5:
                continue

            item = {'t': t, 'k': info['strike'], 'dte': dte_days, 'a': a, 'b': b}
            if info['type'] == 'C':
                calls.append(item)
            else:
                puts.append(item)

        # -----------------------------------------------------------------------
        # TP2 no-arbitrage (additive form):
        #
        # Variable naming convention: x{T_index}{K_index}
        #   T1 < T2  (near expiry first)
        #   K1 < K2  (lower strike first)
        #
        # The no-arb condition is the calendar-spread dominance:
        #   [C/P](T2,K1) - [C/P](T2,K2)  >=  [C/P](T1,K1) - [C/P](T1,K2)
        #
        # Rearranged into a 4-leg trade (buy near spread, sell far spread):
        #   Buy  (T1,K1)  +  Buy  (T2,K2)
        #   Sell (T2,K1)  +  Sell (T1,K2)
        #
        # cost    = a(T1,K1) + a(T2,K2)   [what we pay]
        # revenue = b(T2,K1) + b(T1,K2)   [what we receive]
        # score   = revenue - cost          [net P&L per combo, in price units]
        #
        # This is identical for calls AND puts — the same 4-leg structure
        # applies to both option types.
        # -----------------------------------------------------------------------

        # Process Calls
        if len(calls) >= 4:
            calls_map = {(item['dte'], item['k']): item for item in calls}
            dtes = sorted(list({item['dte'] for item in calls}))
            strikes = sorted(list({item['k'] for item in calls}))
            
            for t1_idx in range(len(dtes)):
                for t2_idx in range(t1_idx + 1, len(dtes)):
                    t1, t2 = dtes[t1_idx], dtes[t2_idx]
                    for k1_idx in range(len(strikes)):
                        for k2_idx in range(k1_idx + 1, len(strikes)):
                            k1, k2 = strikes[k1_idx], strikes[k2_idx]
                            
                            # c{T}{K}: c11=(T1,K1), c12=(T2,K1), c21=(T1,K2), c22=(T2,K2)
                            c11 = calls_map.get((t1, k1))
                            c12 = calls_map.get((t2, k1))
                            c21 = calls_map.get((t1, k2))
                            c22 = calls_map.get((t2, k2))
                            
                            if not (c11 and c12 and c21 and c22):
                                continue
                            
                            # Discount far-leg (T2) prices back to T1 present value.
                            # carry = r - q = -0.01 (observed for IO futures options):
                            # negative carry means far-leg prices are worth *more*
                            # in PV terms, so discount > 1 — correctly inflating
                            # the far-leg before comparison.
                            dt       = (t2 - t1) / 365.0
                            discount = math.exp(-args.net_carry * dt)

                            # Carry-adjusted mid prices
                            mid11 = (c11['a'] + c11['b']) / 2.0
                            mid12 = ((c12['a'] + c12['b']) / 2.0) * discount
                            mid21 = (c21['a'] + c21['b']) / 2.0
                            mid22 = ((c22['a'] + c22['b']) / 2.0) * discount

                            if mid11 <= 0 or mid12 <= 0 or mid21 <= 0 or mid22 <= 0:
                                continue

                            # Score: carry-adjusted log TP2 determinant
                            ratio = (mid11 * mid22) / (mid21 * mid12)
                            score = -math.log(ratio)

                            # Keep cost and rev for logging/reference
                            cost  = c11['a'] + c22['a'] * discount
                            rev   = c12['b'] * discount + c21['b']

                            if score > args.min_score:
                                violations.append({
                                    'time': current_time,
                                    'option_type': 'C',
                                    'k1': k1, 'k2': k2,
                                    't1': t1, 't2': t2,
                                    'leg1_buy':  c11['t'],  # buy (T1,K1)
                                    'leg2_buy':  c22['t'],  # buy (T2,K2)
                                    'leg1_sell': c12['t'],  # sell (T2,K1)
                                    'leg2_sell': c21['t'],  # sell (T1,K2)
                                    'cost': cost,
                                    'revenue': rev,
                                    'score': score
                                })
                                    
        # Process Puts — identical 4-leg structure as calls
        if len(puts) >= 4:
            puts_map = {(item['dte'], item['k']): item for item in puts}
            dtes = sorted(list({item['dte'] for item in puts}))
            strikes = sorted(list({item['k'] for item in puts}))
            
            for t1_idx in range(len(dtes)):
                for t2_idx in range(t1_idx + 1, len(dtes)):
                    t1, t2 = dtes[t1_idx], dtes[t2_idx]
                    for k1_idx in range(len(strikes)):
                        for k2_idx in range(k1_idx + 1, len(strikes)):
                            k1, k2 = strikes[k1_idx], strikes[k2_idx]
                            
                            # p{T}{K}: p11=(T1,K1), p12=(T2,K1), p21=(T1,K2), p22=(T2,K2)
                            p11 = puts_map.get((t1, k1))
                            p12 = puts_map.get((t2, k1))
                            p21 = puts_map.get((t1, k2))
                            p22 = puts_map.get((t2, k2))
                            
                            if not (p11 and p12 and p21 and p22):
                                continue

                            # Discount far-leg (T2) prices back to T1 present value.
                            # Same carry adjustment as calls.
                            dt       = (t2 - t1) / 365.0
                            discount = math.exp(-args.net_carry * dt)

                            # Carry-adjusted mid prices
                            mid11 = (p11['a'] + p11['b']) / 2.0
                            mid12 = ((p12['a'] + p12['b']) / 2.0) * discount
                            mid21 = (p21['a'] + p21['b']) / 2.0
                            mid22 = ((p22['a'] + p22['b']) / 2.0) * discount

                            if mid11 <= 0 or mid12 <= 0 or mid21 <= 0 or mid22 <= 0:
                                continue

                            # Score: carry-adjusted log TP2 determinant
                            ratio = (mid11 * mid22) / (mid21 * mid12)
                            score = -math.log(ratio)

                            # Keep cost and rev for logging/reference
                            cost  = p11['a'] + p22['a'] * discount
                            rev   = p12['b'] * discount + p21['b']

                            if score > args.min_score:
                                violations.append({
                                    'time': current_time,
                                    'option_type': 'P',
                                    'k1': k1, 'k2': k2,
                                    't1': t1, 't2': t2,
                                    'leg1_buy':  p11['t'],  # buy (T1,K1)
                                    'leg2_buy':  p22['t'],  # buy (T2,K2)
                                    'leg1_sell': p12['t'],  # sell (T2,K1)
                                    'leg2_sell': p21['t'],  # sell (T1,K2)
                                    'cost': cost,
                                    'revenue': rev,
                                    'score': score
                                })

    if violations:
        res_df = pd.DataFrame(violations)
        res_df = res_df.sort_values(by='score', ascending=False)
        date_str = os.path.basename(os.path.normpath(args.date_dir))
        out_name = f"tp2_violations_{args.symbol}_{date_str}.csv"
        res_df.to_csv(out_name, index=False)
        print(f"Found {len(res_df)} violations. Saved to {out_name}.")
    else:
        print("No violations found.")

if __name__ == "__main__":
    main()