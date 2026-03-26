import os
import glob
import pandas as pd
import numpy as np
from numba import njit
from datetime import datetime, timedelta

def get_3rd_friday(year, month):
    # Find the 1st of the month
    first_day = datetime(year, month, 1)
    # Find the first Friday (0=Mon, 4=Fri)
    first_friday_offset = (4 - first_day.weekday()) % 7
    first_friday = first_day + timedelta(days=first_friday_offset)
    # Add two weeks to get the 3rd Friday
    third_friday = first_friday + timedelta(days=14)
    return third_friday

def calc_dte(current_time, year, month):
    exp_date = get_3rd_friday(year, month)
    # CFFEX contracts expire at 15:00 usually, but let's just do days
    diff = exp_date - current_time
    # +1 day because option close time is 15:00 and it's intraday? 
    # Let's just return diff.total_seconds() / 86400
    return diff.total_seconds() / 86400

@njit
def find_best_boxes(c_ask, c_bid, p_ask, p_bid, Ks, num_strikes, num_times):
    # Returns best long near, mid and short
    # output arrays: shape (num_times, 5) -> K1, K2, cost/credit, profit, ann_ret
    best_long = np.zeros((num_times, 5)) 
    best_short = np.zeros((num_times, 5))
    
    best_long[:, 4] = -1.0 # Initialize ann_ret with negative
    best_short[:, 4] = -1.0
    
    for t in range(num_times):
        for i in range(num_strikes):
            for j in range(i+1, num_strikes):
                K1 = Ks[i]
                K2 = Ks[j]
                
                c1_a = c_ask[t, i]
                c2_b = c_bid[t, j]
                p2_a = p_ask[t, j]
                p1_b = p_bid[t, i]
                
                c1_b = c_bid[t, i]
                c2_a = c_ask[t, j]
                p2_b = p_bid[t, j]
                p1_a = p_ask[t, i]
                
                if c1_a > 0 and c2_b > 0 and p2_a > 0 and p1_b > 0:
                    box_buy_cost = (c1_a - c2_b) + (p2_a - p1_b)
                    payout = K2 - K1
                    long_profit = payout - box_buy_cost
                    if box_buy_cost > 0:
                        long_ret = long_profit / box_buy_cost
                        if long_ret > best_long[t, 4]:
                            best_long[t, 0] = K1
                            best_long[t, 1] = K2
                            best_long[t, 2] = box_buy_cost
                            best_long[t, 3] = long_profit
                            best_long[t, 4] = long_ret
                            
                if c1_b > 0 and c2_a > 0 and p2_b > 0 and p1_a > 0:
                    box_sell_credit = (c1_b - c2_a) + (p2_b - p1_a)
                    payout = K2 - K1
                    short_profit = box_sell_credit - payout
                    if payout > 0:
                        short_ret = short_profit / payout
                        if short_ret > best_short[t, 4]:
                            best_short[t, 0] = K1
                            best_short[t, 1] = K2
                            best_short[t, 2] = box_sell_credit
                            best_short[t, 3] = short_profit
                            best_short[t, 4] = short_ret
                            
    return best_long, best_short
