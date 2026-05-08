import pandas as pd
import numpy as np
import pandas_ta as ta
import argparse
from datetime import datetime, timedelta
import os

# Import original functions
import research_otm_levels as r_otm

r_otm.select_etf("300")
inst, opt, etf = r_otm.load_data()
cycles = r_otm.get_cycles(opt, etf, years=None)

# Pre-calculate indicators for all filters
etf['sma20'] = ta.sma(etf['close'], length=20)
etf['ema20'] = ta.ema(etf['close'], length=20)
etf['rsi14'] = ta.rsi(etf['close'], length=14)
macd = ta.macd(etf['close'])
if macd is not None:
    etf['macd_hist'] = macd.iloc[:, 1] # MACDh_12_26_9
else:
    etf['macd_hist'] = np.nan
bbands = ta.bbands(etf['close'], length=20, std=2)
if bbands is not None:
    etf['bb_upper'] = bbands.iloc[:, 2] # BBU_20_2.0
else:
    etf['bb_upper'] = np.nan
etf['roc20'] = ta.roc(etf['close'], length=20)
atr = ta.atr(etf['high'], etf['low'], etf['close'], length=20)
etf['atr20'] = atr
adx = ta.adx(etf['high'], etf['low'], etf['close'], length=14)
if adx is not None:
    etf['adx14'] = adx.iloc[:, 0] # ADX_14
else:
    etf['adx14'] = np.nan
etf['ema10'] = ta.ema(etf['close'], length=10)
etf['ema30'] = ta.ema(etf['close'], length=30)
stoch = ta.stoch(etf['high'], etf['low'], etf['close'], k=14, d=3, smooth_k=3)
if stoch is not None:
    etf['stoch_k'] = stoch.iloc[:, 0] # STOCHk_14_3_3
else:
    etf['stoch_k'] = np.nan
etf['rolling_high_20'] = etf['close'].rolling(20).max()
etf['rolling_high_252'] = etf['close'].rolling(252).max()

# Define the 12 working filters based on filter.txt
def f1_sma20(etf, entry_date):
    idx = entry_date.normalize()
    if idx not in etf.index: return False
    return etf.loc[idx, 'close'] < etf.loc[idx, 'sma20']

def f2_ema20(etf, entry_date):
    idx = entry_date.normalize()
    if idx not in etf.index: return False
    return etf.loc[idx, 'close'] < etf.loc[idx, 'ema20']

def f3_rsi_overbought(etf, entry_date):
    idx = entry_date.normalize()
    if idx not in etf.index: return False
    return etf.loc[idx, 'rsi14'] < 70

def f4_rsi_oversold(etf, entry_date):
    idx = entry_date.normalize()
    if idx not in etf.index: return False
    return etf.loc[idx, 'rsi14'] > 30

def f5_macd(etf, entry_date):
    idx = entry_date.normalize()
    if idx not in etf.index: return False
    return etf.loc[idx, 'macd_hist'] < 0

def f6_bbands(etf, entry_date):
    idx = entry_date.normalize()
    if idx not in etf.index: return False
    return etf.loc[idx, 'close'] < etf.loc[idx, 'bb_upper']

# skipping f7 IVR and f8 HV because they are not standard pandas-ta

def f9_roc(etf, entry_date):
    idx = entry_date.normalize()
    if idx not in etf.index: return False
    return etf.loc[idx, 'roc20'] < 5.0 # percentage? pandas-ta roc is in %

def f10_atr_breakout(etf, entry_date):
    idx = entry_date.normalize()
    if idx not in etf.index: return False
    return etf.loc[idx, 'close'] < (etf.loc[idx, 'sma20'] + etf.loc[idx, 'atr20'])

def f11_adx(etf, entry_date):
    idx = entry_date.normalize()
    if idx not in etf.index: return False
    return etf.loc[idx, 'adx14'] < 25

def f12_ema_cross(etf, entry_date):
    idx = entry_date.normalize()
    if idx not in etf.index: return False
    return etf.loc[idx, 'ema10'] < etf.loc[idx, 'ema30']

def f15_stoch(etf, entry_date):
    idx = entry_date.normalize()
    if idx not in etf.index: return False
    return etf.loc[idx, 'stoch_k'] < 80

def f16_rolling_high_20(etf, entry_date):
    idx = entry_date.normalize()
    if idx not in etf.index: return False
    return etf.loc[idx, 'close'] < (0.98 * etf.loc[idx, 'rolling_high_20'])

def f17_rolling_high_252(etf, entry_date):
    idx = entry_date.normalize()
    if idx not in etf.index: return False
    return etf.loc[idx, 'close'] < (0.95 * etf.loc[idx, 'rolling_high_252'])

def f20_keltner(etf, entry_date):
    idx = entry_date.normalize()
    if idx not in etf.index: return False
    return etf.loc[idx, 'close'] < (etf.loc[idx, 'ema20'] + 1.0 * etf.loc[idx, 'atr20'])

