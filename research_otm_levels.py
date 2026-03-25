import pandas as pd
import numpy as np
import pandas_ta as ta
import argparse
from datetime import datetime, timedelta
import os

# Constants matching backtest_covered_call.py
SPREAD_HALF    = 0.02
COMMISSION     = 2.0

# Global paths that will be updated by select_etf
ETF_NAME = "300ETF"
PATH_INST = "data/300ETF_instruments.parquet"
PATH_OPT  = "data/300ETF_historical_prices.parquet"
PATH_ETF  = "data/510300_1d.parquet"

def select_etf(choice):
    global ETF_NAME, PATH_INST, PATH_OPT, PATH_ETF
    if choice == "50":
        ETF_NAME = "50ETF"
        PATH_INST = "data/50ETF_instruments.parquet"
        PATH_OPT  = "data/50ETF_historical_prices.parquet"
        PATH_ETF  = "data/50ETF_1d.parquet"
    elif choice == "500":
        ETF_NAME = "500ETF"
        PATH_INST = "data/500ETF_instruments.parquet"
        PATH_OPT  = "data/500ETF_historical_prices.parquet"
        PATH_ETF  = "data/500ETF_1d.parquet"
    else:
        # Default 300
        ETF_NAME = "300ETF"
        PATH_INST = "data/300ETF_instruments.parquet"
        PATH_OPT  = "data/300ETF_historical_prices.parquet"
        PATH_ETF  = "data/510300_1d.parquet"

def load_data():
    inst = pd.read_parquet(PATH_INST)
    opt  = pd.read_parquet(PATH_OPT)
    etf  = pd.read_parquet(PATH_ETF)

    inst["maturity_date"] = pd.to_datetime(inst["maturity_date"])
    opt["date"]           = pd.to_datetime(opt["date"])
    etf["date"]           = pd.to_datetime(etf["date"])

    inst = inst[["order_book_id", "strike_price", "maturity_date",
                 "option_type", "contract_multiplier"]].copy()

    opt = opt.merge(inst, on="order_book_id", how="left", suffixes=("_raw", ""))
    for col in ["strike_price", "contract_multiplier"]:
        raw = col + "_raw"
        if raw in opt.columns:
            opt[col] = opt[col].fillna(opt[raw])
            opt.drop(columns=[raw], inplace=True)

    etf = etf.set_index("date").sort_index()
    return inst, opt, etf

def get_cycles(opt, etf, years=None):
    trading_days_set = set(etf.index.normalize())
    opt_trading_days = sorted(opt["date"].unique())

    expiries_cp = (
        opt.groupby(["maturity_date", "option_type"])["order_book_id"]
        .nunique()
        .unstack("option_type")
        .dropna()
        .index.tolist()
    )
    expiries_cp = sorted(expiries_cp)

    cycles = []
    
    start_date = None
    if years:
        latest_date = max(opt_trading_days)
        start_date = latest_date - timedelta(days=years * 365)
        print(f"Filtering for cycles starting after: {start_date.date()}")

    for i, expiry in enumerate(expiries_cp):
        if i == 0:
            entry = opt_trading_days[0]
        else:
            prev_expiry = expiries_cp[i - 1]
            candidates = [d for d in opt_trading_days if d > prev_expiry]
            if not candidates:
                continue
            entry = candidates[0]

        if entry >= expiry:
            continue
            
        if start_date and entry < start_date:
            continue

        entry_norm = pd.Timestamp(entry).normalize()
        if entry_norm not in trading_days_set:
            continue

        cycles.append({"entry_date": entry, "expiry_date": expiry})

    return cycles

def get_otm_strikes(opt, etf, entry_date, expiry_date, option_type, offsets):
    etf_close = float(etf.loc[entry_date.normalize(), "close"])

    day_opt = opt[
        (opt["date"] == entry_date) &
        (opt["maturity_date"] == expiry_date) &
        (opt["option_type"] == option_type) &
        (opt["close"] > 0)
    ].copy()

    if day_opt.empty:
        return [None] * len(offsets)

    if option_type == "C":
        # OTM: strike > spot
        otm = day_opt[day_opt["strike_price"] > etf_close].sort_values("strike_price")
        # ITM: strike <= spot (closest to spot first)
        itm = day_opt[day_opt["strike_price"] <= etf_close].sort_values("strike_price", ascending=False)
    else:
        # OTM: strike < spot
        otm = day_opt[day_opt["strike_price"] < etf_close].sort_values("strike_price", ascending=False)
        # ITM: strike >= spot (closest to spot first)
        itm = day_opt[day_opt["strike_price"] >= etf_close].sort_values("strike_price", ascending=True)

    results = []
    for off in offsets:
        if off == 0:
            if len(itm) > 0:
                results.append(itm.iloc[0].to_dict())
            else:
                results.append(None)
        else:
            idx = off - 1
            if idx < len(otm):
                results.append(otm.iloc[idx].to_dict())
            else:
                results.append(None)
    return results

