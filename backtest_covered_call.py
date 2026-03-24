"""
备兑期权 Backtest — Covered Call + Bull Put Spread on 300ETF (510300.XSHG)
=========================================================================
Assumptions:
  - Spread: options only — buy at close*1.02 (ask), sell at close*0.98 (bid)
  - Commission: 5 RMB per option leg (open or close)
  - Exercise cost: 2 RMB if WE exercise (buyer); 0 RMB if assigned (seller)
  - Always hold to last trading day of the contract; exercise at ETF close price
  - ETF stock: no spread, no commission
  - Strike selection (OTM offset 3 or 4) driven by ATM IV of the cycle contract:
      IV > IV_THRESHOLD  → use offset 4 (further OTM)
      IV ≤ IV_THRESHOLD  → use offset 3 (closer OTM)
"""

# ── Imports ──────────────────────────────────────────────────────────────────
import math
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from numba import njit
import os
import sys

# ── Constants ────────────────────────────────────────────────────────────────
SPREAD_HALF    = 0.02        # ±2% → bid = mid*0.98, ask = mid*1.02
COMMISSION     = 2.0         # RMB per option leg, muti legs are cheaper, so on averge set 2
EXERCISE_COST  = 0.6         # RMB when WE exercise as buyer
ETF_SHARES     = 20_000      # equity leg (no cost modelled here)
RISK_FREE      = 0.02        # annual risk-free rate for BS IV
IVR_HIGH       = 0.50        # IVR above this → go further OTM (offset 5)
IVR_LOW        = 0.10        # IVR below this → go closer OTM (offset 3)
IV_THRESHOLD   = 0.20        # Fallback ATM IV if calculation fails
MIN_PUT_CREDIT = 5.0         # Minimum expected net credit (RMB) for put spread per contract
# ── Underlying Config (Dynamic based on CLI) ───────────────────────────────────
# Default: 300ETF
ETF_NAME = "300ETF"
PATH_INST = "data/300ETF_instruments.parquet"
PATH_OPT  = "data/300ETF_historical_prices.parquet"
PATH_ETF  = "data/510300_1d.parquet"
PATH_IV_CACHE = "data/30d_iv_cache_300.parquet"

def select_underlying(etf_choice):
    global ETF_NAME, PATH_INST, PATH_OPT, PATH_ETF, PATH_IV_CACHE
    if etf_choice == "50":
        ETF_NAME = "50ETF"
        PATH_INST = "data/50ETF_instruments.parquet"
        PATH_OPT  = "data/50ETF_historical_prices.parquet"
        PATH_ETF  = "data/50ETF_1d.parquet"
        PATH_IV_CACHE = "data/30d_iv_cache_50.parquet"
    elif etf_choice == "500":
        ETF_NAME = "500ETF"
        PATH_INST = "data/500ETF_instruments.parquet"
        PATH_OPT  = "data/500ETF_historical_prices.parquet"
        PATH_ETF  = "data/500ETF_1d.parquet"
        PATH_IV_CACHE = "data/30d_iv_cache_500.parquet"
    else:
        # Default 300
        ETF_NAME = "300ETF"
        PATH_INST = "data/300ETF_instruments.parquet"
        PATH_OPT  = "data/300ETF_historical_prices.parquet"
        PATH_ETF  = "data/510300_1d.parquet"
        PATH_IV_CACHE = "data/30d_iv_cache_300.parquet"
    print(f"  Selected Underlying: {ETF_NAME}")
    print(f"  ETF Data Path      : {PATH_ETF}")


# ── Black-Scholes / IV helpers (numba-compiled) ───────────────────────────────
@njit(cache=True)
def _cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


@njit(cache=True)
def _bs_price(S, K, T, r, sigma, is_call):
    if T <= 1e-7 or sigma <= 1e-7:
        return max(0.0, S - K) if is_call else max(0.0, K - S)
    sqrtT = math.sqrt(T)
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * sqrtT)
    d2 = d1 - sigma * sqrtT
    if is_call:
        return S * _cdf(d1) - K * math.exp(-r * T) * _cdf(d2)
    else:
        return K * math.exp(-r * T) * _cdf(-d2) - S * _cdf(-d1)