# Combine filters logically
filters = {
    "f1": f1_sma20, "f2": f2_ema20, "f3": f3_rsi_overbought, "f4": f4_rsi_oversold,
    "f5": f5_macd, "f6": f6_bbands, "f9": f9_roc, "f10": f10_atr_breakout,
    "f11": f11_adx, "f12": f12_ema_cross, "f15": f15_stoch, "f16": f16_rolling_high_20,
    "f17": f17_rolling_high_252, "f20": f20_keltner
}

filter_descriptions = {
    "f1": "Close < 20-day SMA",
    "f2": "Close < 20-day EMA",
    "f3": "14-day RSI < 70",
    "f4": "14-day RSI > 30",
    "f5": "MACD Histogram < 0",
    "f6": "Close < Upper Bollinger Band (20, 2)",
    "f9": "20-day ROC < 5%",
    "f10": "Close < SMA20 + 1 * ATR(20)",
    "f11": "14-day ADX < 25",
    "f12": "EMA10 < EMA30",
    "f15": "14-day Stochastic %K < 80",
    "f16": "Close < 0.98 * max(close over last 20 days)",
    "f17": "Close < 0.95 * max(close over last 252 days)",
    "f20": "Close < EMA20 + 1.0 * ATR(20)",
}

combinations = [
    # 2-filter combos (Either/Or or AND)
    ("c1", lambda e, d: filters["f1"](e, d) and filters["f3"](e, d), "f1 AND f3"),
    ("c2", lambda e, d: filters["f1"](e, d) or filters["f3"](e, d), "f1 OR f3"),
    ("c3", lambda e, d: filters["f11"](e, d) and filters["f12"](e, d), "f11 AND f12"),
    ("c4", lambda e, d: filters["f11"](e, d) or filters["f12"](e, d), "f11 OR f12"),
    ("c5", lambda e, d: filters["f16"](e, d) and filters["f15"](e, d), "f16 AND f15"),
    ("c6", lambda e, d: filters["f17"](e, d) and filters["f12"](e, d), "f17 AND f12"),
    ("c7", lambda e, d: filters["f20"](e, d) and filters["f4"](e, d), "f20 AND f4"),
    ("c8", lambda e, d: filters["f9"](e, d) and filters["f10"](e, d), "f9 AND f10"),
    ("c9", lambda e, d: filters["f12"](e, d) and filters["f16"](e, d), "f12 AND f16"),
    ("c10", lambda e, d: filters["f11"](e, d) and filters["f10"](e, d), "f11 AND f10"),
    ("c11", lambda e, d: filters["f6"](e, d) and filters["f9"](e, d), "f6 AND f9"),
    ("c12", lambda e, d: filters["f5"](e, d) and filters["f16"](e, d), "f5 AND f16"),
    ("c13", lambda e, d: filters["f12"](e, d) and filters["f20"](e, d), "f12 AND f20"),
    ("c14", lambda e, d: filters["f11"](e, d) and filters["f20"](e, d), "f11 AND f20"),
    ("c15", lambda e, d: filters["f16"](e, d) and filters["f20"](e, d), "f16 AND f20"),
    ("c16", lambda e, d: filters["f3"](e, d) and filters["f10"](e, d), "f3 AND f10"),
    # 3-filter combos
    ("c17", lambda e, d: filters["f11"](e, d) and filters["f12"](e, d) and filters["f16"](e, d), "f11 AND f12 AND f16"),
    ("c18", lambda e, d: filters["f11"](e, d) or (filters["f12"](e, d) and filters["f16"](e, d)), "f11 OR (f12 AND f16)"),
    ("c19", lambda e, d: filters["f20"](e, d) and filters["f4"](e, d) and filters["f3"](e, d), "f20 AND f4 AND f3"),
    ("c20", lambda e, d: filters["f12"](e, d) and filters["f16"](e, d) and filters["f20"](e, d), "f12 AND f16 AND f20"),
    # Add a few more with relaxed ORs to get higher trade counts
    ("c21", lambda e, d: (filters["f1"](e, d) or filters["f11"](e, d)) and filters["f3"](e, d), "(f1 OR f11) AND f3"),
    ("c22", lambda e, d: filters["f12"](e, d) or (filters["f16"](e, d) and filters["f20"](e, d)), "f12 OR (f16 AND f20)"),
    ("c23", lambda e, d: (filters["f1"](e, d) or filters["f2"](e, d)) and filters["f16"](e, d), "(f1 OR f2) AND f16"),
]

