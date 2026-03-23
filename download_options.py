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

    for underlying, clean_name in underlying_map.items():
        print(f"Processing {underlying} -> {clean_name}")
        
        # Get instruments for this underlying
        instruments = df_opts[df_opts['underlying_symbol'] == underlying]
        if instruments.empty:
            print(f"  No instruments found for {underlying}")
            continue
            
        # Save instruments to parquet
        inst_file = f"{clean_name}_instruments.parquet"
        instruments.to_parquet(inst_file)
        print(f"  Saved {len(instruments)} instruments to {inst_file}")
        
        order_book_ids = instruments['order_book_id'].tolist()
        
        # Fetch historical daily prices for all these options
        # To avoid memory issues or API timeouts, we can fetch in chunks if necessary,
        # but 1d data for ~2000 contracts is usually small enough for a single call.
        try:
            prices = rqdatac.get_price(
                order_book_ids, 
                frequency='1d', 
                fields=['open_interest', 'prev_close', 'contract_multiplier', 'limit_up', 'volume', 'low', 'strike_price', 'prev_settlement', 'high', 'limit_down', 'day_session_open', 'total_turnover', 'settlement', 'open', 'close']
            )
            
            if prices is not None and not prices.empty:
                prices = prices.reset_index()
                price_file = f"{clean_name}_historical_prices.parquet"
                prices.to_parquet(price_file)
                print(f"  Saved {len(prices)} rows of historical prices to {price_file}")
            else:
                print(f"  No historical prices returned for {clean_name}")
        except Exception as e:
            print(f"  Error fetching prices for {clean_name}: {e}")

if __name__ == '__main__':
    main()