class Tee(object):
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()
    def flush(self):
        for f in self.files:
            f.flush()


@njit(cache=True)
def compute_iv(market_price, S, K, T, r, is_call):
    """Bisection IV solver; returns 0.5 as fallback."""
    intrinsic = max(0.0, S - K) if is_call else max(0.0, K - S)
    if market_price <= intrinsic * 0.9999 or market_price <= 0:
        return 0.50
    lo, hi = 1e-4, 10.0
    if (_bs_price(S, K, T, r, hi, is_call) - market_price) < 0:
        return 0.50          # price > BS at max vol — fallback
    for _ in range(60):
        mid = (lo + hi) * 0.5
        if _bs_price(S, K, T, r, mid, is_call) < market_price:
            lo = mid
        else:
            hi = mid
    return (lo + hi) * 0.5




# ── Data loading ──────────────────────────────────────────────────────────────
def load_data():
    """Return (inst, opt, etf) DataFrames with parsed dates."""
    inst = pd.read_parquet(PATH_INST)
    opt  = pd.read_parquet(PATH_OPT)
    etf  = pd.read_parquet(PATH_ETF)

    inst["maturity_date"] = pd.to_datetime(inst["maturity_date"])
    opt["date"]           = pd.to_datetime(opt["date"])
    etf["date"]           = pd.to_datetime(etf["date"])

    # Keep only the columns we need from instruments
    inst = inst[["order_book_id", "strike_price", "maturity_date",
                 "option_type", "contract_multiplier"]].copy()

    # Merge instrument metadata into daily option prices
    opt = opt.merge(inst, on="order_book_id", how="left",
                    suffixes=("_raw", ""))
    # Resolve duplicate strike_price / contract_multiplier columns if any
    for col in ["strike_price", "contract_multiplier"]:
        raw = col + "_raw"
        if raw in opt.columns:
            opt[col] = opt[col].fillna(opt[raw])
            opt.drop(columns=[raw], inplace=True)

    etf = etf.set_index("date").sort_index()
    return inst, opt, etf


# ── Cycle detection ───────────────────────────────────────────────────────────
def get_cycles(opt, etf):
    """
    Return a list of dicts, one per tradeable monthly cycle:
      entry_date  – first available trading day in this cycle
      expiry_date – the contract's maturity_date (last trading day)
    Only include cycles where we have:
      - at least one call AND one put in the option data
      - ETF price data on entry_date
      - at least one trading day between entry and expiry
    We use the front-month expiry (the next expiry after data starts).
    Specifically, for each monthly expiry that is ≥ 30 days away from
    the first data date, compute entry as the trading day after the
    PRECEDING expiry (or data start if none).
    """
    trading_days_set = set(etf.index.normalize())
    opt_trading_days = sorted(opt["date"].unique())

    # Find all distinct monthly expiry dates with both C and P contracts
    expiries_cp = (
        opt.groupby(["maturity_date", "option_type"])["order_book_id"]
        .nunique()
        .unstack("option_type")
        .dropna()                    # must have both C and P
        .index.tolist()
    )
    expiries_cp = sorted(expiries_cp)

    cycles = []
    for i, expiry in enumerate(expiries_cp):
        # Entry date = first opt trading day AFTER previous expiry
        # (or first available day for the very first cycle)
        if i == 0:
            # First cycle: enter on the first trading day in dataset
            entry = opt_trading_days[0]
        else:
            prev_expiry = expiries_cp[i - 1]
            candidates = [d for d in opt_trading_days if d > prev_expiry]
            if not candidates:
                continue
            entry = candidates[0]

        # Skip if entry >= expiry (no room to trade)
        if entry >= expiry:
            continue

        # Skip if ETF data missing on entry date
        entry_norm = pd.Timestamp(entry).normalize()
        if entry_norm not in trading_days_set:
            continue

        cycles.append({"entry_date": entry, "expiry_date": expiry})

    return cycles


