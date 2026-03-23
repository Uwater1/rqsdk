# 因子计算

## execute_factor

``` python
execute_factor(factor, order_book_ids, start_date, end_date, universe=None)
```

#### 参数

| 参数名         | 说明        |
| --------------|------------|
| factor          | 需要计算的因子 |
| order_book_ids       | 需要计算的股票列表        |
| start_date |开始计算时间，支持字符串, `datetime.date`, `datetime.datetime`, `pd.Timestamp`|
|end_date|结束计算时间，支持字符串, `datetime.date`, `datetime.datetime`, `pd.Timestamp`|
|universe|指定参与计算的股票池，默认为 `None`；支持指数代码及 `None`，`None` 表示全市场|


## CachedExecContext.init

您可能需要：在初始化阶段缓存一些必要数据，大量计算因子的时候可以从缓存读取数据，而不需要每次重新从 rqdatac 调取数据。<br>缓存数据包括: 日行情因子 (默认后复权) ，财务因子，ALpha101 因子，技术指标。<br>如无指定，则仅会加载后复权的日行情因子 (open，close，high，low，total_turnover，volume，num_trades)。<br>初始化：

``` python
CachedExecContext.init(order_book_ids, start_date, end_date, leaves=None, universes=None)
```

#### 参数

| 参数名         | 说明        |
| --------------|------------|
| order_book_ids       | 需要计算的股票列表        |
| start_date |开始计算时间，支持字符串, `datetime.date`, `datetime.datetime`, `pd.Timestamp`；`start_date`应不晚于因子值的开始计算日期+因子的最长回望周期|
|end_date|结束计算时间，支持字符串, `datetime.date`, `datetime.datetime`, `pd.Timestamp`|
|leaves|用于指定初始化的叶子因子列表，如果不指定则默认包含所有日级别行情因子|
|universes|指定需要缓存的 universe 列表，避免每次计算重新调取|


## 范例

```python
from rqfactor.engine_v2 import execute_factor
from rqfactor.engine_v2 import CachedExecContext
from rqfactor import *
from rqdatac import *
init()

start_date, end_date = 20231201,20240101
order_book_ids = ['000001.XSHE','000002.XSHE']
leaves = ['pe_ratio',]
#初始化
CachedExecContext.init(order_book_ids, start_date, end_date,  leaves=leaves)

#计算时指定使用 CachedExecContext
execute_factor(Factor('pe_ratio'), order_book_ids, start_date, end_date, exec_context_class=CachedExecContext)
```