"""
boxx.py - Real-time box spread scanner for CFFEX index options
"""
import os
import re
import sys
import glob
from datetime import datetime, timedelta
from collections import defaultdict

import numpy as np
from numba import njit
import pandas as pd

# ── constants ────────────────────────────────────────────────────────────────

# 0.2 point commission per leg (4 legs for a full box spread)
# Only paid at open; other price (including exercise) is included.
COMMISSION_PER_LEG = 0.2
BOX_COMMISSION = 4 * COMMISSION_PER_LEG


# ── helpers ─────────────────────────────────────────────────────────────────

TICKER_RE = re.compile(r'^(IO|HO|MO)(\d{4})([CP])(\d+)')

def get_3rd_friday(year: int, month: int) -> datetime:
    """Return the 3rd Friday of a given year/month (expiry date for CFFEX options)."""
    first = datetime(year, month, 1)
    # weekday(): Mon=0 ... Fri=4
    offset = (4 - first.weekday()) % 7
    return first + timedelta(days=offset + 14)  # 1st Friday + 2 weeks


def parse_ticker(order_book_id: str):
    """
    Parse order_book_id like 'IO2604C4400' into
    (prefix, expiry_str, opt_type, strike).
    Returns None if it doesn't match.
    """
    m = TICKER_RE.match(order_book_id)
    if not m:
        return None
    prefix, expiry, opt_type, strike = m.group(1), m.group(2), m.group(3), int(m.group(4))
    year  = 2000 + int(expiry[:2])
    month = int(expiry[2:])
    expiry_dt = get_3rd_friday(year, month)
    return prefix, expiry_dt, opt_type, strike


# ── data loading ─────────────────────────────────────────────────────────────

def load_date_folder(date_dir: str) -> dict:
    """
    Load all .parquet option files from subfolders IO/, HO/, MO/ under date_dir.

    Returns a dict keyed by (prefix, expiry_dt):
        {
            (prefix, expiry_dt): {
                'strikes_c': sorted list of strikes with Calls,
                'strikes_p': sorted list of strikes with Puts,
                'common_strikes': sorted list of strikes with both C and P,
                'df_c': {strike: DataFrame(a1, b1) resampled to 2S},
                'df_p': {strike: DataFrame(a1, b1) resampled to 2S},
            }
        }
    """
    folders = ['IO', 'HO', 'MO']
    groups = defaultdict(lambda: {'calls': {}, 'puts': {}})

    for sub in folders:
        sub_dir = os.path.join(date_dir, sub)
        if not os.path.isdir(sub_dir):
            continue
        for fpath in sorted(glob.glob(os.path.join(sub_dir, '*.parquet'))):
            oid = os.path.splitext(os.path.basename(fpath))[0]
            parsed = parse_ticker(oid)
            if parsed is None:
                continue
            prefix, expiry_dt, opt_type, strike = parsed
            key = (prefix, expiry_dt)

            df = pd.read_parquet(fpath, columns=['a1', 'b1'])
            df.index = df.index.get_level_values('datetime')
            df = df[df.index.time >= __import__('datetime').time(9, 30)]  # trading hours only

            if opt_type == 'C':
                groups[key]['calls'][strike] = df
            else:
                groups[key]['puts'][strike] = df

    # Build per-expiry aligned arrays
    result = {}
    for key, data in groups.items():
        calls = data['calls']
        puts  = data['puts']
        common = sorted(set(calls) & set(puts))
        if len(common) < 2:
            continue
        result[key] = {
            'common_strikes': common,
            'calls': {k: calls[k] for k in common},
            'puts':  {k: puts[k]  for k in common},
        }

    return result


