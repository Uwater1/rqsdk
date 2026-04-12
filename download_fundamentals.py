import os
import pandas as pd
import rqdatac
import logging
from tqdm import tqdm

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize RQData
rqdatac.init()

def convert_code(code):
    """Convert sh.XXXXXX / sz.XXXXXX to XXXXXX.XSHG / XXXXXX.XSHE"""
    if code.startswith('sh.'):
        return code[3:] + '.XSHG'
    elif code.startswith('sz.'):
        return code[3:] + '.XSHE'
    return code

def download_stock_fundamentals(code, name, fields, start_q, end_q, base_dir):
    """Download fundamental data for a single stock and save to basic/<code>_<name>/financials.csv"""
    standard_code = convert_code(code)
    # Ensure name is filesystem friendly
    safe_name = "".join([c for c in name if c.isalnum() or c in (' ', '_')]).rstrip()
    folder_name = f"{standard_code}_{safe_name}"
    stock_dir = os.path.join(base_dir, folder_name)
    os.makedirs(stock_dir, exist_ok=True)
    
    file_path = os.path.join(stock_dir, 'financials.csv')
    
    try:
        # Fetch Point-in-Time financial data
        df = rqdatac.get_pit_financials_ex(
            order_book_ids=standard_code,
            fields=fields,
            start_quarter=start_q,
            end_quarter=end_q
        )
        
        if df is not None and not df.empty:
            df.to_csv(file_path)
            # logging.info(f"Successfully saved {standard_code} ({name}) to {file_path}")
            return True
        else:
            # logging.warning(f"No fundamental data found for {standard_code} ({name}) from {start_q} to {end_q}")
            return False
            
    except Exception as e:
        logging.error(f"Error downloading {standard_code} ({name}): {e}")
        return False

def main():
    # 1. Load stock lists
    hs300_file = 'hs300_l.csv'
    zz500_file = 'zz500-l.csv'
    
    codes_to_download = []
    
    if os.path.exists(hs300_file):
        df_hs300 = pd.read_csv(hs300_file)
        codes_to_download.append(df_hs300[['code', 'code_name']])
        
    if os.path.exists(zz500_file):
        df_zz500 = pd.read_csv(zz500_file)
        codes_to_download.append(df_zz500[['code', 'code_name']])
        
    if not codes_to_download:
        logging.error("No stock list files found.")
        return
    
    all_stocks = pd.concat(codes_to_download).drop_duplicates('code')
    logging.info(f"Total unique stocks to download: {len(all_stocks)}")
    
    # 2. Define fields and time range
    # Comprehensive set of fields from the three main statements
    fields = [
        'revenue', 'operating_revenue', 'cost_of_goods_sold', 'operating_expense',
        'financing_expense', 'investment_income', 'net_profit', 'total_assets',
        'current_assets', 'total_liabilities', 'current_liabilities', 'total_equity',
        'net_fixed_assets', 'intangible_assets', 'inventory', 'net_accts_receivable',
        'notes_payable', 'undistributed_profit', 'cash_flow_from_operating_activities',
        'cash_flow_from_investing_activities', 'cash_flow_from_financing_activities'
    ]
    
    start_q = '2010q1'
    end_q = '2025q4'
    base_dir = 'basic'
    
    # 3. Create basic directory
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        
    # 4. Download and save loop
    success_count = 0
    for idx, row in tqdm(all_stocks.iterrows(), total=len(all_stocks), desc="Downloading Fundamentals"):
        if download_stock_fundamentals(row['code'], row['code_name'], fields, start_q, end_q, base_dir):
            success_count += 1
            
    logging.info(f"Download complete. Successfully downloaded {success_count}/{len(all_stocks)} stocks.")

if __name__ == "__main__":
    main()
