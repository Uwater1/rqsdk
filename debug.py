import pandas as pd
import numpy as np
import math
from tp2_analysis import load_price_data_for_day, parse_ticker

v = pd.read_csv('tp2_violations_IO_2026-03-24.csv')
p = load_price_data_for_day('data-deep/2026-03-24', 'IO')
np_p = load_price_data_for_day('data-deep/2026-03-25', 'IO')

print(f"violations: {len(v)}")
print(f"price cols: {len(p.columns)}, next price cols: {len(np_p.columns)}")
print(f"next price first: {np_p.index[0]}, last: {np_p.index[-1]}")

row = v.iloc[0]
l1b, l2b = row['leg1_buy'], row['leg2_buy']
l1s, l2s = row['leg1_sell'], row['leg2_sell']

print(f"legs: {l1b}, {l2b}, {l1s}, {l2s}")

next_columns = np_p.columns.tolist()
next_col_idx = {col: i for i, col in enumerate(next_columns)}

nc_a11 = next_col_idx.get(f'{l1b}_ask', -1); nc_b11 = next_col_idx.get(f'{l1b}_bid', -1)
nc_a22 = next_col_idx.get(f'{l2b}_ask', -1); nc_b22 = next_col_idx.get(f'{l2b}_bid', -1)
nc_a12 = next_col_idx.get(f'{l1s}_ask', -1); nc_b12 = next_col_idx.get(f'{l1s}_bid', -1)
nc_a21 = next_col_idx.get(f'{l2s}_ask', -1); nc_b21 = next_col_idx.get(f'{l2s}_bid', -1)

print("indices:", nc_a11, nc_b11, nc_a22, nc_b22, nc_a12, nc_b12, nc_a21, nc_b21)

next_day_date = np_p.index[0].normalize()
t_next_session_end = next_day_date + pd.Timedelta(hours=14, minutes=55)
print("t_next_session_end:", t_next_session_end)

idx = np_p.index.get_indexer([t_next_session_end], method='pad')[0]
print("idx:", idx, "at time:", np_p.index[idx] if idx != -1 else "N/A")

if idx != -1:
    b11 = np_p.values[idx, nc_b11]
    b22 = np_p.values[idx, nc_b22]
    a12 = np_p.values[idx, nc_a12]
    a21 = np_p.values[idx, nc_a21]
    print(f"b11: {b11}, b22: {b22}, a12: {a12}, a21: {a21}")