# ── ATM IV on a given date ────────────────────────────────────────────────────
def get_atm_iv(opt, etf, entry_date, expiry_date):
    """
    Find the ATM call option for `expiry_date` on `entry_date`
    and return its implied volatility (annualised).
    Falls back to IV_THRESHOLD if data is missing.
    """
    etf_close = etf.loc[entry_date.normalize(), "close"]
    dte = (expiry_date - entry_date).days
    T = max(dte, 1) / 365.0

    day_opt = opt[
        (opt["date"] == entry_date) &
        (opt["maturity_date"] == expiry_date) &
        (opt["option_type"] == "C") &
        (opt["close"] > 0)
    ].copy()

    if day_opt.empty:
        return IV_THRESHOLD

    # Find the call whose strike is closest to current ETF price
    day_opt["dist"] = (day_opt["strike_price"] - etf_close).abs()
    row = day_opt.loc[day_opt["dist"].idxmin()]

    iv = compute_iv(
        float(row["close"]),
        float(etf_close),
        float(row["strike_price"]),
        T,
        RISK_FREE,
        True   # call
    )
    return iv


def get_30d_iv(opt, etf, date):
    """
    Estimate the 30-day interpolated ATM IV for a given date.
    Uses linear interpolation of variance: sigma_30^2 = (sigma1^2 * (T2-30) + sigma2^2 * (30-T1)) / (T2-T1)
    """
    date_norm = date.normalize()
    if date_norm not in etf.index:
        return IV_THRESHOLD
    etf_close = float(etf.loc[date_norm, "close"])

    # All calls for this date
    day_calls = opt[
        (opt["date"] == date) &
        (opt["option_type"] == "C") &
        (opt["close"] > 0)
    ].copy()

    if day_calls.empty:
        return IV_THRESHOLD

    # Group by expiry and find ATM strike for each
    expiries = sorted(day_calls["maturity_date"].unique())
    iv_by_expiry = {}

    for exp in expiries:
        exp_opts = day_calls[day_calls["maturity_date"] == exp].copy()
        exp_opts["dist"] = (exp_opts["strike_price"] - etf_close).abs()
        row = exp_opts.loc[exp_opts["dist"].idxmin()]
        
        dte = (exp - date).days
        T = max(dte, 1) / 365.0
        
        iv = compute_iv(
            float(row["close"]),
            float(etf_close),
            float(row["strike_price"]),
            T,
            RISK_FREE,
            True
        )
        iv_by_expiry[dte] = iv

    dtes = sorted(iv_by_expiry.keys())
    if not dtes:
        return IV_THRESHOLD

    # Select T1 (<= 30) and T2 (> 30)
    t1_candidates = [d for d in dtes if d <= 30]
    t2_candidates = [d for d in dtes if d > 30]

    if t1_candidates and t2_candidates:
        t1 = t1_candidates[-1]
        t2 = t2_candidates[0]
        v1 = iv_by_expiry[t1]**2
        v2 = iv_by_expiry[t2]**2
        # Interpolate variance
        v30 = (v1 * (t2 - 30) + v2 * (30 - t1)) / (t2 - t1)
        return math.sqrt(max(0, v30))
    elif t1_candidates:
        # Only shorter expiries available
        return iv_by_expiry[t1_candidates[-1]]
    elif t2_candidates:
        # Only longer expiries available
        return iv_by_expiry[t2_candidates[0]]
    
    return IV_THRESHOLD


# ── OTM strike selector ───────────────────────────────────────────────────────
def get_otm_strikes(opt, etf, entry_date, expiry_date, option_type, offsets):
    """
    Select actual contracts for the given OTM offsets (1-indexed rank).
    option_type: 'C' or 'P'
    offsets: list of ints, e.g. [3, 4] for call legs A and B

    Returns a list of rows (dicts) from opt, one per offset.
    Missing contracts return None at that position.
    """
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
        # OTM calls: strike > ETF price, sorted ascending
        otm = day_opt[day_opt["strike_price"] > etf_close].sort_values("strike_price")
    else:
        # OTM puts: strike < ETF price, sorted descending (OTM1 = closest to spot)
        otm = day_opt[day_opt["strike_price"] < etf_close].sort_values(
            "strike_price", ascending=False
        )

    results = []
    for off in offsets:
        idx = off - 1          # 0-based
        if idx < len(otm):
            results.append(otm.iloc[idx].to_dict())
        else:
            results.append(None)
    return results



