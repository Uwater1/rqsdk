import pandas as pd
import rqdatac
from datetime import datetime

def download_option_data(underlying='510300.XSHG', start_date='2015-01-01'):
    """
    下载指定标的的历史全量期权数据（包含已到期的合约）
    """
    try:
        # 1. 初始化
        rqdatac.init()

        # 2. 获取全量期权合约信息并筛选标的
        print(f"正在从全量合约库中筛选标的 {underlying} 的历史合约...")
        # 获取所有期权合约的基础信息 DataFrame
        all_options_df = rqdatac.all_instruments('Option')

        # 筛选 underlying_order_book_id 匹配的合约
        # 注意：不同版本字段名可能略有不同，通常为 underlying_order_book_id 或 underlying_symbol
        mask = (all_options_df['underlying_order_book_id'] == underlying) | (all_options_df['underlying_symbol'] == underlying)
        target_options_df = all_options_df[mask]

        if target_options_df.empty:
            print(f"未找到标的 {underlying} 的任何合约。")
            return

        all_instruments = target_options_df['order_book_id'].tolist()
        print(f"共找到 {len(all_instruments)} 个历史及当前挂牌合约。")

        # 保存合约信息
        target_options_df.to_csv(f"{underlying}_all_instruments_info.csv", index=False, encoding='utf-8-sig')
        print(f"全量合约信息已保存至: {underlying}_all_instruments_info.csv")

        # 3. 下载全量历史行情
        end_date = datetime.now().strftime('%Y-%m-%d')
        print(f"正在下载行情数据，起始日期: {start_date}...")

        # 建议分批获取以避免大数据量导致超时或内存溢出
        # 这里直接尝试批量获取，如果报错可以改为循环获取
        price_data = rqdatac.get_price(all_instruments, start_date=start_date, end_date=end_date, frequency='1d')

        if price_data is not None and not price_data.empty:
            price_data.to_csv(f"{underlying}_full_history_prices.csv", encoding='utf-8-sig')
            print(f"全量历史行情已保存至: {underlying}_full_history_prices.csv")
        else:
            print("未能获取到行情数据。")


        # 3. 下载历史行情 (获取最近一年的日线数据)
        end_date = datetime.now().strftime('%Y-%m-%d')
        print(f"正在下载 {len(all_instruments)} 个合约从 {start_date} 到 {end_date} 的行情...")
        
        # 使用 get_price 获取所有合约的行情数据
        # 批量获取通常返回多重索引 DataFrame
        price_data = rqdatac.get_price(all_instruments, start_date=start_date, end_date=end_date, frequency='1d')
        
        if price_data is not None and not price_data.empty:
            price_data.to_csv(f"{underlying}_historical_prices.csv", encoding='utf-8-sig')
            print(f"行情数据已保存至: {underlying}_historical_prices.csv")
        else:
            print("未能获取到行情数据。")

    except Exception as e:
        print(f"下载过程中出错: {e}")

if __name__ == "__main__":
    # 执行下载：默认下载沪深 300 ETF 期权
    download_option_data()