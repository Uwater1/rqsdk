import os
import pandas as pd
import rqdatac
import logging
from tqdm import tqdm
from datetime import datetime

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

def safe_getattr(obj, attr, default='N/A'):
    val = getattr(obj, attr, default)
    return val if val is not None else default

def format_number(val):
    if val is None or pd.isna(val):
        return 'N/A'
    if val >= 1e8:
        return f"{val/1e8:.2f} 亿"
    if val >= 1e4:
        return f"{val/1e4:.2f} 万"
    return str(val)

def process_batch(batch_stocks, base_dir):
    codes = [convert_code(row['code']) for _, row in batch_stocks.iterrows()]
    code_to_name = {convert_code(row['code']): row['code_name'] for _, row in batch_stocks.iterrows()}
    
    # 1. Fetch data in bulk
    try:
        instruments_list = rqdatac.instruments(codes)
        # Convert list to dict for easier access
        instruments_dict = {inst.order_book_id: inst for inst in instruments_list}
        
        # Latest shares
        shares_df = rqdatac.get_shares(codes)
        
        # Name changes
        name_changes_df = rqdatac.get_symbol_change_info(codes)
        
        # Top shareholders (latest)
        # get_main_shareholder might return a lot of data if we don't restrict. 
        # Usually we want the latest report date's top 10.
        shareholders_df = rqdatac.get_main_shareholder(codes)
        
        # Staff count
        staff_df = rqdatac.get_staff_count(codes)
        
    except Exception as e:
        logging.error(f"Error fetching bulk data: {e}")
        return

    for code in codes:
        name = code_to_name.get(code, "Unknown")
        safe_name = "".join([c for c in name if c.isalnum() or c in (' ', '_')]).rstrip()
        folder_name = f"{code}_{safe_name}"
        stock_dir = os.path.join(base_dir, folder_name)
        os.makedirs(stock_dir, exist_ok=True)
        
        file_path = os.path.join(stock_dir, 'introduction.md')
        
        inst = instruments_dict.get(code)
        if not inst:
            continue
            
        # Build Markdown content
        lines = []
        lines.append(f"# 企业详细介绍: {inst.symbol} ({code})")
        lines.append("")
        
        lines.append("## 1. 基本信息")
        lines.append(f"- **股票代码**: {code}")
        lines.append(f"- **股票简称**: {inst.symbol}")
        lines.append(f"- **拼音简称**: {safe_getattr(inst, 'abbrev_symbol')}")
        lines.append(f"- **上市日期**: {inst.listed_date}")
        lines.append(f"- **上市交易所**: {inst.exchange}")
        lines.append(f"- **板块**: {safe_getattr(inst, 'board_type')}")
        lines.append(f"- **状态**: {inst.status}")
        lines.append(f"- **发行价格**: {safe_getattr(inst, 'issue_price')} 元")
        lines.append(f"- **每手股数**: {safe_getattr(inst, 'round_lot')}")
        lines.append("")
        
        lines.append("## 2. 行业与分类")
        lines.append(f"- **所属行业 (证监会)**: {safe_getattr(inst, 'industry_name')}")
        lines.append(f"- **所属行业 (中信)**: {safe_getattr(inst, 'citics_industry_name')}")
        lines.append(f"- **所属大板块**: {safe_getattr(inst, 'sector_code_name')}")
        lines.append(f"- **相关概念标签**: {safe_getattr(inst, 'concept_names')}")
        lines.append("")
        
        lines.append("## 3. 股本结构 (最新公开数据)")
        if not shares_df.empty and code in shares_df.index.get_level_values(0):
            stock_shares = shares_df.xs(code, level=0).iloc[-1]
            lines.append(f"- **总股本**: {format_number(stock_shares.get('total'))}")
            lines.append(f"- **流通A股**: {format_number(stock_shares.get('circulation_a'))}")
            lines.append(f"- **自由流通股本**: {format_number(stock_shares.get('free_circulation'))}")
        else:
            lines.append("- 暂无股本数据记录")
        lines.append("")
        
        lines.append("## 4. 前十大股东 (最新报告期)")
        if not shareholders_df.empty and code in shareholders_df.index.get_level_values(0):
            stock_holders = shareholders_df.xs(code, level=0)
            # Get latest info_date
            latest_info_date = stock_holders.index.max()
            latest_holders = stock_holders.loc[latest_info_date]
            if isinstance(latest_holders, pd.Series): # Just one holder (unlikely but possible)
                latest_holders = pd.DataFrame([latest_holders])
            
            latest_holders = latest_holders.sort_values('rank')
            lines.append("| 排名 | 股东名称 | 持股比例 (%) |")
            lines.append("| :--- | :--- | :--- |")
            for _, holder in latest_holders.iterrows():
                lines.append(f"| {holder['rank']} | {holder['shareholder_name']} | {holder['hold_percent_float']:.2f}% |")
        else:
            lines.append("- 暂无股东数据记录")
        lines.append("")
        
        lines.append("## 5. 证券简称变更历史")
        if not name_changes_df.empty and code in name_changes_df.index.get_level_values(0):
            changes = name_changes_df.xs(code, level=0).reset_index()
            lines.append("| 变更日期 | 证券简称 |")
            lines.append("| :--- | :--- |")
            for _, change in changes.iterrows():
                lines.append(f"| {change['change_date']} | {change['symbol']} |")
        else:
            lines.append("- 暂无名称变更记录")
        lines.append("")
        
        lines.append("## 6. 公司运营信息")
        lines.append(f"- **办公地址**: {safe_getattr(inst, 'office_address')}")
        lines.append(f"- **所在省份**: {safe_getattr(inst, 'province')}")
        
        if not staff_df.empty and code in staff_df.index.get_level_values(0):
            latest_staff = staff_df.xs(code, level=0).iloc[-1]
            lines.append(f"- **员工总数**: {latest_staff['staff_count']} (截至 {latest_staff['end_date']})")
        else:
            lines.append("- **员工总数**: 暂无数据")
            
        lines.append("")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))

def main():
    # 1. Load stock lists
    hs300_file = 'hs300_l.csv'
    zz500_file = 'zz500-l.csv'
    
    codes_to_process = []
    if os.path.exists(hs300_file):
        codes_to_process.append(pd.read_csv(hs300_file)[['code', 'code_name']])
    if os.path.exists(zz500_file):
        codes_to_process.append(pd.read_csv(zz500_file)[['code', 'code_name']])
        
    all_stocks = pd.concat(codes_to_process).drop_duplicates('code')
    logging.info(f"Total unique stocks to process: {len(all_stocks)}")
    
    base_dir = 'basic'
    batch_size = 50 # Small batch size to handle potential API timeouts or limits
    
    # 2. Process in batches
    for i in tqdm(range(0, len(all_stocks), batch_size), desc="Processing Batches"):
        batch = all_stocks.iloc[i:i+batch_size]
        process_batch(batch, base_dir)
            
    logging.info("Detailed introductions update complete.")

if __name__ == "__main__":
    main()