def filter_cycle(etf, entry_date):
    """
    User-defined filter for trading cycles. 
    Return True to include the cycle, False to skip.

    Using Combined Filter c2: f1 (SMA20) OR f3 (RSI Overbought)
    Returns True if Close < 20-day SMA OR 14-day RSI < 70
    """
    idx = entry_date.normalize()
    if idx not in etf.index:
        return False

    # Indicators should be pre-calculated on the 'etf' DataFrame for performance.
    # Handle NaNs at the start of the series.
    sma20 = etf.loc[idx, "sma20"]
    rsi14 = etf.loc[idx, "rsi14"]

    if pd.isna(sma20) or pd.isna(rsi14):
        return False # Not enough data to apply filter, skip cycle

    cond1 = etf.loc[idx, "close"] < sma20
    cond2 = rsi14 < 70

    return cond1 or cond2

def analyze_otm_levels(years=None):
    print(f"Analyzing {ETF_NAME}...")
    print("Loading data...")
    inst, opt, etf = load_data()
    cycles = get_cycles(opt, etf, years=years)
    print(f"Found {len(cycles)} cycles.")
    
    levels = [0, 1, 2, 3, 4, 5]
    results_data = []

    for option_type in ["C", "P"]:
        level_metrics = {level: {"wins": 0, "total_wins": 0, "pnls": [], "count": 0} for level in levels}
        
        for cyc in cycles:
            entry = cyc["entry_date"]
            expiry = cyc["expiry_date"]
            
            if not filter_cycle(etf, entry):
                continue
            
            etf_expiry_dates = etf.index[etf.index <= expiry]
            if etf_expiry_dates.empty:
                continue
            etf_settle = float(etf.loc[etf_expiry_dates[-1], "close"])

            legs = get_otm_strikes(opt, etf, entry, expiry, option_type, levels)
            
            for i, leg in enumerate(legs):
                level = levels[i]
                if leg is None:
                    continue
                
                K = float(leg["strike_price"])
                mult = float(leg["contract_multiplier"])
                entry_mid = float(leg["close"])
                
                exec_px = entry_mid * (1 - SPREAD_HALF)
                premium_received_rmb = exec_px * mult
                
                intrinsic = 0.0
                if option_type == "C":
                    if etf_settle > K:
                        intrinsic = etf_settle - K
                else:
                    if etf_settle < K:
                        intrinsic = K - etf_settle
                        
                exercise_pnl_rmb = -intrinsic * mult
                net_rmb = premium_received_rmb + exercise_pnl_rmb - COMMISSION
                
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
                "Option Type": "Call" if option_type == "C" else "Put",
                "OTM Level": level,
                "Cycles": count,
                "Winrate": f"{winrate:.2%}",
                "Expire Worthless Rate": f"{total_winrate:.2%}",
                "Expected Return (RMB)": round(expected_return, 2),
                "Max Loss (RMB)": round(max_loss, 2)
            })
            
    df = pd.DataFrame(results_data)
    
    title = f"ALPHA RESEARCH: OTM OPTIONS ({ETF_NAME}) (0 = ATM) - {'Last ' + str(years) + ' Years' if years else 'Full History'}"
    print("\n" + "="*95)
    print(" " * ((95 - len(title)) // 2) + title)
    print("="*95)
    print(df.to_string(index=False))
    print("="*95)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Research OTM Alpha for each level of options.")
    parser.add_argument("-t", "--years", type=int, help="Limit analysis to the last N years (default: all)")
    parser.add_argument("-e", "--etf", type=str, choices=["50", "300", "500"], default="300", help="ETF choice: 50, 300, or 500 (default: 300)")
    args = parser.parse_args()
    
    select_etf(args.etf)
    analyze_otm_levels(years=args.years)
