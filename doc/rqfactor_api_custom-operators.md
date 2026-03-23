# 自定义算子

以下是 `rqfactor.extension` 包中用于开发自定义算子的**抽象类**与**辅助函数**说明，涵盖类的功能定位、参数要求、函数原型及使用场景，为个性化算子开发提供标准化工具支持：

## 抽象类定义

抽象类用于封装不同类型算子的通用逻辑，只需实现核心运算函数，无需关注数据格式对齐、滑动窗口迭代等底层细节。

#### CombinedFactor
简单复合算子，接受一个函数及单因子或多因子的当期数据运算。

```python
CombinedFactor(func, *factors)
```

#### 参数

| 参数名         | 说明        |
| --------------|------------|
| func          | 原型为 `def func(*series)`，`series` 对应输入的`*factors`，每个`series` 是单因子的时间序列，一维 `np.ndarray`），返回值为计算后的时间序列 |
| *factors        | 1 个或多个输入因子        |


#### RollingWindowFactor

滑动窗口算子

``` python
RollingWindowFactor(func, window, factor)
```

#### 参数

| 参数名         | 说明        |
| --------------|------------|
| func          | 其原型为 `def func(series, window)`，其中 `series` 为 `factor` 的因子值，一维 `np.ndarray`；`window` 为滑动窗口大小（与类参数 `window `一致），返回值为滑动计算后的时间序列    |
|window|滑动窗口大小|
| factor        | 单个输入因子        |



#### CombinedRollingWindowFactor

复合滑动窗口算子
``` python
CombinedRollingWindowFactor(func, window, *factors)
```

#### 参数

| 参数名         | 说明        |
| --------------|------------|
| func          | 其原型为 `def func(window, *series)`, 注意，`window` 参数在前|
|window|滑动窗口大小|
| *factors       | 输入因子        |


#### CombinedCrossSectionalFactor

复合横截面算子，接受一个函数及一个或多个因子

``` python
CombinedCrossSectionalFactor(func, *factors)
```

#### 参数

| 参数名         | 说明        |
| --------------|------------|
| func          | 原型为 `def func(df1, df2, ...)`, 其中 df1/df2/... 对应输入的 `*factors`（每个 df 是横截面数据框，索引为交易日 `pd.DatetimeIndex`，列为股票代码 `order_book_id`，值为因子值），返回值为横截面计算后的 `DataFrame` |
| *factors        | 1 个或多个输入因子        |


#### UserDefinedLeafFactor

用于创建自定义基础因子

``` python 
UserDefinedLeafFactor(name, func)
```

- `name`: 自定义因子的名字；
- `func`: 其原型如下：

```python
    def func(order_book_ids, start_date, end_date):
        """
        @param order_book_ids: 股票/指数代码列表，如 ['000001.XSHE', '600000.XSHG']
        @param start_date: 开始日期，pd.Timestamp 类型
        @param end_date: 结束日期，pd.Timestamp 类型

        @return pd.DataFrame, index 为 pd.DatatimeIndex 类型，可通过 pd.to_datetime(rqdatac.get_trading_dates(start_date, end_date)) 生成；column 为 order_book_id；注意，仅包含交易日
        """
```

## 辅助函数

#### rolling_window

```python
rolling_window(series, window)
```

#### 参数

| 参数名         | 说明        |
| --------------|------------|
| series          | 输入的一维时间序列（`np.ndarray` 或可转换为数组的序列，如 `pd.Series`） |
| window        | 滑动窗口大小（正整数）       |


可参考 [这里](http://stackoverflow.com/questions/6811183/rolling-window-for-1d-arrays-in-numpy)。
其功能如下：

```python
In[]:
a = np.arange(100)
rolling_window(a, 20)

Out[]:
array([[ 0,  1,  2, ..., 17, 18, 19],
    [ 1,  2,  3, ..., 18, 19, 20],
    [ 2,  3,  4, ..., 19, 20, 21],
    ...,
    [78, 79, 80, ..., 95, 96, 97],
    [79, 80, 81, ..., 96, 97, 98],
    [80, 81, 82, ..., 97, 98, 99]])
```
