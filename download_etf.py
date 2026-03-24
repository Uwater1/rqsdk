import rqdatac
import pandas as pd
import os

def download_300etf_prices():
    # Initialize rqdatac
    rqdatac.init()
    
    # 510300.XSHG is the Huatai-PineBridge CSI 300 ETF
    order_book_id = '510300.XSHG'
    
    # Get historical daily price data
    # Starting from a reasonable date for 300ETF options (2019-12-23 launch)
    start_date = '2019-01-01'
    end_date = pd.Timestamp.now().strftime('%Y-%m-%d')
    
    print(f"Downloading historical prices for {order_book_id} from {start_date} to {end_date}...")
    df = rqdatac.get_price(order_book_id, start_date=start_date, end_date=end_date, frequency='1d')
    
    if df is not None and not df.empty:
        # Save to parquet
        output_path = 'data/510300_1d.parquet'
        df.reset_index(inplace=True) # Ensure date is a column
        df.to_parquet(output_path)
        print(f"Successfully saved {len(df)} records to {output_path}")
    else:
        print("Failed to download price data.")

if __name__ == "__main__":
    download_300etf_prices()