# ── Per-cycle P&L ─────────────────────────────────────────────────────────────
def calc_leg_pnl(leg, opt, etf, expiry_date, side, is_buyer_at_expiry):
    """
    Compute the full P&L (in RMB) for a single option leg.

    Parameters
    ----------
    leg                : dict (row from opt on entry date), or None
    opt                : full option DataFrame
    etf                : ETF DataFrame (indexed by date)
    expiry_date        : pd.Timestamp
    side               : 'sell' or 'buy'
    is_buyer_at_expiry : True if WE are the option buyer (put spread buy leg)

    Returns dict with: entry_px, exec_px, premium_rmb, exercise_pnl_rmb,
                       commission_rmb, exercise_cost_rmb, net_rmb, note
    """
    if leg is None:
        return None

    K          = float(leg["strike_price"])
    mult       = float(leg["contract_multiplier"])
    entry_mid  = float(leg["close"])
    otype      = leg["option_type"]   # 'C' or 'P'

    # Execution price with spread
    if side == "sell":
        exec_px = entry_mid * (1 - SPREAD_HALF)   # we sell at bid
    else:
        exec_px = entry_mid * (1 + SPREAD_HALF)   # we buy at ask

    # Premium in RMB (positive = cash received, negative = paid)
    if side == "sell":
        premium_rmb = exec_px * mult
    else:
        premium_rmb = -exec_px * mult

    # Last ETF close price (settlement)
    # Use the last available ETF date on or before expiry
    etf_expiry_dates = etf.index[etf.index <= expiry_date]
    if etf_expiry_dates.empty:
        etf_settle = None
    else:
        etf_settle = float(etf.loc[etf_expiry_dates[-1], "close"])

    # Exercise outcome
    exercise_pnl_rmb = 0.0
    exercise_cost_rmb = 0.0
    note = "expires_worthless"

    if etf_settle is not None:
        if otype == "C":
            in_the_money = etf_settle > K
            intrinsic = max(0.0, etf_settle - K)
        else:
            in_the_money = etf_settle < K
            intrinsic = max(0.0, K - etf_settle)

        if in_the_money:
            if side == "sell":
                # We are ASSIGNED (seller): we pay the intrinsic, no exercise fee
                exercise_pnl_rmb  = -intrinsic * mult
                exercise_cost_rmb = 0.0
                note = f"assigned  ETF={etf_settle:.4f} K={K:.4f}"
            else:
                # We EXERCISE (buyer): we receive the intrinsic, pay exercise fee
                exercise_pnl_rmb  = intrinsic * mult
                exercise_cost_rmb = EXERCISE_COST
                note = f"exercised ETF={etf_settle:.4f} K={K:.4f}"

    commission_rmb = COMMISSION   # flat 5 RMB per leg regardless of direction

    net_rmb = (premium_rmb
               + exercise_pnl_rmb
               - commission_rmb
               - exercise_cost_rmb)

    return {
        "entry_mid":          entry_mid,
        "exec_px":            exec_px,
        "K":                  K,
        "mult":               mult,
        "otype":              otype,
        "side":               side,
        "premium_rmb":        premium_rmb,
        "exercise_pnl_rmb":   exercise_pnl_rmb,
        "commission_rmb":     commission_rmb,
        "exercise_cost_rmb":  exercise_cost_rmb,
        "net_rmb":            net_rmb,
        "note":               note,
    }