def build_unified_timeline(group: dict, freq='2S'):
    """
    Given a group (one expiry), resample each strike's prices to a unified 2-second grid,
    forward-fill (limit=1 tick, i.e. valid for 2 seconds).

    Returns:
        timestamps: DatetimeIndex
        c_ask: 2D float64 array (T, N_strikes)  -- ask prices for calls
        c_bid: 2D float64 array (T, N_strikes)
        p_ask: 2D float64 array (T, N_strikes)
        p_bid: 2D float64 array (T, N_strikes)
        strikes: 1D int array (N_strikes)
    """
    strikes = group['common_strikes']
    calls = group['calls']
    puts  = group['puts']

    # Collect all timestamps across all strikes → unified index
    all_times = pd.DatetimeIndex([])
    for k in strikes:
        all_times = all_times.union(calls[k].index)
        all_times = all_times.union(puts[k].index)

    # Snap to 2-second grid (use lowercase '2s' - pandas ≥2.2)
    all_times = all_times.floor('2s').unique().sort_values()

    T = len(all_times)
    N = len(strikes)
    c_ask = np.zeros((T, N), dtype=np.float64)
    c_bid = np.zeros((T, N), dtype=np.float64)
    p_ask = np.zeros((T, N), dtype=np.float64)
    p_bid = np.zeros((T, N), dtype=np.float64)

    for j, k in enumerate(strikes):
        # Resample to 2s grid, forward-fill exactly 1 period
        c = calls[k].resample('2s', closed='left', label='left').last().reindex(all_times).ffill(limit=1).fillna(0)
        p = puts[k].resample('2s',  closed='left', label='left').last().reindex(all_times).ffill(limit=1).fillna(0)
        c_ask[:, j] = c['a1'].values
        c_bid[:, j] = c['b1'].values
        p_ask[:, j] = p['a1'].values
        p_bid[:, j] = p['b1'].values

    return all_times, c_ask, c_bid, p_ask, p_bid, np.array(strikes, dtype=np.int64)


# ── numba box-spread kernel ──────────────────────────────────────────────────

@njit(cache=True)
def find_best_boxes(c_ask, c_bid, p_ask, p_bid, ks, dte):
    """
    For each time step t, iterate over all (i,j) strike pairs (i<j) and compute:
      - Long box  : buy C_i, sell C_j, buy P_j, sell P_i
      - Short box : sell C_i, buy C_j, sell P_j, buy P_i

    Returns parallel arrays of length T:
      long_K1, long_K2, long_cost, long_payout, long_ret, long_ann
      short_K1, short_K2, short_credit, short_margin, short_ret, short_ann
    All initialised to 0/-999 to signal "no valid box found".
    """
    T, N = c_ask.shape
    ann_factor = 365.0 / dte

    long_K1     = np.zeros(T, np.int64)
    long_K2     = np.zeros(T, np.int64)
    long_cost   = np.zeros(T, np.float64)
    long_payout = np.zeros(T, np.float64)
    long_ret    = np.full(T, -999.0, np.float64)
    long_ann    = np.full(T, -999.0, np.float64)

    short_K1      = np.zeros(T, np.int64)
    short_K2      = np.zeros(T, np.int64)
    short_credit  = np.zeros(T, np.float64)
    short_margin  = np.zeros(T, np.float64)
    short_ret     = np.full(T, -999.0, np.float64)
    short_ann     = np.full(T, -999.0, np.float64)

    for t in range(T):
        for i in range(N):
            for j in range(i + 1, N):
                K1 = ks[i]
                K2 = ks[j]
                payout = float(K2 - K1)

                # prices must be valid (>0)
                ca1 = c_ask[t, i]; cb1 = c_bid[t, i]
                ca2 = c_ask[t, j]; cb2 = c_bid[t, j]
                pa1 = p_ask[t, i]; pb1 = p_bid[t, i]
                pa2 = p_ask[t, j]; pb2 = p_bid[t, j]

                # Long box: buy C_i@ask, sell C_j@bid, buy P_j@ask, sell P_i@bid
                if ca1 > 0 and cb2 > 0 and pa2 > 0 and pb1 > 0:
                    # Plus commission to open (4 legs * 0.2)
                    cost = (ca1 - cb2) + (pa2 - pb1) + BOX_COMMISSION
                    if cost > 0:
                        r = (payout - cost) / cost
                        if r > long_ret[t]:
                            long_K1[t]     = K1
                            long_K2[t]     = K2
                            long_cost[t]   = cost
                            long_payout[t] = payout
                            long_ret[t]    = r
                            long_ann[t]    = r * ann_factor

                # Short box: sell C_i@bid, buy C_j@ask, sell P_j@bid, buy P_i@ask
                if cb1 > 0 and ca2 > 0 and pb2 > 0 and pa1 > 0:
                    # Minus commission to open (4 legs * 0.2)
                    credit = (cb1 - ca2) + (pb2 - pa1) - BOX_COMMISSION
                    if credit > 0:
                        r = (credit - payout) / payout
                        if r > short_ret[t]:
                            short_K1[t]     = K1
                            short_K2[t]     = K2
                            short_credit[t] = credit
                            short_margin[t] = payout
                            short_ret[t]    = r
                            short_ann[t]    = r * ann_factor

    return (long_K1, long_K2, long_cost, long_payout, long_ret, long_ann,
            short_K1, short_K2, short_credit, short_margin, short_ret, short_ann)


