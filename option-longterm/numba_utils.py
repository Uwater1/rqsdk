import math
import numpy as np
from numba import njit

# --- Constants for Yield and Interpolation ---
MIN_T_FOR_YIELD = 2 / 365.0  # Threshold to avoid division by near-zero T1 (Bug 3)

@njit(cache=True)
def _cdf(x):
    """Cumulative normal distribution function."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

@njit(cache=True)
def black_price(F, K, T, sigma, r, is_call):
    """Black model option price (Price of call/put on a forward/futures)."""
    if T <= 1e-7 or sigma <= 1e-7:
        intrinsic = max(0.0, F - K if is_call else K - F)
        return intrinsic * math.exp(-r * T)
    
    sqrtT = math.sqrt(T)
    # sigma * sqrtT must be positive
    s_sqrtT = sigma * sqrtT
    d1 = (math.log(F / K) + 0.5 * sigma**2 * T) / s_sqrtT
    d2 = d1 - s_sqrtT
    
    df = math.exp(-r * T)
    if is_call:
        return df * (F * _cdf(d1) - K * _cdf(d2))
    else:
        return df * (K * _cdf(-d2) - F * _cdf(-d1))

@njit(cache=True)
def black_iv(market_price, F, K, T, r, is_call):
    """Implied volatility for Black model using bisection."""
    intrinsic = max(0.0, (F - K if is_call else K - F) * math.exp(-r * T))
    
    # If market price is too low, return 0 or small vol
    if market_price <= intrinsic + 1e-7:
        return 1e-4
        
    # Bisection search range
    lo, hi = 1e-5, 5.0
    
    # Check if price at max vol is still below market price (Upper Bound check)
    if black_price(F, K, T, hi, r, is_call) < market_price:
        return 5.0 

    # Check if price at min vol is already above market price (Lower Bound check - Bug 4)
    if black_price(F, K, T, lo, r, is_call) >= market_price:
        return lo
        
    # Robust bisection
    for _ in range(40): 
        mid = (lo + hi) / 2.0
        if black_price(F, K, T, mid, r, is_call) < market_price:
            lo = mid
        else:
            hi = mid
            
    return (lo + hi) / 2.0

@njit(cache=True)
def process_synthetic_strikes_loop(strikes, 
                                 c1_arr, p1_arr, c2_arr, p2_arr, 
                                 s0, r, T1, T2, t_star,
                                 F1, F2):
    """
    Core numerical loop for a single (Date, Target) pair.
    Uses pre-computed shared forwards F1, F2 to ensure consistency across strikes (Bug 2).
    Averages Call/Put IVs to maintain Put-Call Parity at T* (Bug 3).
    """
    num_strikes = len(strikes)
    # Result: [Price_C, Price_P, IV_star, F_star, unused]
    results = np.zeros((num_strikes, 5))
    
    # 1. Shared Yields and Forward Star (Constant for all strikes in this loop)
    q2 = r - math.log(F2 / s0) / T2
    # Use fallback if T1 is too close to expiry to avoid noisy yield (Bug 5)
    q1 = (r - math.log(F1 / s0) / T1) if T1 > MIN_T_FOR_YIELD else q2
    
    # Clip yield to reasonable range [-1.0, 1.0]
    q1 = max(-1.0, min(1.0, q1))
    q2 = max(-1.0, min(1.0, q2))
    
    # Interpolate yield and forward star
    q_star = ((T2 - t_star) / (T2 - T1)) * q1 + ((t_star - T1) / (T2 - T1)) * q2
    F_star = s0 * math.exp((r - q_star) * t_star)
    
    for i in range(num_strikes):
        k = strikes[i]
        c1, p1 = c1_arr[i], p1_arr[i]
        c2, p2 = c2_arr[i], p2_arr[i]
        
        # 2. Implied Vols at T1 and T2 - Average C and P for parity consistency
        iv1_c = black_iv(c1, F1, k, T1, r, True)
        iv1_p = black_iv(p1, F1, k, T1, r, False)
        iv1 = (iv1_c + iv1_p) / 2.0
        
        iv2_c = black_iv(c2, F2, k, T2, r, True)
        iv2_p = black_iv(p2, F2, k, T2, r, False)
        iv2 = (iv2_c + iv2_p) / 2.0
        
        # 3. Interpolate in Total Variance (Bug 5: skip noisy T1 if near expiry)
        if T1 <= MIN_T_FOR_YIELD:
            iv_star = iv2
        else:
            w1 = (T2 - t_star) / (T2 - T1)
            w2 = (t_star - T1) / (T2 - T1)
            var_star = w1 * (iv1**2 * T1) + w2 * (iv2**2 * T2)
            iv_star = math.sqrt(max(0.0, var_star / t_star))
        
        # 4. Reprice both from SAME iv_star and F_star to preserve PCP
        price_star_c = black_price(F_star, k, t_star, iv_star, r, True)
        price_star_p = black_price(F_star, k, t_star, iv_star, r, False)
        
        # Store results
        results[i, 0] = price_star_c
        results[i, 1] = price_star_p
        results[i, 2] = iv_star
        results[i, 3] = F_star
        
    return results

@njit(cache=True)
def calculate_research_metrics_numba(strikes, s0s, ret_val, prices, worthless, boundaries, is_short_call, filter_mask):
    """
    Numba-accelerated aggregation for OTM levels with filter support.
    is_short_call: True for Short Call, False for Long Put
    filter_mask: Boolean array indicating if a group (date) passes the filter.
    Returns: Two sets of metrics (passed, filtered)
    """
    num_groups = len(boundaries) - 1
    num_levels = 6
    
    # Results per level: [count, sum_pnl, sum_wins, sum_total_wins, min_pnl]
    # Indices: 0: count, 1: sum_pnl, 2: sum_wins, 3: sum_total_wins, 4: min_pnl
    metrics_passed = np.zeros((num_levels, 5))
    metrics_passed[:, 4] = 9999999.0 # Initialize min_pnl
    
    metrics_filtered = np.zeros((num_levels, 5))
    metrics_filtered[:, 4] = 9999999.0
    
    # Constants for RMB
    MULTIPLIER = 10000.0
    COMMISSION = 2.0
    SLIPPAGE = 0.02
    
    for g in range(num_groups):
        start = boundaries[g]
        end = boundaries[g+1]
        
        # s0 is same for all strikes in group
        s0 = s0s[start]
        is_pass = filter_mask[g]
        
        # Determine which metrics set to update
        if is_pass:
            metrics = metrics_passed
        else:
            # Filter only applies to Short Call cycles
            if is_short_call:
                metrics = metrics_filtered
            else:
                # Long Put always passes filter (as per research_otm_levels.py)
                metrics = metrics_passed
        
        # Since group is sorted by Strike (ASC):
        if is_short_call:
            # Call: OTM strikes are > s0, sorted ascending. ATM is last strike <= s0.
            atm_idx = -1
            first_otm_idx = start
            for i in range(start, end):
                if strikes[i] <= s0:
                    atm_idx = i
                    first_otm_idx = i + 1
                else:
                    break
            
            idx_list = []
            if atm_idx != -1:
                idx_list.append(atm_idx)
            else:
                idx_list.append(-1) # No Level 0 available
                
            # Levels 1-5 (Strikes > s0)
            for i in range(first_otm_idx, end):
                if len(idx_list) >= 6: break
                idx_list.append(i)

            # Process collected levels
            for lv in range(len(idx_list)):
                idx = idx_list[lv]
                if idx == -1: continue # Skip if this level is missing (e.g., Level 0)

                ret = ret_val[idx]
                prc = prices[idx]
                wth = worthless[idx]

                if np.isnan(ret): continue

                # Short Call calculation
                sell_p = prc * (1.0 - SLIPPAGE)
                pnl = ret * sell_p * MULTIPLIER - COMMISSION

                metrics[lv, 0] += 1
                metrics[lv, 1] += pnl
                if pnl > 0: metrics[lv, 2] += 1
                if wth == 1: metrics[lv, 3] += 1
                if pnl < metrics[lv, 4]: metrics[lv, 4] = pnl
        else:
            # Long Put: OTM strikes are < s0, sorted descending (so we reverse later).
            # ATM is first strike >= s0.
            atm_idx = -1
            first_otm_idx = end - 1
            for i in range(start, end):
                if strikes[i] >= s0:
                    atm_idx = i
                    first_otm_idx = i - 1
                    break
            
            # If no strike >= s0, all strikes are < s0. ATM is missing, but first OTM is still end-1.

            idx_list = []
            if atm_idx != -1:
                idx_list.append(atm_idx)
            else:
                idx_list.append(-1) # No Level 0 available
                
            # Levels 1-5 (Strikes < s0) - search backwards
            for i in range(first_otm_idx, start - 1, -1):
                if len(idx_list) >= 6: break
                idx_list.append(i)

            # Process collected levels
            for lv in range(len(idx_list)):
                idx = idx_list[lv]
                if idx == -1: continue

                ret = ret_val[idx]
                prc = prices[idx]
                wth = worthless[idx]

                if np.isnan(ret): continue

                # Long Put calculation
                buy_p = prc * (1.0 + SLIPPAGE)
                pnl = ret * buy_p * MULTIPLIER - COMMISSION

                metrics[lv, 0] += 1
                metrics[lv, 1] += pnl
                if pnl > 0: metrics[lv, 2] += 1
                if wth == 1: metrics[lv, 3] += 1
                if pnl < metrics[lv, 4]: metrics[lv, 4] = pnl
                    
    return metrics_passed, metrics_filtered
