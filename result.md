# Ricequant 期权数据获取与本地化研究结论

## 1. 期权数据获取核心 API
根据 `GEMINI.md` 指引及官方文档，主要数据接口如下：

| 数据类型 | 推荐 API | 返回格式 | 关键字段/说明 |
| :--- | :--- | :--- | :--- |
| **合约查询** | `options.get_contracts()` | `list` | 根据标的、到期日、行权价筛选合约 ID |
| **基础信息** | `instruments()` | `Instrument` 对象 | 上市/到期日、行权价、合约乘数、行权方式 |
| **历史行情** | `get_price()` | `DataFrame` | 开高低收、成交量、持仓量、结算价、行权价 |
| **希腊字母** | `options.get_greeks()` | `DataFrame` | IV, Delta, Gamma, Vega, Theta, Rho |
| **衍生指标** | `options.get_indicators()`| `DataFrame` | PCR (成交/持仓比), Skew (偏度) |
| **当日快照** | `current_snapshot()` | `Snapshot` | 最新价、买卖盘、当日最高/最低 |

## 2. 本地化下载方案
`rqdatac` 的设计理念是“按需获取”，数据以 `pandas.DataFrame` 格式驻留在内存中。用户可以通过以下方式将其保存到本地：

- **标准格式**：
  - `df.to_csv('path/to/file.csv')`：通用性最强。
  - `df.to_excel('path/to/file.xlsx')`：适合人工查看。
- **专业格式（推荐）**：
  - `df.to_parquet('data.parquet')`：适合分钟线/Tick 等大数据量，存储效率最高。
  - `df.to_pickle('data.pkl')`：完整保留 DataFrame 类型信息。
  - `df.to_hdf('data.h5', key='key')`：适合构建本地多维数据库。

## 3. 开发建议
1. **先初始化**：在获取任何数据前，必须执行 `rqdatac.init()`。
2. **频率选择**：获取历史行情时，通过 `frequency` 参数指定 `'1d'` (日线), `'1m'` (分钟) 或 `'tick'`。
3. **分红调整**：对于 ETF 期权，建议配合 `options.get_contract_property()` 追踪因标的分红导致的合约属性变动。
4. **项目参考**：项目中 `examples/option_buy_and_hold.py` 提供了期权交易的基本逻辑参考。
