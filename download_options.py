import rqdatac
import pandas as pd

def main():
    rqdatac.init()

    # Mapping of underlying symbol to clean names for stock-linked options
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

    # Fetch all option instruments
    df_opts = rqdatac.all_instruments('Option')
    
    # Filter by listed_date (optional, but safe)
    # df_opts = df_opts[df_opts.listed_date <= '2026-03-23']

    # Define the start date to get as much data as possible (2015 is when ETF options started)
    start_date = '2015-01-01'
    end_date = pd.Timestamp.today().strftime('%Y-%m-%d')

    for underlying, clean_name in underlying_map.items():
        print(f"Processing {underlying} -> {clean_name}")
        
        # Get instruments for this underlying
        instruments = df_opts[df_opts['underlying_symbol'] == underlying]
        if instruments.empty:
            print(f"  No instruments found for {underlying}")
            continue
            
        # Save instruments to parquet
        inst_file = f"data/{clean_name}_instruments.parquet"
        instruments.to_parquet(inst_file)
        print(f"  Saved {len(instruments)} instruments to {inst_file}")
        
        order_book_ids = instruments['order_book_id'].tolist()
        
        # Fetch historical daily prices for all these options
        try:
            prices = rqdatac.get_price(
                order_book_ids, 
                start_date=start_date,
                end_date=end_date,
                frequency='1d', 
                fields=['open_interest', 'prev_close', 'contract_multiplier', 'limit_up', 'volume', 'low', 'strike_price', 'prev_settlement', 'high', 'limit_down', 'day_session_open', 'total_turnover', 'settlement', 'open', 'close']
            )
            
            if prices is not None and not prices.empty:
                prices = prices.reset_index()
                price_file = f"data/{clean_name}_historical_prices.parquet"
                prices.to_parquet(price_file)
                print(f"  Saved {len(prices)} rows of historical prices to {price_file}")
            else:
                print(f"  No historical prices returned for {clean_name}")
        except Exception as e:
            print(f"  Error fetching prices for {clean_name}: {e}")

if __name__ == '__main__':
    main()
