import os
import rqdatac
import pandas as pd
from datetime import datetime

# Initialize rqdatac
rqdatac.init()

# Define date range for maximum history
START_DATE = "2005-01-01"
END_DATE = datetime.now().strftime("%Y-%m-%d")

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def save_data(df, path, format='csv'):
    if df is None or df.empty:
        return
    if format == 'parquet':
        try:
            df.to_parquet(path.replace('.csv', '.parquet'), engine='pyarrow', compression='snappy')
        except Exception as e:
            print(f"    Error saving parquet to {path}: {e}. Falling back to CSV.")
            df.to_csv(path)
    else:
        df.to_csv(path)

def download_market_data():
    print("Downloading Market Data...")
    
    # 1. Macro Economy
    macro_dir = os.path.join("basic", "macro")
    ensure_dir(macro_dir)
    
    try:
        print("  Fetching Reserve Ratio...")
        df_rr = rqdatac.econ.get_reserve_ratio(start_date=START_DATE, end_date=END_DATE)
        save_data(df_rr, os.path.join(macro_dir, "reserve_ratio.csv"))
    except Exception as e:
        print(f"  Error fetching reserve ratio: {e}")

    try:
        print("  Fetching Money Supply...")
        df_ms = rqdatac.econ.get_money_supply(start_date=START_DATE, end_date=END_DATE)
        save_data(df_ms, os.path.join(macro_dir, "money_supply.csv"))
    except Exception as e:
        print(f"  Error fetching money supply: {e}")

    # 2. Repo (Shibor)
    repo_dir = os.path.join("basic", "repo")
    ensure_dir(repo_dir)
    try:
        print("  Fetching Interbank Offered Rate (Shibor)...")
        df_shibor = rqdatac.get_interbank_offered_rate(start_date=START_DATE, end_date=END_DATE)
        save_data(df_shibor, os.path.join(repo_dir, "shibor.csv"))
    except Exception as e:
        print(f"  Error fetching shibor: {e}")

    # 3. VIX Index
    vix_dir = os.path.join("basic", "vix")
    ensure_dir(vix_dir)
    vix_codes = [f"VX00{i:02d}.RI" for i in range(1, 13)]
    for vix_code in vix_codes:
        try:
            print(f"  Fetching VIX Index: {vix_code}...")
            df_vix = rqdatac.get_price(vix_code, start_date=START_DATE, end_date=END_DATE)
            save_data(df_vix, os.path.join(vix_dir, f"{vix_code}.csv"))
        except Exception as e:
            print(f"  Error fetching VIX {vix_code}: {e}")

def download_stock_data():
    print("Downloading Stock-Specific Data (Large files will use Parquet)...")
    
    # Get all stock directories in basic/
    stock_dirs = sorted([d for d in os.listdir("basic") if os.path.isdir(os.path.join("basic", d)) and "_" in d])
    
    # For ESG and News, they require extra packages
    try:
        import rqdatac_news
    except ImportError:
        rqdatac_news = None
        print("Warning: rqdatac_news not installed. Skipping news data.")

    try:
        import rqdatac_esg
    except ImportError:
        rqdatac_esg = None
        print("Warning: rqdatac_esg not installed. Skipping ESG data.")

    for stock_dir in stock_dirs:
        order_book_id = stock_dir.split("_")[0]
        full_path = os.path.join("basic", stock_dir)
        print(f"  Processing stock: {order_book_id} ({stock_dir})...")

        # 1. Risk Factors (Likely large)
        try:
            # Factor Exposure
            df_exposure = rqdatac.get_factor_exposure(order_book_id, start_date=START_DATE, end_date=END_DATE)
            save_data(df_exposure, os.path.join(full_path, "factor_exposure.csv"), format='parquet')

            # Stock Beta
            df_beta = rqdatac.get_stock_beta(order_book_id, start_date=START_DATE, end_date=END_DATE)
            save_data(df_beta, os.path.join(full_path, "stock_beta.csv"))

            # Specific Return
            df_spec_ret = rqdatac.get_specific_return(order_book_id, start_date=START_DATE, end_date=END_DATE)
            save_data(df_spec_ret, os.path.join(full_path, "specific_return.csv"))

            # Specific Risk
            df_spec_risk = rqdatac.get_specific_risk(order_book_id, start_date=START_DATE, end_date=END_DATE)
            save_data(df_spec_risk, os.path.join(full_path, "specific_risk.csv"))
        except Exception as e:
            print(f"    Error fetching risk factors for {order_book_id}: {e}")

        # 2. Alternative Data (Consensus)
        try:
            # Comp Indicators (Likely large)
            df_comp = rqdatac.consensus.get_comp_indicators(order_book_id, start_date=START_DATE, end_date=END_DATE)
            save_data(df_comp, os.path.join(full_path, "consensus_comp_indicators.csv"), format='parquet')

            # Forecast Prices
            df_price = rqdatac.consensus.get_price(order_book_id, start_date=START_DATE, end_date=END_DATE)
            save_data(df_price, os.path.join(full_path, "consensus_forecast_price.csv"))

            # Expectation Probability (Exceed/Below)
            try:
                df_exceed = rqdatac.consensus.get_expect_prob(order_book_id, expect_prob='exceed', start_date=START_DATE, end_date=END_DATE)
                save_data(df_exceed, os.path.join(full_path, "consensus_expect_exceed.csv"))
                
                df_below = rqdatac.consensus.get_expect_prob(order_book_id, expect_prob='below', start_date=START_DATE, end_date=END_DATE)
                save_data(df_below, os.path.join(full_path, "consensus_expect_below.csv"))
            except:
                pass

            # Analyst Momentum
            df_momentum = rqdatac.consensus.get_analyst_momentum(order_book_id, start_date=START_DATE, end_date=END_DATE)
            save_data(df_momentum, os.path.join(full_path, "consensus_analyst_momentum.csv"))
        except Exception as e:
            print(f"    Error fetching consensus data for {order_book_id}: {e}")

        # 3. Alternative Data (News - Likely large)
        if rqdatac_news:
            try:
                df_news = rqdatac.news.get_stock_news(order_book_id, start_date=START_DATE, end_date=END_DATE)
                save_data(df_news, os.path.join(full_path, "news.csv"), format='parquet')
            except Exception as e:
                print(f"    Error fetching news for {order_book_id}: {e}")

        # 4. Alternative Data (ESG)
        if rqdatac_esg:
            try:
                df_esg = rqdatac.esg.get_rating(order_book_id, start_date=START_DATE, end_date=END_DATE)
                save_data(df_esg, os.path.join(full_path, "esg.csv"))
            except Exception as e:
                print(f"    Error fetching ESG for {order_book_id}: {e}")

if __name__ == "__main__":
    download_market_data()
    download_stock_data()
    print("Data download completed.")
