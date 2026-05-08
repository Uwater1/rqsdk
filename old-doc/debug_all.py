import pandas as pd
import numpy as np
from tp2_analysis import load_price_data_for_day

v = pd.read_csv('tp2_violations_IO_2026-03-24.csv')
v = v[v['score'] >= 1.0]

np_p = load_price_data_for_day('data-deep/2026-03-25', 'IO')
next_timestamps = np_p.index
next_price_mat = np_p.values
next_columns = np_p.columns.tolist()
next_col_idx = {col: i for i, col in enumerate(next_columns)}

valid_count = 0
nan_count = 0
good_count = 0
for i, row in v.iterrows():
    l1b, l2b = row['leg1_buy'], row['leg2_buy']
    l1s, l2s = row['leg1_sell'], row['leg2_sell']

    nc_a11 = next_col_idx.get(f'{l1b}_ask', -1); nc_b11 = next_col_idx.get(f'{l1b}_bid', -1)
    nc_a22 = next_col_idx.get(f'{l2b}_ask', -1); nc_b22 = next_col_idx.get(f'{l2b}_bid', -1)
    nc_a12 = next_col_idx.get(f'{l1s}_ask', -1); nc_b12 = next_col_idx.get(f'{l1s}_bid', -1)
    nc_a21 = next_col_idx.get(f'{l2s}_ask', -1); nc_b21 = next_col_idx.get(f'{l2s}_bid', -1)

    if -1 not in [nc_a11, nc_b11, nc_a22, nc_b22, nc_a12, nc_b12, nc_a21, nc_b21]:
        valid_count += 1
        
        idx = next_timestamps.get_indexer([next_timestamps[0].normalize() + pd.Timedelta(hours=14, minutes=55)], method='pad')[0]
        if idx != -1:
            b11 = next_price_mat[idx, nc_b11]
            b22 = next_price_mat[idx, nc_b22]
            a12 = next_price_mat[idx, nc_a12]
            a21 = next_price_mat[idx, nc_a21]
            import math
            if any(math.isnan(val) or val<=0 for val in [b11,b22,a12,a21]):
                nan_count += 1
            else:
                good_count += 1

print(f"Total violations: {len(v)}, Valid: {valid_count}, nan: {nan_count}, good: {good_count}")

