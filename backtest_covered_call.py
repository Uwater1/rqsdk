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

# ── Constants ────────────────────────────────────────────────────────────────
SPREAD_HALF    = 0.02        # ±2% → bid = mid*0.98, ask = mid*1.02
COMMISSION     = 5.0         # RMB per option leg
EXERCISE_COST  = 2.0         # RMB when WE exercise as buyer
ETF_SHARES     = 20_000      # equity leg (no cost modelled here)
RISK_FREE      = 0.02        # annual risk-free rate for BS IV
IV_THRESHOLD   = 0.20        # ATM IV above this → go further OTM (offset 4)

# Data paths (relative to CWD = /home/hallo/Documents/rqsdk)
PATH_INST   = "data/300ETF_instruments.parquet"
PATH_OPT    = "data/300ETF_historical_prices.parquet"
PATH_ETF    = "data/510300_1d.parquet"


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


def calc_cycle_pnl(cyc, opt, etf):
    """
    Run a full cycle and return a summary dict.
    """
    entry  = cyc["entry_date"]
    expiry = cyc["expiry_date"]

    iv     = get_atm_iv(opt, etf, entry, expiry)
    offset = 4 if iv > IV_THRESHOLD else 3

    call_legs = get_otm_strikes(opt, etf, entry, expiry, "C", [offset, offset + 1])
    put_legs  = get_otm_strikes(opt, etf, entry, expiry, "P", [offset, offset + 1])

    results = []
    labels  = [
        f"Call Leg A (OTM{offset})",
        f"Call Leg B (OTM{offset+1})",
        f"Put Sell   (OTM{offset})",
        f"Put Buy    (OTM{offset+1})",
    ]
    legs  = [call_legs[0], call_legs[1], put_legs[0], put_legs[1]]
    sides = ["sell", "sell", "sell", "buy"]

    for leg, side, label in zip(legs, sides, labels):
        res = calc_leg_pnl(leg, opt, etf, expiry, side, side == "buy")
        if res is not None:
            res["label"] = label
            results.append(res)

    total_net = sum(r["net_rmb"] for r in results)
    total_premium = sum(r["premium_rmb"] for r in results)

    etf_close_entry = float(etf.loc[entry.normalize(), "close"])

    return {
        "entry_date":     entry,
        "expiry_date":    expiry,
        "iv":             iv,
        "offset":         offset,
        "etf_entry":      etf_close_entry,
        "legs":           results,
        "total_premium":  total_premium,
        "total_net_rmb":  total_net,
    }




# ── Main backtest runner ───────────────────────────────────────────────────────
def run_backtest(opt, etf):
    cycles  = get_cycles(opt, etf)
    results = [calc_cycle_pnl(cyc, opt, etf) for cyc in cycles]

    # ── Per-cycle detail printout ──────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  备兑期权 BACKTEST — Cycle Detail")
    print("=" * 70)

    for res in results:
        print(f"\nCycle  {res['entry_date'].date()} → {res['expiry_date'].date()}"
              f"   IV={res['iv']:.1%}  offset=OTM{res['offset']}"
              f"   ETF-entry={res['etf_entry']:.4f}")
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
    labels    = [f"{r['entry_date'].strftime('%m/%d')}\n→{r['expiry_date'].strftime('%m/%d')}"
                 for r in results]
    x         = np.arange(len(results))
    bar_colors = ["#4CAF50" if n >= 0 else "#F44336" for n in nets]

    fig, axes = plt.subplots(2, 1, figsize=(10, 7),
                             gridspec_kw={"height_ratios": [3, 2]})
    fig.suptitle("300ETF Backtest — Covered Call + Bull Put Spread (Beichu Qiquan)",
                 fontsize=13, fontweight="bold")

    # ── Top panel: net P&L per cycle (bars) + cumulative (line) ──────────────
    ax1 = axes[0]
    ax1.bar(x, nets, color=bar_colors, alpha=0.85, label="Net P&L per cycle")
    ax1.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax2 = ax1.twinx()
    ax2.plot(x, cumulative, marker="o", color="#1565C0",
             linewidth=2, markersize=6, label="Cumulative P&L")
    ax2.axhline(0, color="#1565C0", linewidth=0.4, linestyle=":")
    ax1.set_xticks(x); ax1.set_xticklabels(labels, fontsize=8)
    ax1.set_ylabel("Per-cycle Net P&L (RMB)")
    ax2.set_ylabel("Cumulative P&L (RMB)", color="#1565C0")
    ax2.tick_params(axis="y", labelcolor="#1565C0")
    # combine legends
    bars_h, bars_l = ax1.get_legend_handles_labels()
    line_h, line_l = ax2.get_legend_handles_labels()
    ax1.legend(bars_h + line_h, bars_l + line_l, loc="upper left", fontsize=8)
    ax1.set_title("Per-cycle and Cumulative Net P&L", fontsize=10)

    # ── Bottom panel: premium breakdown stacked bar ───────────────────────────
    ax3 = axes[1]
    leg_labels_all = set()
    for res in results:
        for r in res["legs"]:
            leg_labels_all.add(r["label"].strip())
    leg_labels_all = sorted(leg_labels_all)

    colors = ["#66BB6A", "#26A69A", "#EF5350", "#AB47BC"]
    bottom = np.zeros(len(results))
    for i, ll in enumerate(leg_labels_all):
        vals = []
        for res in results:
            match = next((r for r in res["legs"] if r["label"].strip() == ll), None)
            vals.append(match["net_rmb"] if match else 0.0)
        ax3.bar(x, vals, bottom=bottom, color=colors[i % len(colors)],
                alpha=0.80, label=ll, width=0.6)
        bottom = bottom + np.array(vals)

    ax3.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax3.set_xticks(x); ax3.set_xticklabels(labels, fontsize=8)
    ax3.set_ylabel("Net P&L (RMB)")
    ax3.legend(loc="upper left", fontsize=7, ncol=2)
    ax3.set_title("Per-leg Net P&L Breakdown", fontsize=10)

    plt.tight_layout()
    out_path = "backtest_covered_call.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"\n  Chart saved → {out_path}")

    return results


if __name__ == "__main__":
    inst, opt, etf = load_data()
    run_backtest(opt, etf)

