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

def write_introduction(code, name, base_dir):
    """Fetch company basic info and write to introduction.md"""
    standard_code = convert_code(code)
    # Ensure name is filesystem friendly
    safe_name = "".join([c for c in name if c.isalnum() or c in (' ', '_')]).rstrip()
    folder_name = f"{standard_code}_{safe_name}"
    stock_dir = os.path.join(base_dir, folder_name)
    
    # We expect the folder to exist from previous step, but let's be safe
    os.makedirs(stock_dir, exist_ok=True)
    
    file_path = os.path.join(stock_dir, 'introduction.md')
    
    try:
        info = rqdatac.instruments(standard_code)
        if info is None:
            logging.warning(f"No info found for {standard_code}")
            return False
            
        content = f"""# 企业介绍: {info.symbol} ({info.order_book_id})

## 基本信息
- **股票代码**: {info.order_book_id}
- **股票简称**: {info.symbol}
- **拼音简称**: {getattr(info, 'abbrev_symbol', 'N/A')}
- **上市日期**: {info.listed_date}
- **上市交易所**: {info.exchange}
- **板块**: {getattr(info, 'board_type', 'N/A')}
- **状态**: {info.status}

## 行业与业务
- **所属行业 (证监会)**: {getattr(info, 'industry_name', 'N/A')}
- **所属行业 (中信)**: {getattr(info, 'citics_industry_name', 'N/A')}
- **所属板块**: {getattr(info, 'sector_code_name', 'N/A')}
- **相关概念**: {getattr(info, 'concept_names', 'N/A')}

## 公司联系方式
- **办公地址**: {getattr(info, 'office_address', 'N/A')}
- **所在省份**: {getattr(info, 'province', 'N/A')}

---
*数据来源: Ricequant (RQData)*
"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
            
    except Exception as e:
        logging.error(f"Error writing introduction for {standard_code}: {e}")
        return False

def main():
    # 1. Load stock lists
    hs300_file = 'hs300_l.csv'
    zz500_file = 'zz500-l.csv'
    
    codes_to_process = []
    
    if os.path.exists(hs300_file):
        df_hs300 = pd.read_csv(hs300_file)
        codes_to_process.append(df_hs300[['code', 'code_name']])
        
    if os.path.exists(zz500_file):
        df_zz500 = pd.read_csv(zz500_file)
        codes_to_process.append(df_zz500[['code', 'code_name']])
        
    if not codes_to_process:
        logging.error("No stock list files found.")
        return
    
    all_stocks = pd.concat(codes_to_process).drop_duplicates('code')
    logging.info(f"Total unique stocks to process: {len(all_stocks)}")
    
    base_dir = 'basic'
    
    # 2. Process loop
    success_count = 0
    for idx, row in tqdm(all_stocks.iterrows(), total=len(all_stocks), desc="Writing Introductions"):
        if write_introduction(row['code'], row['code_name'], base_dir):
            success_count += 1
            
    logging.info(f"Process complete. Successfully wrote {success_count}/{len(all_stocks)} introductions.")

if __name__ == "__main__":
    main()
