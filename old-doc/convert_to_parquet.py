import os
import pandas as pd

def convert_dir(base_dir):
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.csv') and any(keyword in file for keyword in [
                'consensus', 'factor', 'specific', 'stock_beta', 'news', 'esg'
            ]):
                csv_path = os.path.join(root, file)
                parquet_path = csv_path.replace('.csv', '.parquet')
                try:
                    print(f"Converting {csv_path}...")
                    df = pd.read_csv(csv_path)
                    if not df.empty:
                        df.to_parquet(parquet_path, engine='pyarrow', compression='snappy')
                    os.remove(csv_path)
                except Exception as e:
                    print(f"Error converting {csv_path}: {e}")

if __name__ == "__main__":
    convert_dir('basic')
