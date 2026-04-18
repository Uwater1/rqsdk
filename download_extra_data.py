import os
import rqdatac
import pandas as pd
from datetime import datetime

# Initialize rqdatac
rqdatac.init()

# Define date range for maximum history
START_DATE = "2015-01-01"
END_DATE = datetime.now().strftime("%Y-%m-%d")

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def save_data(df, path, format='csv'):
    if df is None or df.empty:
        return
    if format == 'parquet':
        final_path = path.replace('.csv', '.parquet')
        try:
            df.to_parquet(final_path, engine='pyarrow', compression='snappy')
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            print(f"    Error saving parquet to {final_path}: {e}. Falling back to CSV.")
            df.to_csv(path)
    else:
        df.to_csv(path)

def download_stock_data():
    print("Downloading Stock-Specific Data (Incremental & Parquet)...")
    
    stock_dirs = sorted([d for d in os.listdir("basic") if os.path.isdir(os.path.join("basic", d)) and "_" in d])
    
    try:
        import rqdatac_news
    except ImportError:
        rqdatac_news = None

    try:
        import rqdatac_esg
    except ImportError:
        rqdatac_esg = None

    for stock_dir in stock_dirs:
        order_book_id = stock_dir.split("_")[0]
        full_path = os.path.join("basic", stock_dir)
        print(f"  Processing stock: {order_book_id}...")

        # 1. Risk Factors
        files_to_fetch = {
            "factor_exposure.parquet": (rqdatac.get_factor_exposure, {}),
            "stock_beta.parquet": (rqdatac.get_stock_beta, {}),
            "specific_return.parquet": (rqdatac.get_specific_return, {}),
            "specific_risk.parquet": (rqdatac.get_specific_risk, {}),
        }
        
        for filename, (func, kwargs) in files_to_fetch.items():
            if not os.path.exists(os.path.join(full_path, filename)):
                try:
                    df = func(order_book_id, start_date=START_DATE, end_date=END_DATE, **kwargs)
                    save_data(df, os.path.join(full_path, filename.replace('.parquet', '.csv')), format='parquet')
                except Exception as e:
                    print(f"    Error fetching {filename} for {order_book_id}: {e}")

        # 2. Alternative Data (Consensus)
        consensus_files = {
            "consensus_comp_indicators.parquet": rqdatac.consensus.get_comp_indicators,
            "consensus_forecast_price.parquet": rqdatac.consensus.get_price,
            "consensus_analyst_momentum.parquet": rqdatac.consensus.get_analyst_momentum,
        }
        for filename, func in consensus_files.items():
            if not os.path.exists(os.path.join(full_path, filename)):
                try:
                    df = func(order_book_id, start_date=START_DATE, end_date=END_DATE)
                    save_data(df, os.path.join(full_path, filename.replace('.parquet', '.csv')), format='parquet')
                except Exception as e:
                    print(f"    Error fetching {filename} for {order_book_id}: {e}")

        # Expectation Prob
        if not os.path.exists(os.path.join(full_path, "consensus_expect_exceed.parquet")):
            try:
                df = rqdatac.consensus.get_expect_prob(order_book_id, expect_prob='exceed', start_date=START_DATE, end_date=END_DATE)
                save_data(df, os.path.join(full_path, "consensus_expect_exceed.csv"), format='parquet')
            except: pass
        if not os.path.exists(os.path.join(full_path, "consensus_expect_below.parquet")):
            try:
                df = rqdatac.consensus.get_expect_prob(order_book_id, expect_prob='below', start_date=START_DATE, end_date=END_DATE)
                save_data(df, os.path.join(full_path, "consensus_expect_below.csv"), format='parquet')
            except: pass

        # 3. Alternative Data (News)
        if rqdatac_news and not os.path.exists(os.path.join(full_path, "news.parquet")):
            try:
                df = rqdatac.news.get_stock_news(order_book_id, start_date=START_DATE, end_date=END_DATE)
                save_data(df, os.path.join(full_path, "news.csv"), format='parquet')
            except Exception as e:
                print(f"    Error fetching news for {order_book_id}: {e}")

        # 4. Alternative Data (ESG)
        if rqdatac_esg and not os.path.exists(os.path.join(full_path, "esg.parquet")):
            try:
                df = rqdatac.esg.get_rating(order_book_id, start_date=START_DATE, end_date=END_DATE)
                save_data(df, os.path.join(full_path, "esg.csv"), format='parquet')
            except Exception as e:
                print(f"    Error fetching ESG for {order_book_id}: {e}")

if __name__ == "__main__":
    download_stock_data()
    print("Data download completed.")