# ── minute batching ───────────────────────────────────────────────────────────

def batch_by_minute(timestamps, kernel_out, prefix, expiry, dte):
    """
    Group per-tick kernel results into 1-minute windows.
    For each minute, find the single tick with the best ann_ret
    among ticks that have a positive return (ret > 0).

    kernel_out: tuple returned by find_best_boxes
    Returns list of dicts, one per minute, keys:
      minute, prefix, expiry, dte,
      long_K1, long_K2, long_cost, long_payout, long_ret, long_ann,
      short_K1, short_K2, short_credit, short_margin, short_ret, short_ann
    """
    (lK1, lK2, lcost, lpay, lret, lann,
     sK1, sK2, scred, smarg, sret, sann) = kernel_out

    # floor timestamps to minutes
    minutes = timestamps.floor('1min')
    unique_mins = pd.DatetimeIndex(sorted(set(minutes)))

    rows = []
    for mn in unique_mins:
        mask = (minutes == mn)
        row = {'minute': mn, 'prefix': prefix, 'expiry': expiry, 'dte': dte}

        # best long tick this minute
        lr = lret[mask]
        if lr.max() > 0:
            best = np.argmax(lr)
            idxs = np.where(mask)[0]
            t = idxs[best]
            row.update(long_K1=int(lK1[t]), long_K2=int(lK2[t]),
                       long_cost=lcost[t], long_payout=lpay[t],
                       long_ret=lret[t], long_ann=lann[t])
        else:
            row.update(long_K1=0, long_K2=0, long_cost=0, long_payout=0,
                       long_ret=-999, long_ann=-999)

        # best short tick this minute
        sr = sret[mask]
        if sr.max() > 0:
            best = np.argmax(sr)
            idxs = np.where(mask)[0]
            t = idxs[best]
            row.update(short_K1=int(sK1[t]), short_K2=int(sK2[t]),
                       short_credit=scred[t], short_margin=smarg[t],
                       short_ret=sret[t], short_ann=sann[t])
        else:
            row.update(short_K1=0, short_K2=0, short_credit=0, short_margin=0,
                       short_ret=-999, short_ann=-999)

        rows.append(row)
    return rows


# ── scanner: loops all expiry groups, merges per-minute best ─────────────────

def run_scanner(date_dir: str, out_dir: str = '.'):
    """
    Main entry point.
    - Loads all expiry groups.
    - Classifies each group as 'near' (min DTE), 'mid' (2nd smallest DTE ≤60),
      or 'far' (DTE >60, only used for short box).
    - Runs numba kernel on each group.
    - Batches results by minute.
    - For each minute, picks the best near-long, mid-long, and short across ALL groups.
    - Writes 3 CSV files to out_dir.
    """
    trade_date = pd.Timestamp(os.path.basename(date_dir))
    date_str = trade_date.strftime('%Y-%m-%d')

    print(f"Loading: {date_dir}")
    groups = load_date_folder(date_dir)
    if not groups:
        print("No data found.")
        return

    # Compute DTE for each group
    group_meta = {}
    for (prefix, expiry), g in groups.items():
        dte = (expiry - trade_date.to_pydatetime()).days
        group_meta[(prefix, expiry)] = dte

    all_dtes = sorted(set(group_meta.values()))
    min_dte  = all_dtes[0]
    mid_dte  = all_dtes[1] if len(all_dtes) > 1 else None

    print(f"DTE classes: near={min_dte}, mid={mid_dte}, others={all_dtes[2:]}")

    # Per-minute accumulators keyed by minute timestamp
    # Each stores the best row seen across all groups for that category
    near_best:  dict = {}   # long box, near DTE
    mid_best:   dict = {}   # long box, mid DTE
    short_best: dict = {}   # short box, any DTE

    for (prefix, expiry), g in groups.items():
        dte = group_meta[(prefix, expiry)]
        print(f"  [{prefix}] exp={expiry.date()} DTE={dte} ...", end='', flush=True)

        ts, ca, cb, pa, pb, ks = build_unified_timeline(g)
        out = find_best_boxes(ca, cb, pa, pb, ks, float(dte))
        rows = batch_by_minute(ts, out, prefix, expiry, dte)
        print(f" {len(rows)} mins")

        for r in rows:
            mn = r['minute']

            # ── long box ──
            if r['long_ret'] > 0:
                if dte == min_dte:
                    if mn not in near_best or r['long_ann'] > near_best[mn]['long_ann']:
                        near_best[mn] = r
                elif mid_dte is not None and mid_dte <= 60 and dte == mid_dte:
                    if mn not in mid_best or r['long_ann'] > mid_best[mn]['long_ann']:
                        mid_best[mn] = r

            # ── short box (any DTE ≤60) ──
            if r['short_ret'] > 0 and dte <= 60:
                if mn not in short_best or r['short_ann'] > short_best[mn]['short_ann']:
                    short_best[mn] = r

    write_csvs(near_best, mid_best, short_best, date_str, out_dir)


