import pandas as pd
import rqdatac
from datetime import datetime

def download_option_data(underlying='510300.XSHG', start_date='2018-10-01', output_dir='data'):
    """
    下载指定期权标的的历史行情及合约信息并保存到本地
    """
    try:
        # 1. 初始化
        # 提示：如果没配置环境变量，请手动传入 init(username='...', password='...')
        rqdatac.init()
        
        # 2. 获取合约基本信息
        print(f"正在拉取标的 {underlying} 的所有历史及当前挂牌合约信息...")
        all_instruments = rqdatac.options.get_contracts(underlying)
        if not all_instruments:
            print("未找到有效合约，请检查标的代码。")
            return
            
        # 修正：rqdatac.instruments 返回的是对象列表，需转换为 DataFrame
        instruments_list = rqdatac.instruments(all_instruments)
        # 将对象属性提取为字典列表
        instruments_data = [inst.__dict__ for inst in instruments_list if inst is not None]
        instruments_df = pd.DataFrame(instruments_data)
        
        if not instruments_df.empty:
            instruments_df.to_csv(f"{underlying}_instruments.csv", index=False, encoding='utf-8-sig')
            print(f"合约基础信息已保存至: {underlying}_instruments.csv")
        else:
            print("未能获取到有效的合约详细信息。")

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