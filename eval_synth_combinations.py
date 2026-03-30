import pandas as pd
import numpy as np
import pandas_ta as ta
import os
from numba_utils import calculate_research_metrics_numba

PATH_PARQUET = "synthetic_options_300ETF.parquet"
PATH_ETF = "data/510300_1d.parquet"

def load_data():
    df = pd.read_parquet(PATH_PARQUET)
    df["Date"] = pd.to_datetime(df["Date"])
    if 'Underlying Price at Date' not in df.columns and 'Underlying_Price' in df.columns:
        df['Underlying Price at Date'] = df['Underlying_Price']

    etf = pd.read_parquet(PATH_ETF)
    etf["date"] = pd.to_datetime(etf["date"])
    etf = etf.set_index("date").sort_index()

    # Needs entire ETF history for smoothing warmth
    etf['sma20'] = ta.sma(etf['close'], length=20)
    etf['ema20'] = ta.ema(etf['close'], length=20)
    etf['rsi14'] = ta.rsi(etf['close'], length=14)
    macd = ta.macd(etf['close'])
    if macd is not None:
        etf['macd_hist'] = macd.iloc[:, 1]
    bbands = ta.bbands(etf['close'], length=20, std=2)
    if bbands is not None:
        etf['bb_upper'] = bbands.iloc[:, 2]
    etf['roc20'] = ta.roc(etf['close'], length=20)
    etf['atr20'] = ta.atr(etf['high'], etf['low'], etf['close'], length=20)
    adx = ta.adx(etf['high'], etf['low'], etf['close'], length=14)
    if adx is not None:
        etf['adx14'] = adx.iloc[:, 0]
    etf['ema10'] = ta.ema(etf['close'], length=10)
    etf['ema30'] = ta.ema(etf['close'], length=30)
    stoch = ta.stoch(etf['high'], etf['low'], etf['close'], k=14, d=3, smooth_k=3)
    if stoch is not None:
        etf['stoch_k'] = stoch.iloc[:, 0]
    etf['rolling_high_20'] = etf['close'].rolling(20).max()
    etf['rolling_high_252'] = etf['close'].rolling(252).max()

    df = df.merge(etf, left_on="Date", right_index=True, how="left")

    # Pre-sort for numba
    df = df.sort_values(['Option Type', 'Date', 'Strike']).reset_index(drop=True)
    return df

df = load_data()

f1 = df['close'] < df['sma20']
f2 = df['close'] < df['ema20']
f3 = df['rsi14'] < 70
f4 = df['rsi14'] > 30
f5 = df['macd_hist'] < 0
f6 = df['close'] < df['bb_upper']
f9 = df['roc20'] < 5.0
f10 = df['close'] < (df['sma20'] + df['atr20'])
f11 = df['adx14'] < 25
f12 = df['ema10'] < df['ema30']
f15 = df['stoch_k'] < 80
f16 = df['close'] < (0.98 * df['rolling_high_20'])
f17 = df['close'] < (0.95 * df['rolling_high_252'])
f20 = df['close'] < (df['ema20'] + 1.0 * df['atr20'])

combinations = {
    "c1": f1 & f3,
    "c2": f1 | f3,
    "c3": f11 & f12,
    "c4": f11 | f12,
    "c5": f16 & f15,
    "c6": f17 & f12,
    "c7": f20 & f4,
    "c8": f9 & f10,
    "c9": f12 & f16,
    "c10": f11 & f10,
    "c11": f6 & f9,
    "c12": f5 & f16,
    "c13": f12 & f20,
    "c14": f11 & f20,
    "c15": f16 & f20,
    "c16": f3 & f10,
    "c17": f11 & f12 & f16,
    "c18": f11 | (f12 & f16),
    "c19": f20 & f4 & f3,
    "c20": f12 & f16 & f20,
    "c21": (f1 | f11) & f3,
    "c22": f12 | (f16 & f20),
    "c23": (f1 | f2) & f16,
    "f20 AND f6": f20 & f6,
    "f3 AND f6": f3 & f6,
    "f12 OR (f3 AND f6)": f12 | (f3 & f6),
    "f3 AND f4 AND f6": f3 & f4 & f6,
    "f4 AND f6": f4 & f6,
    "f3 AND f20 AND f6": f3 & f20 & f6,
    "baseline": pd.Series(True, index=df.index)
}