# ── CSV writer ────────────────────────────────────────────────────────────────

LONG_HEADER  = ['Minute','Prefix','K1','K2','DTE','Cost','Payout','Exp Return','Ann Return','Action']
SHORT_HEADER = ['Minute','Prefix','K1','K2','DTE','Credit','Margin','Exp Return','Ann Return','Action']

def _long_row(mn, r):
    prefix = r['prefix']
    exp = r['expiry'].strftime('%y%m')  # e.g. 2604
    action = (f"Buy {prefix}{exp}C{r['long_K1']}; "
              f"Sell {prefix}{exp}C{r['long_K2']}; "
              f"Buy {prefix}{exp}P{r['long_K2']}; "
              f"Sell {prefix}{exp}P{r['long_K1']}")
    return [mn, f"[{prefix}]",
            r['long_K1'], r['long_K2'], r['dte'],
            f"{r['long_cost']:.2f}", f"{r['long_payout']:.2f}",
            f"{r['long_ret']*100:.2f}%", f"{r['long_ann']*100:.2f}%",
            action]

def _short_row(mn, r):
    prefix = r['prefix']
    exp = r['expiry'].strftime('%y%m')
    action = (f"Sell {prefix}{exp}C{r['short_K1']}; "
              f"Buy {prefix}{exp}C{r['short_K2']}; "
              f"Sell {prefix}{exp}P{r['short_K2']}; "
              f"Buy {prefix}{exp}P{r['short_K1']}")
    return [mn, f"[{prefix}]",
            r['short_K1'], r['short_K2'], r['dte'],
            f"{r['short_credit']:.2f}", f"{r['short_margin']:.2f}",
            f"{r['short_ret']*100:.2f}%", f"{r['short_ann']*100:.2f}%",
            action]

def write_csvs(near_best, mid_best, short_best, date_str, out_dir):
    """Write 3 CSV files."""
    all_mins = sorted(set(near_best) | set(mid_best) | set(short_best))

    def to_df(best_dict, row_fn, header, empty_row):
        rows = []
        for mn in all_mins:
            if mn in best_dict:
                rows.append(row_fn(mn, best_dict[mn]))
            else:
                rows.append([mn] + empty_row)
        return pd.DataFrame(rows, columns=header)

    long_empty  = [''] * (len(LONG_HEADER)  - 1)
    short_empty = [''] * (len(SHORT_HEADER) - 1)

    df_near  = to_df(near_best,  _long_row,  LONG_HEADER,  long_empty)
    df_mid   = to_df(mid_best,   _long_row,  LONG_HEADER,  long_empty)
    df_short = to_df(short_best, _short_row, SHORT_HEADER, short_empty)

    paths = {
        'near': os.path.join(out_dir, f'near-long-{date_str}.csv'),
        'mid':  os.path.join(out_dir, f'mid-long-{date_str}.csv'),
        'short':os.path.join(out_dir, f'short-{date_str}.csv'),
    }
    dfs = {'near': df_near, 'mid': df_mid, 'short': df_short}
    for k, p in paths.items():
        dfs[k].to_csv(p, index=False)
        print(f"Written: {p}  ({len(dfs[k])} rows)")


# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python boxx.py <data-deep/YYYY-MM-DD> [output_dir]")
        sys.exit(1)
    date_dir = sys.argv[1]
    out_dir  = sys.argv[2] if len(sys.argv) > 2 else '.'
    run_scanner(date_dir, out_dir)