def run_backtest_with_filter(filter_func):
    levels = [0, 1, 2, 3, 4, 5]
    results_data = []

    for option_type in ["C"]: # Only testing Call for simplicity/speed as per filter.txt focuses on Calls
        level_metrics = {level: {"wins": 0, "total_wins": 0, "pnls": [], "count": 0} for level in levels}

        for cyc in cycles:
            entry = cyc["entry_date"]
            expiry = cyc["expiry_date"]

            try:
                if not filter_func(etf, entry):
                    continue
            except Exception as e:
                print(f"Error evaluating filter for entry date {entry}: {e}")
                continue

            etf_expiry_dates = etf.index[etf.index <= expiry]
            if etf_expiry_dates.empty:
                continue
            etf_settle = float(etf.loc[etf_expiry_dates[-1], "close"])

            legs = r_otm.get_otm_strikes(opt, etf, entry, expiry, option_type, levels)

            for i, leg in enumerate(legs):
                level = levels[i]
                if leg is None:
                    continue

                K = float(leg["strike_price"])
                mult = float(leg["contract_multiplier"])
                entry_mid = float(leg["close"])

                exec_px = entry_mid * (1 - r_otm.SPREAD_HALF)
                premium_received_rmb = exec_px * mult

                intrinsic = 0.0
                if etf_settle > K:
                    intrinsic = etf_settle - K

                exercise_pnl_rmb = -intrinsic * mult
                net_rmb = premium_received_rmb + exercise_pnl_rmb - r_otm.COMMISSION

                level_metrics[level]["count"] += 1
                level_metrics[level]["pnls"].append(net_rmb)

                if net_rmb > 0:
                    level_metrics[level]["wins"] += 1

                if intrinsic == 0.0:
                    level_metrics[level]["total_wins"] += 1

        for level in levels:
            metrics = level_metrics[level]
            count = metrics["count"]
            if count == 0:
                continue

            winrate = metrics["wins"] / count
            total_winrate = metrics["total_wins"] / count
            expected_return = np.mean(metrics["pnls"])
            max_loss = np.min(metrics["pnls"])

            results_data.append({
                "Option Type": "Call",
                "OTM Level": level,
                "Cycles": count,
                "Winrate": winrate,
                "Expected Return": expected_return,
                "Max Loss": max_loss
            })

    df = pd.DataFrame(results_data)
    return df

all_results = []
for name, func, desc in combinations:
    print(f"Testing {name}: {desc}...")
    df = run_backtest_with_filter(func)
    if not df.empty:
        # Aggregate score across levels
        avg_cycles = df['Cycles'].mean()
        avg_winrate = df['Winrate'].mean()
        avg_er = df['Expected Return'].mean()
        avg_ml = df['Max Loss'].mean()
        total_annual_return = avg_er * avg_cycles / (len(cycles) / 12) # Approximation, assume ~1 cycle per month

        # Score it (we want 70% placement, which is 0.7 * 75 = 52.5 cycles)
        if avg_cycles >= 50: # MIN_AVG_CYCLES_FOR_SCORING
            score = (avg_winrate * 1000) + avg_er + (total_annual_return * 0.1) # Arbitrary scoring
            all_results.append({
                "Name": name,
                "Description": desc,
                "Score": score,
                "Avg Cycles": avg_cycles,
                "Avg Winrate": avg_winrate,
                "Avg Expected Return": avg_er,
                "Avg Max Loss": avg_ml,
                "Total Annual Return Approx": total_annual_return,
                "Raw_DF": df
            })

all_results.sort(key=lambda x: x["Score"], reverse=True)

print("\n--- TOP 5 COMBINATIONS ---")
for i, res in enumerate(all_results[:5]):
    print(f"Rank {i+1}: {res['Name']} ({res['Description']})")
    print(f"Score: {res['Score']:.2f}, Cycles: {res['Avg Cycles']:.1f}, Winrate: {res['Avg Winrate']:.2%}, ER: {res['Avg Expected Return']:.2f}, ML: {res['Avg Max Loss']:.2f}")

    # Write logs
    log_content = f"Combination Rank {i+1}: {res['Name']}\n"
    log_content += f"Filters: {res['Description']}\n"

    # Expand description mapping, sort by length descending to prevent partial replacements (e.g. f1 replacing f11)
    desc_expanded = res['Description']
    for k, v in sorted(filter_descriptions.items(), key=lambda item: len(item[0]), reverse=True):
        desc_expanded = desc_expanded.replace(k, f"({v})")
    log_content += f"Expanded logic: {desc_expanded}\n\n"

    log_content += f"Average Cycles Traded: {res['Avg Cycles']:.1f} / 75 ({(res['Avg Cycles']/75):.2%})\n"
    log_content += f"Average Winrate: {res['Avg Winrate']:.2%}\n"
    log_content += f"Average Expected Return: {res['Avg Expected Return']:.2f} RMB\n"
    log_content += f"Average Max Loss: {res['Avg Max Loss']:.2f} RMB\n"
    log_content += f"Total Annual Return Approximation: {res['Total Annual Return Approx']:.2f}\n\n"

    log_content += "--- Level Breakdown ---\n"

    # Format the dataframe similar to original script output
    df = res['Raw_DF']
    df_formatted = df.copy()
    df_formatted['Winrate'] = df_formatted['Winrate'].apply(lambda x: f"{x:.2%}")
    df_formatted['Expected Return'] = df_formatted['Expected Return'].round(2)
    df_formatted['Max Loss'] = df_formatted['Max Loss'].round(2)

    log_content += df_formatted.to_string(index=False)

    with open(f"filter2_{i+1}.log", "w") as f:
        f.write(log_content)

print("\nSaved top 5 combinations to filter2_1.log ... filter2_5.log")
