import rqdatac
import os
import pandas as pd
from datetime import datetime, timedelta
import concurrent.futures
import time

# 初始化
rqdatac.init()

# 设置保存路径
SAVE_DIR = "data-deep"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

def get_latest_trading_dates(n=5):
    """获取最近n个交易日"""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=n*3)  # 多给点范围，因为中间可能有周末
    dates = rqdatac.get_trading_dates(start_date=start_date, end_date=end_date)
    return sorted(dates, reverse=True)[:n]

def download_tick(order_book_id, date):
    """下载单个合约单日的Tick数据"""
    try:
        # 文件名：data-deep/order_book_id_date.parquet
        filename = f"{order_book_id}_{date}.parquet"
        filepath = os.path.join(SAVE_DIR, filename)
        
        # 检查是否已存在
        if os.path.exists(filepath):
            return f"{order_book_id} {date} ALREADY EXISTS"
        
        # 获取Tick数据
        df = rqdatac.get_price(
            order_book_id, 
            start_date=date, 
            end_date=date, 
            frequency='tick',
            expect_df=True
        )
        
        if df is not None and not df.empty:
            # 确保保存为parquet
            df.to_parquet(filepath)
            return f"{order_book_id} {date} SUCCESS: {len(df)} ticks"
        else:
            return f"{order_book_id} {date} EMPTY"
            
    except Exception as e:
        return f"{order_book_id} {date} ERROR: {str(e)}"

def batch_download():
    # 获取最近5个交易日
    dates = get_latest_trading_dates(n=5)
    print(f"Targeting dates: {dates}")
    
    all_tasks = []
    
    # 获取所有的期权合约
    underlying_symbols = [
        '510050.XSHG', '510300.XSHG', '510500.XSHG', '159919.XSHE', '159915.XSHE',
        'IO', 'MO', 'HO'
    ]
    
    for date in dates:
        date_str = date.strftime('%Y-%m-%d')
        print(f"Fetching contracts for {date_str}...")
        
        # 针对每个标的获取合约
        for und in underlying_symbols:
            try:
                contracts = rqdatac.options.get_contracts(underlying=und, trading_date=date)
                for contract in contracts:
                    all_tasks.append((contract, date_str))
            except Exception as e:
                print(f"Error fetching contracts for {und} on {date_str}: {e}")
                
    print(f"Total tasks to download: {len(all_tasks)}")
    
    # 使用多线程下载，控制并发数，避免账号被封
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_to_task = {executor.submit(download_tick_with_retry, task[0], task[1]): task for task in all_tasks}
        
        for future in concurrent.futures.as_completed(future_to_task):
            res = future.result()
            print(res)

def download_tick_with_retry(order_book_id, date, retries=3):
    """带重试的下载逻辑"""
    for i in range(retries):
        res = download_tick(order_book_id, date)
        if "ERROR: connection number exceeds" in res:
            wait_time = (i + 1) * 2
            print(f"Connection limit hit for {order_book_id}, waiting {wait_time}s...")
            time.sleep(wait_time)
            continue
        return res
    return f"{order_book_id} {date} FAILED after {retries} retries"

if __name__ == "__main__":
    batch_download()
