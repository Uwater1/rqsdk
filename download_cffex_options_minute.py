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
    # 查找最近的交易日
    dates = rqdatac.get_trading_dates(start_date=end_date - timedelta(days=30), end_date=end_date)
    return sorted(dates, reverse=True)[:n]

def download_minute_data(order_book_id, date):
    """下载单个合约单日的分钟数据"""
    try:
        filename = f"{order_book_id}_{date}.parquet"
        filepath = os.path.join(SAVE_DIR, filename)
        
        if os.path.exists(filepath):
            return f"{order_book_id} {date} ALREADY EXISTS"
        
        # 获取1分钟线数据
        df = rqdatac.get_price(
            order_book_id, 
            start_date=date, 
            end_date=date, 
            frequency='1m',
            expect_df=True
        )
        
        if df is not None and not df.empty:
            df.to_parquet(filepath)
            return f"{order_book_id} {date} SUCCESS: {len(df)} bars"
        else:
            return f"{order_book_id} {date} EMPTY"
            
    except Exception as e:
        return f"{order_book_id} {date} ERROR: {str(e)}"

def run_download():
    # 获取最近5个交易日
    dates = get_latest_trading_dates(n=5)
    print(f"Targeting dates: {dates}")
    
    # 中金所股指期权标的
    underlying_symbols = ['IO', 'MO', 'HO']
    
    total_count = 0
    for date in dates:
        date_str = date.strftime('%Y-%m-%d')
        print(f"\n--- Processing date: {date_str} ---")
        
        for und in underlying_symbols:
            try:
                # 获取该标的下的所有合约
                contracts = rqdatac.options.get_contracts(underlying=und, trading_date=date)
                print(f"Found {len(contracts)} contracts for {und} on {date_str}")
                
                for contract in contracts:
                    res = download_minute_data(contract, date_str)
                    print(res)
                    total_count += 1
                    # 适当延时，避免触发频率限制
                    time.sleep(0.1) 
            except Exception as e:
                print(f"Error fetching contracts for {und} on {date_str}: {e}")

    print(f"\nDownload completed. Total tasks processed: {total_count}")

if __name__ == "__main__":
    run_download()