def calc_cycle_pnl(cyc, opt, etf, daily_ivs):
    """
    Run a full cycle and return a summary dict.
    daily_ivs is a pd.Series of 30-day interpolated IVs indexed by date.
    """
    entry  = cyc["entry_date"]
    expiry = cyc["expiry_date"]

    # Use the pre-calculated 30-day IV for signal generation
    iv = daily_ivs.get(entry, IV_THRESHOLD)

    # 1. IV Rank calculation (using 252-day daily lookback = 1 year)
    history = daily_ivs[daily_ivs.index <= entry]
    if len(history) >= 20:   # Require at least some history
        lookback = history.tail(252)
        min_iv = lookback.min()
        max_iv = lookback.max()
        if max_iv > min_iv:
            ivr = (iv - min_iv) / (max_iv - min_iv)
        else:
            ivr = 0.5
    else:
        ivr = 0.5

    # IVR regime logic for Call legs
    if ivr > IVR_HIGH:
        offset = 5
    elif ivr < IVR_LOW:
        offset = 3
    else:
        offset = 4

    # 2. Momentum Filter (Vol-Adjusted using 20-day ATR)
    etf_history = etf[etf.index <= entry].copy()
    if len(etf_history) >= 20:
        sma20 = etf_history["close"].tail(20).mean()
        # Calculate ATR
        etf_history['TR'] = etf_history[['high', 'low', 'close']].apply(
            lambda row: max(row['high'] - row['low'], 
                            abs(row['high'] - etf_history['close'].shift(1).loc[row.name]) if pd.notna(etf_history['close'].shift(1).loc[row.name]) else 0,
                            abs(row['low'] - etf_history['close'].shift(1).loc[row.name]) if pd.notna(etf_history['close'].shift(1).loc[row.name]) else 0),
            axis=1
        )
        atr20 = etf_history['TR'].tail(20).mean()
    else:
        sma20 = etf_history["close"].mean()
        atr20 = etf_history['close'].std() if len(etf_history) > 1 else 0.1

    etf_close_entry = float(etf.loc[entry.normalize(), "close"])
    
    # 3. Constant-Notional Sizing
    # Target 400,000 RMB exposure per cycle (approx 10 contracts at 4.0 ETF price)
    target_exposure = 400000.0
    contract_size = 10000
    num_contracts = round(target_exposure / (etf_close_entry * contract_size))
    if num_contracts < 1:
        num_contracts = 1
        
    # [V6] Volatility Sizing Reduction: If IVR > 0.8, reduce size by 30% to manage tail risk
    if ivr > 0.8:
        num_contracts = round(num_contracts * 0.7)
        if num_contracts < 1: num_contracts = 1

    momentum_dist = (etf_close_entry - sma20)
    
    # Trend up breakout: if ETF > 20d SMA by > 1.5 * ATR (volatility-adjusted breakout)
    trend_up_breakout = (momentum_dist > 1.5 * atr20) if atr20 > 0 else False

    call_legs = get_otm_strikes(opt, etf, entry, expiry, "C", [offset, offset + 1])
    
    # 4. Put Selection (Simplified V6: IVR-driven offsets + Momentum Filter + Narrow Gap)
    # [V6] Momentum Filter: Only sell puts if ETF price is above 20d SMA (uptrend)
    put_market_filter = (etf_close_entry > sma20)
    
    # Determine ranks based on IVR
    if ivr > IVR_HIGH:
        put_sell_rank = 4
    else:
        put_sell_rank = 3
    
    # [V6] Narrow Gap: Exactly 2 strikes deeper (Max theoretical loss = 2 * strike_step)
    put_buy_rank = put_sell_rank + 2

    # Get Sell Put (clamped to OTM3+)
    sell_put_list = get_otm_strikes(opt, etf, entry, expiry, "P", [put_sell_rank])
    best_sell_put = sell_put_list[0]
    
    put_valid = False
    put_legs = [None, None]
    put_offsets = [0, 0]

    if best_sell_put and put_market_filter:
        # Get Buy Put: Try target rank, fallback to deepest available
        all_otm = get_otm_strikes(opt, etf, entry, expiry, "P", list(range(1, 15)))
        all_otm = [p for p in all_otm if p is not None]
        
        if len(all_otm) > put_sell_rank:
            # Try target buy rank
            best_buy_put = None
            if len(all_otm) >= put_buy_rank:
                best_buy_put = all_otm[put_buy_rank - 1]
                actual_buy_rank = put_buy_rank
            else:
                # Fallback to deepest available
                best_buy_put = all_otm[-1]
                actual_buy_rank = len(all_otm)
            
            # Ensure they are different and buy is deeper
            if best_buy_put and actual_buy_rank > put_sell_rank:
                p_sell_mid = float(best_sell_put["close"])
                p_buy_mid  = float(best_buy_put["close"])
                mult       = float(best_sell_put["contract_multiplier"])
                
                p_sell_bid = p_sell_mid * (1 - SPREAD_HALF)
                p_buy_ask  = p_buy_mid * (1 + SPREAD_HALF)
                
                exp_net_credit = (p_sell_bid - p_buy_ask) * mult - 2 * COMMISSION
                if exp_net_credit >= MIN_PUT_CREDIT:
                    put_legs = [best_sell_put, best_buy_put]
                    put_offsets = [put_sell_rank, actual_buy_rank]
                    put_valid = True

    results = []
    
    legs_to_process = [
        (call_legs[1], "sell", f"Call Leg B (OTM{offset+1})")
    ]
    if not trend_up_breakout:
        legs_to_process.insert(0, (call_legs[0], "sell", f"Call Leg A (OTM{offset})"))

    if put_valid:
        legs_to_process.append((put_legs[0], "sell", f"Put Sell   (OTM{put_offsets[0]})"))
        legs_to_process.append((put_legs[1], "buy", f"Put Buy    (OTM{put_offsets[1]})"))

    for leg, side, label in legs_to_process:
        res = calc_leg_pnl(leg, opt, etf, expiry, side, side == "buy")
        if res is not None:
            # Scale exactly by the number of contracts
            res["premium_rmb"] *= num_contracts
            res["exercise_pnl_rmb"] *= num_contracts
            res["commission_rmb"] *= num_contracts
            res["exercise_cost_rmb"] *= num_contracts
            res["net_rmb"] *= num_contracts
            res["mult"] *= num_contracts
            
            res["label"] = label
            results.append(res)

    total_net = sum(r["net_rmb"] for r in results)
    total_premium = sum(r["premium_rmb"] for r in results)

    return {
        "entry_date":     entry,
        "expiry_date":    expiry,
        "iv":             iv,
        "ivr":            ivr,
        "atr_dist":       (momentum_dist / atr20) if atr20 > 0 else 0,
        "reduced_calls":  trend_up_breakout,
        "skipped_puts":   not put_valid,
        "offset":         offset,
        "put_offsets":    put_offsets,
        "num_contracts":  num_contracts,
        "etf_entry":      etf_close_entry,
        "legs":           results,
        "total_premium":  total_premium,
        "total_net_rmb":  total_net,
    }




