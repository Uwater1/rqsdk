"""
tp2_analysis.py  —  TP2 Phase 2 Research (Memory Optimized)
=========================================================

Memory saving features:
- Processes **one day at a time** to prevent massive DataFrame concatenation.
- Uses float32 for price matrices.
- Uses Numba for fast loop processing.
"""

import os
import sys
import glob
import math
import re
import argparse
import warnings
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from numba import njit

warnings.filterwarnings('ignore')

# ── Constants ────────────────────────────────────────────────────────────────
COMMISSION_PER_LEG = 1.0   # RMB per leg per contract
MULTIPLIER         = 100   # IO options: 100 RMB / index point
N_LEGS             = 4
MAX_FORWARD_MIN    = 90    # Look no further than 90 minutes forward
SCORE_IMPROVE_BY   = 1.0  # "improved by 1" exit threshold

# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def parse_ticker(ticker):
    match = re.match(r'([A-Z]+)(\d{2})(\d{2})([CP])(\d+)', ticker)
    if match:
        und, yy, mm, typ, strike = match.groups()
        return und, 2000 + int(yy), int(mm), typ, float(strike)
    return None, None, None, None, None

def load_price_data_for_day(data_dir, symbol='IO'):
    """Load price data for a SINGLE day to save memory. Cast to float32."""
    all_series = []
    path = os.path.join(data_dir, symbol, '*.parquet')
    for f in glob.glob(path):
        ticker = os.path.basename(f).replace('.parquet', '')
        und, *_ = parse_ticker(ticker)
        if not und:
            continue
        try:
            df = pd.read_parquet(f)
            if 'datetime' in df.index.names:
                df = df.reset_index()
            if 'datetime' not in df.columns:
                continue
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.set_index('datetime').sort_index()
            df = df[['a1', 'b1']].rename(
                columns={'a1': f'{ticker}_ask', 'b1': f'{ticker}_bid'})
            # ensure float32
            df = df.astype(np.float32)
            df = df[~df.index.duplicated(keep='last')]
            all_series.append(df)
        except Exception as e:
            pass

    if not all_series:
        return pd.DataFrame()

    merged = pd.concat(all_series, axis=1)
    resampled = merged.resample('1min').ffill(limit=10).dropna(how='all')
    return resampled

@njit
def fast_compute_score(a11, b11, a22, b22, a12, b12, a21, b21, discount):
    if (math.isnan(a11) or a11<=0 or math.isnan(b11) or b11<=0 or 
        math.isnan(a22) or a22<=0 or math.isnan(b22) or b22<=0 or
        math.isnan(a12) or a12<=0 or math.isnan(b12) or b12<=0 or
        math.isnan(a21) or a21<=0 or math.isnan(b21) or b21<=0):
        return np.nan
        
    mid11 = (a11 + b11) / 2.0
    mid12 = ((a12 + b12) / 2.0) * discount
    mid21 = (a21 + b21) / 2.0
    mid22 = ((a22 + b22) / 2.0) * discount

    ratio = (mid11 * mid22) / (mid21 * mid12)
    return -math.log(ratio)

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 1 — PERSISTENCE
# ═══════════════════════════════════════════════════════════════════════════════

