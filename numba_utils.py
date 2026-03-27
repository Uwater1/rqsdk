import math
import numpy as np
from numba import njit

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
    
    # Check if price at max vol is still below market price
    if black_price(F, K, T, hi, r, is_call) < market_price:
        return 5.0 # cap at 500%
        
    # Robust bisection
    for _ in range(40): # Enough iterations for high precision
        mid = (lo + hi) / 2.0
        if black_price(F, K, T, mid, r, is_call) < market_price:
            lo = mid
        else:
            hi = mid
            
    return (lo + hi) / 2.0

@njit(cache=True)
def process_synthetic_strikes_loop(strikes, 
                                 c1_arr, p1_arr, c2_arr, p2_arr, 
                                 s0, r, T1, T2, t_star):
    """
    Core numerical loop for a single (Date, Target) pair.
    Calculates yields, forward star, and synthetic prices/IVs for all strikes.
    """
    # Pre-allocate results: [Price_C, Price_P, IV_C, IV_P, F_star]
    num_strikes = len(strikes)
    results = np.zeros((num_strikes, 5))
    
    exp_rT1 = math.exp(r * T1)
    exp_rT2 = math.exp(r * T2)
    
    for i in range(num_strikes):
        k = strikes[i]
        c1, p1 = c1_arr[i], p1_arr[i]
        c2, p2 = c2_arr[i], p2_arr[i]
        
        # 1. Forward Prices at T1 and T2 (Put-Call Parity)
        F1 = k + (c1 - p1) * exp_rT1
        F2 = k + (c2 - p2) * exp_rT2
        
        # Sanity check for F (must be within 20% of spot theoretically for ETFs)
        if F1 <= 1e-3 or F2 <= 1e-3 or abs(F1/s0 - 1) > 0.2 or abs(F2/s0 - 1) > 0.2:
            continue
            
        # 2. Yields calculation
        q2 = r - math.log(F2 / s0) / T2
        q1 = (r - math.log(F1 / s0) / T1) if T1 > (2/365.0) else q2
        
        # Clip yield to reasonable range [-1.0, 1.0]
        if q1 > 1.0: q1 = 1.0
        elif q1 < -1.0: q1 = -1.0
        if q2 > 1.0: q2 = 1.0
        elif q2 < -1.0: q2 = -1.0
        
        # 3. Interpolate yield and forward star
        q_star = ((T2 - t_star) / (T2 - T1)) * q1 + ((t_star - T1) / (T2 - T1)) * q2
        F_star = s0 * math.exp((r - q_star) * t_star)
        
        # 4. Implied Vols at T1 and T2
        iv1_c = black_iv(c1, F1, k, T1, r, True)
        iv1_p = black_iv(p1, F1, k, T1, r, False)
        iv2_c = black_iv(c2, F2, k, T2, r, True)
        iv2_p = black_iv(p2, F2, k, T2, r, False)
        
        # 5. Interpolate in Total Variance for each type
        # Call interpolation
        w_star_c = ((T2 - t_star) / (T2 - T1)) * (iv1_c**2 * T1) + ((t_star - T1) / (T2 - T1)) * (iv2_c**2 * T2)
        iv_star_c = math.sqrt(max(0.0, w_star_c / t_star))
        price_star_c = black_price(F_star, k, t_star, iv_star_c, r, True)
        
        # Put interpolation
        w_star_p = ((T2 - t_star) / (T2 - T1)) * (iv1_p**2 * T1) + ((t_star - T1) / (T2 - T1)) * (iv2_p**2 * T2)
        iv_star_p = math.sqrt(max(0.0, w_star_p / t_star))
        price_star_p = black_price(F_star, k, t_star, iv_star_p, r, False)
        
        # Store results
        results[i, 0] = price_star_c
        results[i, 1] = price_star_p
        results[i, 2] = iv_star_c
        results[i, 3] = iv_star_p
        results[i, 4] = F_star
        
    return results