results = []

for c_name, f_mask in combinations.items():
    df["Pass Filter"] = f_mask.fillna(True)

    sub_df = df[df["Option Type"] == "C"].reset_index(drop=True)

    dates = sub_df['Date'].values
    diff = np.where(dates[1:] != dates[:-1])[0] + 1
    boundaries = np.zeros(len(diff) + 2, dtype=np.int64)
    boundaries[0] = 0
    boundaries[1:-1] = diff
    boundaries[-1] = len(sub_df)

    group_filter_mask = np.zeros(len(boundaries) - 1, dtype=bool)
    for g in range(len(boundaries) - 1):
        group_filter_mask[g] = sub_df["Pass Filter"].values[boundaries[g]]

    strikes = sub_df["Strike"].values.astype(np.float64)
    s0s = sub_df["Underlying Price at Date"].values.astype(np.float64)
    prices = sub_df["Price"].values.astype(np.float64)
    worthless = sub_df["Expire_worthless"].values.astype(np.int8)
    ret_val = sub_df["Exp Ret Short"].values.astype(np.float64)

    metrics_p, metrics_f = calculate_research_metrics_numba(
        strikes, s0s, ret_val, prices, worthless, boundaries, True, group_filter_mask
    )

    total_passed = 0
    total_filtered = 0
    total_er_passed = 0
    total_er_filtered = 0
    min_ml = 9999999

    for lv in range(6):
        count_p = metrics_p[lv, 0]
        pnl_sum_p = metrics_p[lv, 1]
        ml_p = metrics_p[lv, 4]

        count_f = metrics_f[lv, 0]
        pnl_sum_f = metrics_f[lv, 1]

        if count_p > 0:
            total_passed += count_p
            total_er_passed += pnl_sum_p
            if ml_p < min_ml:
                min_ml = ml_p

        if count_f > 0:
            total_filtered += count_f
            total_er_filtered += pnl_sum_f

    avg_er_passed = total_er_passed / total_passed if total_passed > 0 else 0
    avg_er_filtered = total_er_filtered / total_filtered if total_filtered > 0 else 0
    placement_rate = total_passed / (total_passed + total_filtered) if (total_passed + total_filtered) > 0 else 0

    results.append({
        "Filter": c_name,
        "Placement Rate": placement_rate,
        "Max Loss": min_ml if min_ml != 9999999 else 0,
        "Avg ER (Passed)": avg_er_passed,
        "Avg ER (Filtered)": avg_er_filtered
    })

res_df = pd.DataFrame(results)
print(res_df.to_string())

# Score and rank combinations to write to file
best_filters = []
for res in results:
    if res["Filter"] == "baseline":
        continue
    pr = res["Placement Rate"]
    er_p = res["Avg ER (Passed)"]
    er_f = res["Avg ER (Filtered)"]
    ml = res["Max Loss"]

    if pr >= 0.70 and er_f < 1000:
        score = pr * er_p + ml / 100 - er_f
        best_filters.append({
            "Name": res["Filter"],
            "Placement Rate": f"{pr:.2%}",
            "Avg EV (Included)": f"{er_p:.2f}",
            "Avg EV (Filtered Out)": f"{er_f:.2f}",
            "Avg Max Loss": f"{ml:.2f}",
            "Score": score
        })

best_filters.sort(key=lambda x: x["Score"], reverse=True)

with open("filter_syntetic.txt", "w") as f:
    f.write("Top 5 Combinations based on synthetic data evaluation:\n\n")
    for i, bf in enumerate(best_filters[:5]):
        f.write(f"Rank {i+1}: Combination {bf['Name']}\n")
        f.write(f"  - Placement Rate: {bf['Placement Rate']}\n")
        f.write(f"  - Avg EV (Included): {bf['Avg EV (Included)']} RMB\n")
        f.write(f"  - Avg EV (Filtered Out): {bf['Avg EV (Filtered Out)']} RMB\n")
        f.write(f"  - Avg Max Loss: {bf['Avg Max Loss']} RMB\n\n")
