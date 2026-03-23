import pandas as pd
import rqdatac
from typing import List, Union

def get_option_snapshot_to_csv(underlying: str = '510300.XSHG', filename: str = 'snapshot.csv'):
    """
    获取指定标的的期权合约当日快照并保存到本地 CSV
    """
    try:
        # 1. 初始化 (如果不带参数，rqdatac 会尝试读取本地配置文件 rqdatac.yaml 或环境变量)
        rqdatac.init()
        
        # 2. 获取当前挂牌的期权合约列表
        print(f"正在获取标的 {underlying} 的合约列表...")
        contracts = rqdatac.options.get_contracts(underlying)
        if not contracts:
            print("未找到有效合约。")
            return

        # 3. 获取合约快照
        print(f"正在拉取 {len(contracts)} 个合约的当日快照...")
        snapshots = rqdatac.current_snapshot(contracts)
        
        # 4. 数据转换：Snapshot 对象转为 DataFrame
        # current_snapshot 通常返回 Snapshot 对象列表或单个对象
        if not isinstance(snapshots, list):
            snapshots = [snapshots]
            
        data_list = []
        for snp in snapshots:
            # 提取内部的 _data 字典以获得平铺的列（datetime, open, high 等）
            if hasattr(snp, '_data'):
                data_list.append(snp._data)
            else:
                # 兼容性处理
                data_list.append(snp.__dict__)
        
        df = pd.DataFrame(data_list)
        
        # 5. 数据清洗：移除大部分市场数据字段均为 nan 的行（如未开市或无交易的合约）
        # 排除掉元数据列，然后检查剩余列是否全为 NaN
        if not df.empty:
            metadata_cols = {'datetime', 'order_book_id', 'trading_date', 'trading_phase_code'}
            data_cols = [c for c in df.columns if c not in metadata_cols]
            df = df.dropna(subset=data_cols, how='all')
        
        # 6. 保存到本地
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"成功！已保存平铺且过滤后的快照数据至: {filename}")
        
    except Exception as e:
        print(f"操作失败: {e}")

if __name__ == "__main__":
    # 请确保已配置凭据，或在此手动指定：
    # rqdatac.init(username='your_user', password='your_password')
    get_option_snapshot_to_csv()