def run_persistence_for_day(viol_df, price_df, net_carry):
    records = []
    
    # Pre-extract numpy arrays for fast access
    timestamps = price_df.index.values
    columns = price_df.columns.tolist()
    col_idx = {col: i for i, col in enumerate(columns)}
    price_mat = price_df.values # shape: (times, cols), float32
    
    for i, row_v in viol_df.iterrows():
        t0          = pd.Timestamp(row_v['time'])
        l1b         = row_v['leg1_buy']
        l2b         = row_v['leg2_buy']
        l1s         = row_v['leg1_sell']
        l2s         = row_v['leg2_sell']
        t1_dte      = int(row_v['t1'])
        t2_dte      = int(row_v['t2'])
        score0      = float(row_v['score'])
        
        # Check if columns exist
        c_a11 = col_idx.get(f'{l1b}_ask', -1); c_b11 = col_idx.get(f'{l1b}_bid', -1)
        c_a22 = col_idx.get(f'{l2b}_ask', -1); c_b22 = col_idx.get(f'{l2b}_bid', -1)
        c_a12 = col_idx.get(f'{l1s}_ask', -1); c_b12 = col_idx.get(f'{l1s}_bid', -1)
        c_a21 = col_idx.get(f'{l2s}_ask', -1); c_b21 = col_idx.get(f'{l2s}_bid', -1)
        
        if -1 in [c_a11, c_b11, c_a22, c_b22, c_a12, c_b12, c_a21, c_b21]:
            continue

        dt = (t2_dte - t1_dte) / 365.0
        discount = math.exp(-net_carry * dt)
        
        t_end_window  = t0 + timedelta(minutes=MAX_FORWARD_MIN)
        t_session_end = t0.replace(hour=14, minute=55, second=0, microsecond=0)
        t_cap         = min(t_end_window, t_session_end)
        
        # Find indices
        t0_val = t0.to_numpy()
        cap_val = t_cap.to_numpy()
        mask = (timestamps > t0_val) & (timestamps <= cap_val)
        fwd_idx = np.where(mask)[0]
        
        ttl_min         = np.nan
        ttl_improve1    = np.nan
        peak_score      = score0
        resolved        = False
        exit_reason     = None
        n_tracked       = 0
        
        offset_min = 0
        for idx in fwd_idx:
            offset_min += 1
            a11, b11 = price_mat[idx, c_a11], price_mat[idx, c_b11]
            a22, b22 = price_mat[idx, c_a22], price_mat[idx, c_b22]
            a12, b12 = price_mat[idx, c_a12], price_mat[idx, c_b12]
            a21, b21 = price_mat[idx, c_a21], price_mat[idx, c_b21]
            
            s = fast_compute_score(a11, b11, a22, b22, a12, b12, a21, b21, discount)
            n_tracked += 1
            
            if not math.isnan(s):
                if s > peak_score:
                    peak_score = s
                if math.isnan(ttl_improve1) and (score0 - s) >= SCORE_IMPROVE_BY:
                    ttl_improve1 = offset_min
                if math.isnan(ttl_min) and s <= 0:
                    ttl_min = offset_min
                    resolved = True
                    exit_reason = 'reverted'
                    break

        if exit_reason is None:
            if not math.isnan(ttl_improve1):
                exit_reason = 'improved_by_1'
            elif offset_min >= 60:
                exit_reason = 'timeout_60min' if offset_min < MAX_FORWARD_MIN else 'timeout_90min'
            else:
                exit_reason = 'session_end'

        records.append({
            'time':         t0,
            'option_type':  row_v['option_type'],
            'k1':           row_v['k1'],
            'k2':           row_v['k2'],
            't1':           t1_dte,
            't2':           t2_dte,
            'score0':       score0,
            'peak_score':   peak_score,
            'ttl_min':      ttl_min,
            'ttl_improve1': ttl_improve1,
            'n_tracked':    n_tracked,
            'resolved':     resolved,
            'exit_reason':  exit_reason,
            'leg1_buy':     l1b, 'leg2_buy': l2b, 'leg1_sell': l1s, 'leg2_sell': l2s
        })

    return pd.DataFrame(records)

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 2 — PROFITABILITY
# ═══════════════════════════════════════════════════════════════════════════════

