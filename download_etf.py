import rqdatac
import pandas as pd
import os

def download_all_underlying_prices():
    # Initialize rqdatac
    rqdatac.init()

    # Define the same mapping as in download_options.py
    underlying_map = {
        '510050.XSHG': '50ETF',
        '510300.XSHG': '300ETF',
        '510500.XSHG': '500ETF',
        '588000.XSHG': 'STAR50',
        '588080.XSHG': 'STAR50_E',
        '159919.XSHE': '300ETF_SZ',
        '159915.XSHE': 'ChiNextETF',
        '159922.XSHE': '500ETF_SZ',
        '159901.XSHE': 'SZ100ETF',
        'HO': 'HO',
        'IO': 'IO',
        'MO': 'MO'
    }

    # Setting a broad start date to capture full history
    start_date = '2015-01-01'
    end_date = pd.Timestamp.now().strftime('%Y-%m-%d')

    for symbol, clean_name in underlying_map.items():
        print(f"Downloading historical prices for {symbol} ({clean_name})...")
        try:
            df = rqdatac.get_price(symbol, start_date=start_date, end_date=end_date, frequency='1d')
            
            if df is not None and not df.empty:
                # Save to both Parquet (for analysis) and CSV (as requested)
                parquet_path = f'data/{clean_name}_1d.parquet'
                csv_path = f'data/{clean_name}_1d.csv'
                
                df.reset_index(inplace=True) # Ensure date/order_book_id is a column
                
                # Save Parquet
                df.to_parquet(parquet_path)
                # Save CSV
                df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                
                print(f"  Successfully saved {len(df)} records to {parquet_path} and {csv_path}")
            else:
                print(f"  No price data returned for {symbol}.")
        except Exception as e:
            print(f"  Error downloading {symbol}: {e}")

if __name__ == "__main__":
    download_all_underlying_prices()
