import pandas as pd
import numpy as np
import argparse
import os
from datetime import datetime, timedelta
from numba_utils import calculate_research_metrics_numba

# Constants for RMB calculation
MULTIPLIER = 10000
COMMISSION = 2.0  # Per contract

# Global paths
PATH_PARQUET = "synthetic_options_300ETF.parquet"
ETF_NAME = "300ETF"

def select_etf(choice):
    global ETF_NAME, PATH_PARQUET
    if choice == "50":
        ETF_NAME = "50ETF"
        PATH_PARQUET = "synthetic_options_50ETF.parquet"
    elif choice == "500":
        ETF_NAME = "500ETF"
        PATH_PARQUET = "synthetic_options_500ETF.parquet"
    else:
        ETF_NAME = "300ETF"
        PATH_PARQUET = "synthetic_options_300ETF.parquet"

def load_data():
    if not os.path.exists(PATH_PARQUET):
        print(f"Error: {PATH_PARQUET} not found.")
        return None
    
    df = pd.read_parquet(PATH_PARQUET)
    df["Date"] = pd.to_datetime(df["Date"])
    
    # Standardize column name
    if 'Target Expiry' in df.columns:
        df["Target Expiry"] = pd.to_datetime(df["Target Expiry"])
    elif 'Maturity' in df.columns:
        df["Target Expiry"] = pd.to_datetime(df["Maturity"])

    if 'Underlying Price at Date' not in df.columns and 'Underlying_Price' in df.columns:
        df['Underlying Price at Date'] = df['Underlying_Price']
        
    return df

def analyze_synthetic_otm(years=None):
    print(f"Analyzing {ETF_NAME} (Synthetic - Numba Accelerated)...")
    df = load_data()
    if df is None:
        return

    if years:
        latest_date = df["Date"].max()
        start_date = latest_date - pd.Timedelta(days=years * 365)
        df = df[df["Date"] >= start_date].copy()
        print(f"Filtering for data after: {start_date.date()}")

    # Prepare for Numba
    # 1. Sort by Option Type, then Date, then Strike to ensure group continuity
    df = df.sort_values(['Option Type', 'Date', 'Strike']).reset_index(drop=True)
    
    results_data = []

    for option_type in ["C", "P"]:
        mask = df["Option Type"] == option_type
        sub_df = df[mask].reset_index(drop=True)
        if sub_df.empty: continue
        
        # Find boundaries where Date changes
        dates = sub_df['Date'].values
        diff = np.where(dates[1:] != dates[:-1])[0] + 1
        boundaries = np.zeros(len(diff) + 2, dtype=np.int64)
        boundaries[0] = 0
        boundaries[1:-1] = diff
        boundaries[-1] = len(sub_df)
        
        # Prepare filter mask per group (Date) - No filter for this script
        group_filter_mask = np.ones(len(boundaries) - 1, dtype=bool)
        
        # Prepare arrays for Numba
        strikes = sub_df["Strike"].values.astype(np.float64)
        s0s = sub_df["Underlying Price at Date"].values.astype(np.float64)
        prices = sub_df["Price"].values.astype(np.float64)
        worthless = sub_df["Expire_worthless"].values.astype(np.int8)
        
        if option_type == "C":
            ret_val = sub_df["Exp Ret Short"].values.astype(np.float64)
            is_call = True
        else:
            ret_val = sub_df["Exp Ret Long"].values.astype(np.float64)
            is_call = False
            
        # Execute Numba core aggregation
        # metrics_p: passed, metrics_f: filtered
        metrics_p, metrics_f = calculate_research_metrics_numba(
            strikes, s0s, ret_val, prices, worthless, boundaries, is_call, group_filter_mask
        )
        
        for lv in range(6):
            count = metrics_p[lv, 0]
            if count == 0: continue
            
            pnl_sum = metrics_p[lv, 1]
            wins = metrics_p[lv, 2]
            total_wins = metrics_p[lv, 3]
            min_pnl = metrics_p[lv, 4]
            
            winrate = wins / count
            total_winrate = total_wins / count
            expected_return = pnl_sum / count
            
            results_data.append({
                "Option Type": "Short Call" if option_type == "C" else "Long Put",
                "OTM Level": lv,
                "Samples": int(count),
                "Winrate": f"{winrate:.2%}",
                "Expire Worthless Rate": f"{total_winrate:.2%}",
                "Expected Return (RMB)": round(expected_return, 2),
                "Max Loss (RMB)": round(min_pnl, 2)
            })
            
    if not results_data:
        print("No valid data found for analysis.")
        return

    df_res = pd.DataFrame(results_data)
    
    title = f"ALPHA RESEARCH (SYNTHETIC): OTM OPTIONS ({ETF_NAME}) (0 = ATM)"
    if years:
        title += f" - Last {years} Years"
        
    print("\n" + "="*95)
    print(" " * ((95 - len(title)) // 2) + title)
    print("="*95)
    print(df_res.to_string(index=False))
    print("="*95)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Research Synthetic OTM Alpha (Short Call & Long Put).")
    parser.add_argument("-t", "--years", type=int, help="Limit analysis to last N years")
    parser.add_argument("-e", "--etf", type=str, choices=["50", "300", "500"], default="300", help="ETF choice (default: 300)")
    args = parser.parse_args()
    
    select_etf(args.etf)
    analyze_synthetic_otm(years=args.years)