# ── Main backtest runner ───────────────────────────────────────────────────────
def run_backtest(opt, etf):
    if os.path.exists(PATH_IV_CACHE):
        print(f"\nLoading pre-calculated 30-day IVs from {PATH_IV_CACHE}...")
        daily_ivs = pd.read_parquet(PATH_IV_CACHE).iloc[:, 0]
        # Ensure it's indexed by datetime
        daily_ivs.index = pd.to_datetime(daily_ivs.index)
    else:
        print("\nPre-calculating daily 30-day IVs (this may take a moment)...")
        trading_days = sorted(etf.index.unique())
        iv_data = {}
        for i, d in enumerate(trading_days):
            if i % 100 == 0:
                print(f"  Progress: {i}/{len(trading_days)}")
            iv_data[d] = get_30d_iv(opt, etf, d)
        daily_ivs = pd.Series(iv_data).sort_index()
        # Save cache
        os.makedirs(os.path.dirname(PATH_IV_CACHE), exist_ok=True)
        daily_ivs.to_frame("iv").to_parquet(PATH_IV_CACHE)
        print(f"  Saved IV cache to {PATH_IV_CACHE}")

    cycles  = get_cycles(opt, etf)
    results = []
    for cyc in cycles:
        res = calc_cycle_pnl(cyc, opt, etf, daily_ivs)
        results.append(res)

    # ── Per-cycle detail printout ──────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  备兑期权 BACKTEST — Cycle Detail")
    print("=" * 70)

    for res in results:
        print(f"\nCycle  {res['entry_date'].date()} → {res['expiry_date'].date()}"
              f"   IV={res['iv']:.1%} (IVR={res['ivr']:.2f})  calls=OTM{res['offset']} puts=OTM{res['put_offsets'][0]}/{res['put_offsets'][1]}"
              f"   ETF={res['etf_entry']:.4f} ATR-dist={res['atr_dist']:+.2f} ({res['num_contracts']} contracts)"
              f"   {'[REDUCED CALLS]' if res['reduced_calls'] else ''}"
              f"{' [SKIPPED PUTS]' if res.get('skipped_puts') else ''}")
        hdr = f"  {'Leg':<25} {'side':>4} {'K':>7} {'exec_px':>8} {'prem':>8}  {'exer':>9}  {'net':>8}"
        print(hdr)
        print("  " + "-" * (len(hdr) - 2))
        for r in res["legs"]:
            print(f"  {r['label']:<25} {r['side']:>4} {r['K']:>7.3f}"
                  f" {r['exec_px']:>8.4f} {r['premium_rmb']:>8.2f}"
                  f"  {r['exercise_pnl_rmb']:>9.2f}  {r['net_rmb']:>8.2f}"
                  f"  [{r['note']}]")
        print(f"  {'CYCLE TOTAL':>49}  {res['total_net_rmb']:>8.2f}")

    # ── Aggregate summary ─────────────────────────────────────────────────────
    nets       = [r["total_net_rmb"]  for r in results]
    premiums   = [r["total_premium"]  for r in results]
    cumulative = list(np.cumsum(nets))
    total_net  = sum(nets)
    win_rate   = sum(1 for n in nets if n > 0) / len(nets) if nets else 0
    avg_prem   = np.mean(premiums) if premiums else 0

    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"  Cycles traded          : {len(results)}")
    print(f"  Winning cycles         : {sum(1 for n in nets if n > 0)}/{len(nets)}"
          f"  ({win_rate:.0%})")
    print(f"  Avg gross premium/cyc  : {avg_prem:>8.2f} RMB")
    print(f"  Total net P&L          : {total_net:>8.2f} RMB")
    print(f"  Cumulative by cycle    : {[f'{v:.0f}' for v in cumulative]}")

    # ── Chart ─────────────────────────────────────────────────────────────────
    out_file = f"backtest_covered_call_{ETF_NAME}.png"
    plot_backtest_results(results, etf, out_file)

    return results