def run_profitability_for_day(viol_df, price_df, persist_df, net_carry, next_price_df=None):
    if persist_df.empty: return pd.DataFrame()
    persist_indexed = persist_df.set_index('time')
    
    timestamps = price_df.index
    columns = price_df.columns.tolist()
    col_idx = {col: i for i, col in enumerate(columns)}
    price_mat = price_df.values
    
    if next_price_df is not None and not next_price_df.empty:
        next_timestamps = next_price_df.index
        next_columns = next_price_df.columns.tolist()
        next_col_idx = {col: i for i, col in enumerate(next_columns)}
        next_price_mat = next_price_df.values
    else:
        next_timestamps = None
        next_col_idx = {}
        next_price_mat = None

    records = []
    
    commission_pts = (N_LEGS * 2 * COMMISSION_PER_LEG) / MULTIPLIER

    for i, row_v in viol_df.iterrows():
        t0 = pd.Timestamp(row_v['time'])
        if t0 not in persist_indexed.index: continue
        pr = persist_indexed.loc[t0]
        if isinstance(pr, pd.DataFrame):
            # match by legs
            pr = pr[(pr['leg1_buy'] == row_v['leg1_buy']) & (pr['k1'] == row_v['k1'])].iloc[0]
            
        l1b, l2b = row_v['leg1_buy'], row_v['leg2_buy']
        l1s, l2s = row_v['leg1_sell'], row_v['leg2_sell']
        
        c_a11 = col_idx.get(f'{l1b}_ask', -1); c_b11 = col_idx.get(f'{l1b}_bid', -1)
        c_a22 = col_idx.get(f'{l2b}_ask', -1); c_b22 = col_idx.get(f'{l2b}_bid', -1)
        c_a12 = col_idx.get(f'{l1s}_ask', -1); c_b12 = col_idx.get(f'{l1s}_bid', -1)
        c_a21 = col_idx.get(f'{l2s}_ask', -1); c_b21 = col_idx.get(f'{l2s}_bid', -1)
        
        if -1 in [c_a11, c_b11, c_a22, c_b22, c_a12, c_b12, c_a21, c_b21]: continue

        # Entry Price
        pos = timestamps.get_indexer([t0], method='pad')[0]
        if pos == -1: continue
        
        dt = (row_v['t2'] - row_v['t1']) / 365.0
        discount = math.exp(-net_carry * dt)
        
        a11 = price_mat[pos, c_a11]
        a22 = price_mat[pos, c_a22] * discount
        b12 = price_mat[pos, c_b12] * discount
        b21 = price_mat[pos, c_b21]
        
        if any(math.isnan(v) or v<=0 for v in [a11,a22,b12,b21]): continue
        entry_pnl = (b12 + b21) - (a11 + a22)

        def get_exit_pnl(exit_ts):
            idx = timestamps.get_indexer([exit_ts], method='pad')[0]
            if idx == -1: return np.nan
            b11 = price_mat[idx, c_b11]
            b22 = price_mat[idx, c_b22] * discount
            a12 = price_mat[idx, c_a12] * discount
            a21 = price_mat[idx, c_a21]
            if any(math.isnan(v) or v<=0 for v in [b11,b22,a12,a21]): return np.nan
            return (b11 + b22) - (a12 + a21)

        def get_exit_score(exit_ts):
            idx = timestamps.get_indexer([exit_ts], method='pad')[0]
            if idx == -1: return np.nan
            a11, b11 = price_mat[idx, c_a11], price_mat[idx, c_b11]
            a22, b22 = price_mat[idx, c_a22], price_mat[idx, c_b22]
            a12, b12 = price_mat[idx, c_a12], price_mat[idx, c_b12]
            a21, b21 = price_mat[idx, c_a21], price_mat[idx, c_b21]
            return fast_compute_score(a11, b11, a22, b22, a12, b12, a21, b21, discount)

        results = {'entry_pnl_pts': entry_pnl}
        
        ttl = pr.get('ttl_min', np.nan)
        if pd.notna(ttl):
            ep = get_exit_pnl(t0 + pd.Timedelta(minutes=int(ttl)))
            if pd.notna(ep):
                results['exit_revert_gross_pts'] = entry_pnl + ep
                results['exit_revert_net_rmb'] = (entry_pnl + ep - commission_pts) * MULTIPLIER
                
        ti1 = pr.get('ttl_improve1', np.nan)
        if pd.notna(ti1):
            ep = get_exit_pnl(t0 + pd.Timedelta(minutes=int(ti1)))
            if pd.notna(ep):
                results['exit_improve1_gross_pts'] = entry_pnl + ep
                results['exit_improve1_net_rmb'] = (entry_pnl + ep - commission_pts) * MULTIPLIER
                
        t_session_end = t0.replace(hour=14, minute=55, second=0)
        for m in [15, 30, 60]:
            ts_exit = min(t0 + pd.Timedelta(minutes=m), t_session_end)
            ep = get_exit_pnl(ts_exit)
            if pd.notna(ep):
                results[f'exit_{m}min_gross_pts'] = entry_pnl + ep
                results[f'exit_{m}min_net_rmb'] = (entry_pnl + ep - commission_pts) * MULTIPLIER
            
            es = get_exit_score(ts_exit)
            if pd.notna(es):
                results[f'score_{m}min'] = es

        results['exit_next_day_gross_pts'] = np.nan
        results['exit_next_day_net_rmb'] = np.nan
        results['score_next_day'] = np.nan

        if next_timestamps is not None:
            nc_a11 = next_col_idx.get(f'{l1b}_ask', -1); nc_b11 = next_col_idx.get(f'{l1b}_bid', -1)
            nc_a22 = next_col_idx.get(f'{l2b}_ask', -1); nc_b22 = next_col_idx.get(f'{l2b}_bid', -1)
            nc_a12 = next_col_idx.get(f'{l1s}_ask', -1); nc_b12 = next_col_idx.get(f'{l1s}_bid', -1)
            nc_a21 = next_col_idx.get(f'{l2s}_ask', -1); nc_b21 = next_col_idx.get(f'{l2s}_bid', -1)
            
            if -1 not in [nc_a11, nc_b11, nc_a22, nc_b22, nc_a12, nc_b12, nc_a21, nc_b21]:
                def get_next_day_exit_pnl(exit_ts):
                    idx = next_timestamps.get_indexer([exit_ts], method='pad')[0]
                    if idx == -1: return np.nan
                    b11 = next_price_mat[idx, nc_b11]
                    b22 = next_price_mat[idx, nc_b22] * discount
                    a12 = next_price_mat[idx, nc_a12] * discount
                    a21 = next_price_mat[idx, nc_a21]
                    if any(math.isnan(v) or v<=0 for v in [b11,b22,a12,a21]): return np.nan
                    return (b11 + b22) - (a12 + a21)

                def get_next_day_exit_score(exit_ts):
                    idx = next_timestamps.get_indexer([exit_ts], method='pad')[0]
                    if idx == -1: return np.nan
                    a11, b11 = next_price_mat[idx, nc_a11], next_price_mat[idx, nc_b11]
                    a22, b22 = next_price_mat[idx, nc_a22], next_price_mat[idx, nc_b22]
                    a12, b12 = next_price_mat[idx, nc_a12], next_price_mat[idx, nc_b12]
                    a21, b21 = next_price_mat[idx, nc_a21], next_price_mat[idx, nc_b21]
                    return fast_compute_score(a11, b11, a22, b22, a12, b12, a21, b21, discount)

                next_day_date = next_timestamps[0].normalize()
                t_next_session_end = next_day_date + pd.Timedelta(hours=14, minutes=55)
                ep_next = get_next_day_exit_pnl(t_next_session_end)
                if pd.notna(ep_next):
                    results['exit_next_day_gross_pts'] = entry_pnl + ep_next
                    results['exit_next_day_net_rmb'] = (entry_pnl + ep_next - commission_pts) * MULTIPLIER
                
                es_next = get_next_day_exit_score(t_next_session_end)
                if pd.notna(es_next):
                    results['score_next_day'] = es_next

        rec = {
            'time': t0, 'option_type': row_v['option_type'], 'score0': row_v['score'],
            'k1': row_v['k1'], 'k2': row_v['k2'], 't1': row_v['t1'], 't2': row_v['t2'],
        }
        rec.update(results)
        records.append(rec)

    return pd.DataFrame(records)

# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY PRINTING MINIMAL
# ─────────────────────────────────────────────────────────────────────────────

def print_characterisation(viol_df, persist_df, profit_df):
    print("\n" + "═" * 70)
    print("MODULE 3 — CHARACTERISATION")
    print("═" * 70)

    # Option type breakdown
    print("\n── By option type ───────────────────────────────────────────────")
    for otype in ['C', 'P']:
        sub = viol_df[viol_df['option_type'] == otype]
        if sub.empty: continue
        print(f"  {otype}: {len(sub)} violations  |  score mean={sub['score'].mean():.3f}  max={sub['score'].max():.3f}")

    if profit_df is not None:
        print("\n── Score Evolution (Mean) ───────────────────────────────────────")
        cols = ['score0', 'score_15min', 'score_30min', 'score_60min', 'score_next_day']
        available_cols = [c for c in cols if c in profit_df.columns]
        if available_cols:
            means = profit_df[available_cols].mean()
            for c in available_cols:
                print(f"  {c:15s}: {means[c]:.4f}")

    if profit_df is not None and 'exit_15min_net_rmb' in profit_df.columns:
        print("\n── Profitability by score band (15-min exit) ────────────────────")
        bands = [(1.0, 1.5), (1.5, 2.0), (2.0, 9.9)]
        for lo, hi in bands:
            sub = profit_df[(profit_df['score0'] >= lo) & (profit_df['score0'] < hi) &
                             profit_df['exit_15min_net_rmb'].notna()]
            if sub.empty: continue
            wr  = (sub['exit_15min_net_rmb'] > 0).mean()
            avg = sub['exit_15min_net_rmb'].mean()
            print(f"  {lo:.1f} ≤ score < {hi:.1f}: n={len(sub):4d}  win={wr:.1%}  avg_net={avg:.1f} RMB")

    if profit_df is not None and 'exit_next_day_net_rmb' in profit_df.columns:
        print("\n── Profitability by score band (Next-day exit) ──────────────────")
        bands = [(1.0, 1.5), (1.5, 2.0), (2.0, 9.9)]
        for lo, hi in bands:
            sub = profit_df[(profit_df['score0'] >= lo) & (profit_df['score0'] < hi) &
                             profit_df['exit_next_day_net_rmb'].notna()]
            if sub.empty: continue
            wr  = (sub['exit_next_day_net_rmb'] > 0).mean()
            avg = sub['exit_next_day_net_rmb'].mean()
            print(f"  {lo:.1f} ≤ score < {hi:.1f}: n={len(sub):4d}  win={wr:.1%}  avg_net={avg:.1f} RMB")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--violations', type=str, nargs='+', required=True)
    parser.add_argument('--data-dirs',  type=str, nargs='+', required=True)
    parser.add_argument('--symbol',     type=str, default='IO')
    parser.add_argument('--mode',       type=str, default='full')
    parser.add_argument('--min-score',  type=float, default=1.0)
    parser.add_argument('--net-carry',  type=float, default=-0.01)
    parser.add_argument('--out-prefix', type=str, default='tp2_analysis')
    args = parser.parse_args()

    all_persist = []
    all_profit = []
    all_viols = []

    # Map directories by date string
    dir_map = {}
    for d in args.data_dirs:
        date_str = os.path.basename(d.rstrip('/'))
        dir_map[date_str] = d

    # Group violations by date
    viols_by_date = {}
    for pattern in args.violations:
        for f in glob.glob(pattern):
            # Extract date from filename, e.g. tp2_violations_IO_2026-03-24.csv
            m = re.search(r'(\d{4}-\d{2}-\d{2})', f)
            if not m: continue
            d_str = m.group(1)
            if d_str not in viols_by_date: viols_by_date[d_str] = []
            viols_by_date[d_str].append(f)

    sorted_dates = sorted(dir_map.keys())

    for d_str in sorted(viols_by_date.keys()):
        files = viols_by_date[d_str]
        if d_str not in dir_map:
            continue
            
        print(f"Processing {d_str}...", end=' ', flush=True)
        dfs = []
        for f in files:
            dfs.append(pd.read_csv(f))
        
        viol_day = pd.concat(dfs, ignore_index=True)
        viol_day = viol_day[viol_day['score'] >= args.min_score].reset_index(drop=True)
        if viol_day.empty: 
            print("No violations.")
            continue
        all_viols.append(viol_day)
        
        price_day = load_price_data_for_day(dir_map[d_str], args.symbol)
        if price_day.empty: 
            print("No price data.")
            continue
        
        if args.mode in ('persist', 'full'):
            p_df = run_persistence_for_day(viol_day, price_day, args.net_carry)
            all_persist.append(p_df)
            
            if args.mode == 'full':
                next_price_day = None
                try:
                    curr_idx = sorted_dates.index(d_str)
                    if curr_idx + 1 < len(sorted_dates):
                        next_d_str = sorted_dates[curr_idx + 1]
                        next_price_day = load_price_data_for_day(dir_map[next_d_str], args.symbol)
                except ValueError:
                    pass
                    
                prof_df = run_profitability_for_day(viol_day, price_day, p_df, args.net_carry, next_price_day)
                all_profit.append(prof_df)
        print("Done.")

    if not all_persist:
        print("No valid results computed.")
        return

    persist_combined = pd.concat(all_persist, ignore_index=True)
    persist_combined.to_csv(f"{args.out_prefix}_persist.csv", index=False)
    print(f"\nSaved {args.out_prefix}_persist.csv ({len(persist_combined)} rows)")
    
    profit_combined = None
    if all_profit:
        profit_combined = pd.concat(all_profit, ignore_index=True)
        profit_combined.to_csv(f"{args.out_prefix}_profit.csv", index=False)
        print(f"Saved {args.out_prefix}_profit.csv ({len(profit_combined)} rows)")
        
    print_characterisation(pd.concat(all_viols, ignore_index=True), persist_combined, profit_combined)


if __name__ == '__main__':
    main()
