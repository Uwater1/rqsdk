import rqdatac
import os
import pandas as pd
from datetime import datetime, timedelta
import time
import argparse
import sys

# Initialize
rqdatac.init()

SAVE_DIR = "data-deep"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

def download_tick_data(order_book_id, date, underlying):
    """下载单个合约单日的Tick数据(包含双边报价)并存入组织好的文件夹"""
    try:
        # Remove dots from folder name (e.g., 510050.XSHG -> 510050XSHG)
        folder_name = underlying.replace('.', '')
        target_dir = os.path.join(SAVE_DIR, date, folder_name)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            
        filepath = os.path.join(target_dir, f"{order_book_id}.parquet")
        
        if os.path.exists(filepath):
            return f"{order_book_id} {date} SKIPPED (Already exists)"
        
        # 获取Tick数据
        df = rqdatac.get_price(
            order_book_id, 
            start_date=date, 
            end_date=date, 
            frequency='tick',
            expect_df=True
        )
        
        if df is not None and not df.empty:
            df.to_parquet(filepath)
            return f"{order_book_id} {date} SUCCESS: {len(df)} ticks"
        else:
            return f"{order_book_id} {date} EMPTY"
            
    except Exception as e:
        return f"{order_book_id} {date} ERROR: {str(e)}"

def run_download(target_date, target_ticker):
    # 处理日期
    date_str = target_date
    print(f"\n--- Processing date: {date_str} ---")
    
    # ETF期权标的
    if target_ticker.upper() == 'ALL':
        underlying_symbols = ['510050.XSHG', '510300.XSHG', '510500.XSHG']
    else:
        underlying_symbols = [target_ticker.upper()]
    
    total_count = 0
    for und in underlying_symbols:
        try:
            contracts = rqdatac.options.get_contracts(underlying=und, trading_date=date_str)
            print(f"Found {len(contracts)} contracts for {und} on {date_str}")
            
            for contract in contracts:
                res = download_tick_data(contract, date_str, und)
                print(res)
                total_count += 1
                time.sleep(0.05) 
        except Exception as e:
            print(f"Error fetching contracts for {und} on {date_str}: {e}")

    print(f"\nTick download completed. Total processed: {total_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download ETF Options Tick data (Bid/Ask).")
    parser.add_argument("--date", type=str, help="Target date (e.g., 2026-03-23)")
    parser.add_argument("--ticker", type=str, default="ALL", help="Underlying ticker: 510050.XSHG, 510300.XSHG, 510500.XSHG, or ALL (default: ALL)")
    
    # 如果没有提供参数或提供了 -h，则显示用法
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
        
    args = parser.parse_args()
    
    if not args.date:
        print("Error: --date is required.")
        parser.print_help()
        sys.exit(1)
        
    run_download(args.date, args.ticker)