def plot_backtest_results(results, etf, out_path):
    """
    Advanced plotting for backtest results including P&L, Drawdown, and Leg Breakdown.
    """
    import numpy as np
    import matplotlib.pyplot as plt
    
    # 1. Prepare Data
    dates = [r['expiry_date'] for r in results]
    nets = [r['total_net_rmb'] for r in results]
    cumulative = np.cumsum(nets)
    
    # Calculate Drawdown
    peaks = np.maximum.accumulate(cumulative)
    drawdown = np.zeros_like(cumulative)
    peak_mask = peaks > 0
    drawdown[peak_mask] = (cumulative[peak_mask] - peaks[peak_mask]) / peaks[peak_mask]
    max_dd = np.min(drawdown) if len(drawdown) > 0 else 0
    
    # Normalize ETF for overlay
    etf_sub = etf.reindex(dates, method='ffill')['close']
    etf_norm = (etf_sub / etf_sub.iloc[0] - 1) * 100 # % change
    
    # Calculate key metrics
    total_net = cumulative[-1]
    win_rate = sum(1 for n in nets if n > 0) / len(results) if results else 0
    sharpe = np.sqrt(12) * np.mean(nets) / np.std(nets) if len(nets) > 1 and np.std(nets) > 0 else 0
    
    # 2. Setup Figure
    try:
        plt.style.use('seaborn-v0_8-muted')
    except:
        plt.style.use('ggplot')
        
    fig = plt.figure(figsize=(12, 12))
    gs = fig.add_gridspec(3, 1, height_ratios=[4, 3, 2], hspace=0.3)
    
    COLOR_CUM = "#2980b9"
    COLOR_BAR_UP = "#27ae60"
    COLOR_BAR_DN = "#e74c3c"
    COLOR_ETF = "#f39c12"
    
    # ── TOP PANEL ─────────────────────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0])
    x = np.arange(len(results))
    bar_colors = [COLOR_BAR_UP if n >= 0 else COLOR_BAR_DN for n in nets]
    ax1.bar(x, nets, color=bar_colors, alpha=0.3, label="Net P&L per Cycle")
    ax1.plot(x, cumulative, color=COLOR_CUM, linewidth=2.5, marker='o', markersize=4, label="Cumulative P&L")
    ax1.set_ylabel("P&L (RMB)", fontsize=10, fontweight='bold')
    ax1.grid(True, linestyle='--', alpha=0.6)
    
    ax1_twin = ax1.twinx()
    ax1_twin.plot(x, etf_norm, color=COLOR_ETF, linestyle='--', linewidth=1.5, alpha=0.7, label="Underlying ETF (%)")
    ax1_twin.set_ylabel("ETF Return (%)", color=COLOR_ETF, fontsize=10, fontweight='bold')
    ax1_twin.tick_params(axis='y', labelcolor=COLOR_ETF)
    
    cycle_labels = [r['expiry_date'].strftime('%y-%m') for r in results]
    ax1.set_xticks(x)
    ax1.set_xticklabels(cycle_labels, rotation=45 if len(x) > 15 else 0, fontsize=8)
    
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1_twin.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=True, fontsize=9)
    
    summary_text = (
        f" Total Net: {total_net/1e4:>6.2f}W\n"
        f" Win Rate : {win_rate:>6.2%}\n"
        f" Max DD   : {max_dd:>6.2%}\n"
        f" Sharpe   : {sharpe:>6.2f}"
    )
    ax1.text(0.98, 0.05, summary_text, transform=ax1.transAxes, 
             verticalalignment='bottom', horizontalalignment='right',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8),
             fontsize=10, family='monospace')
    
    ax1.set_title(f"Covered Call Strategy Performance vs {ETF_NAME}", fontsize=14, fontweight='bold', pad=15)

    # ── MIDDLE PANEL ──────────────────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[1])
    leg_labels = sorted(list(set(l['label'] for res in results for l in res['legs'])))
    palette = ["#1abc9c", "#3498db", "#9b59b6", "#34495e", "#f1c40f", "#e67e22"]
    bottom_pos = np.zeros(len(results))
    bottom_neg = np.zeros(len(results))
    
    for i, label in enumerate(leg_labels):
        vals = np.array([next((l['net_rmb'] for l in res['legs'] if l['label'] == label), 0.0) for res in results])
        pos_vals = np.where(vals > 0, vals, 0)
        neg_vals = np.where(vals < 0, vals, 0)
        ax2.bar(x, pos_vals, bottom=bottom_pos, color=palette[i % len(palette)], label=label, alpha=0.8)
        ax2.bar(x, neg_vals, bottom=bottom_neg, color=palette[i % len(palette)], alpha=0.8)
        bottom_pos += pos_vals
        bottom_neg += neg_vals

    ax2.axhline(0, color='black', linewidth=0.8)
    ax2.set_ylabel("Leg Contribution (RMB)", fontsize=10, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(cycle_labels, rotation=45 if len(x) > 15 else 0, fontsize=8)
    ax2.legend(loc='upper right', frameon=True, fontsize=8, ncol=2)
    ax2.grid(True, axis='y', linestyle=':', alpha=0.5)
    ax2.set_title("Per-Leg Net P&L Contribution", fontsize=12, fontweight='bold')

    # ── BOTTOM PANEL ──────────────────────────────────────────────────────────
    ax3 = fig.add_subplot(gs[2])
    ax3.fill_between(x, drawdown * 100, 0, color=COLOR_BAR_DN, alpha=0.3)
    ax3.plot(x, drawdown * 100, color=COLOR_BAR_DN, linewidth=1.5, alpha=0.7)
    ax3.set_ylabel("Drawdown (%)", fontsize=10, fontweight='bold')
    ax3.set_ylim(min(drawdown * 100) * 1.2 if len(drawdown) > 0 else -10, 1)
    ax3.grid(True, linestyle=':', alpha=0.5)
    ax3.set_title("Strategy Drawdown Profile", fontsize=12, fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(cycle_labels, rotation=45 if len(x) > 15 else 0, fontsize=8)

    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches='tight')
    print(f"\n  Chart saved → {out_path}")


    return results


if __name__ == "__main__":
    # Handle command line argument for ETF choice
    choice = "300"
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    
    select_underlying(choice)
    
    # Redirect output to log file
    log_file = f"backtest_covered_call_{ETF_NAME}.log"
    f = open(log_file, 'w', encoding='utf-8')
    sys.stdout = Tee(sys.stdout, f)
    
    inst, opt, etf = load_data()
    run_backtest(opt, etf)

