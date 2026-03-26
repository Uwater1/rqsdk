import rqdatac
import os
import pandas as pd
from datetime import datetime, timedelta
import time

# Initialize
rqdatac.init()

SAVE_DIR = "data-deep"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

def get_latest_trading_dates(n=5):
    """获取最近n个交易日"""
    end_date = datetime.now().date()
    dates = rqdatac.get_trading_dates(start_date=end_date - timedelta(days=30), end_date=end_date)
    return sorted(dates, reverse=True)[:n]

def download_tick_data(order_book_id, date):
    """下载单个合约单日的Tick数据(包含双边报价)"""
    try:
        filename = f"{order_book_id}_{date}.parquet"
        filepath = os.path.join(SAVE_DIR, filename)
        
        if os.path.exists(filepath):
            return f"{order_book_id} {date} ALREADY EXISTS"
        
        # 获取Tick数据 (包含 a1~a5, b1~b5)
        df = rqdatac.get_price(
            order_book_id, 
            start_date=date, 
            end_date=date, 
            frequency='tick',
            expect_df=True
        )
        
        if df is not None and not df.empty:
            # 确保包含 bid/ask 字段
            df.to_parquet(filepath)
            return f"{order_book_id} {date} SUCCESS: {len(df)} ticks"
        else:
            return f"{order_book_id} {date} EMPTY"
            
    except Exception as e:
        return f"{order_book_id} {date} ERROR: {str(e)}"

def run_download():
    # 获取最近2个交易日（Tick数据量极大，先抓最近的）
    dates = get_latest_trading_dates(n=2)
    print(f"Targeting dates: {dates}")
    
    # 中金所股指期权标的
    underlying_symbols = ['IO', 'MO', 'HO']
    
    total_count = 0
    for date in dates:
        date_str = date.strftime('%Y-%m-%d')
        print(f"\n--- Processing date: {date_str} ---")
        
        for und in underlying_symbols:
            try:
                # 获取该标的下的所有活跃合约
                contracts = rqdatac.options.get_contracts(underlying=und, trading_date=date)
                print(f"Found {len(contracts)} contracts for {und} on {date_str}")
                
                # 串行下载，不启用多线程
                for contract in contracts:
                    res = download_tick_data(contract, date_str)
                    print(res)
                    total_count += 1
                    # 适当延时，保护账号
                    time.sleep(0.05) 
            except Exception as e:
                print(f"Error fetching contracts for {und} on {date_str}: {e}")

    print(f"\nTick download completed. Total tasks processed: {total_count}")

if __name__ == "__main__":
    run_download()
