# 进阶理解

## 数据处理

在因子计算过程中，为确保结果的准确性和合理性，米筐预设了标准化的数据处理细节，覆盖因子计算过程中可能遇到的关键问题。


### 复权处理

以一个简单因子为例，我们定义当日收益率因子：

```python
f2 = Factor('close') / REF(Factor('close'), 1) - 1
```

在这个因子定义中，`REF`算子用来对因子进行时间维度的调整，`REF(Factor('close'), 1)`表示取上一个交易日的收盘价。`f2`代表当日收盘价相对上一交易日收盘价的涨幅，即当日收益率。

不过，若股票在当日存在分红或拆分行为，当日收盘价与上一交易日收盘价无法直接比较，此时需要对价格序列进行复权处理。在本系统中，`Factor('open')`, `Factor('close')` 等价格类因子对应的是后复权价格，另外提供了`Factor('open_unadjusted')`, `Factor('close_unadjusted')` 等带有后缀`_unadjusted`的不复权价格数据，便于特殊场景使用。

我们建议，所有基于价格数据构建的因子，其最终输出应是无量纲的数值，尽量避免直接使用价格的绝对数值，以提升因子的通用性与稳定性。

### 停牌处理

对于均线等技术指标类因子，计算时若包含停牌期间的数据，结果会不符合预期。因此，因子计算引擎在计算因子值时，会自动过滤停牌期间的数据；计算完成后，将停牌日期对应的因子值填充为 NaN，以此保证因子数据能准确反映股票正常交易状态下的特征。

### NaN 及 Inf 处理

在系统提供的横截面算子（如 `RANK`、`CS_ZSCORE` 等）中，Inf 与 NaN 的处理方式一致，参考 pandas 中 [pandas mode.use_inf_as_na=True](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.set_option.html) 时的行为，即把 Inf 当作 NaN 来处理，确保横截面计算过程中数据的一致性

## 自定义算子和因子

借助系统内置的基础因子和算子，能构建诸多经典因子（如著名的 [alpha101](https://arxiv.org/pdf/1601.00991)）。但有时内置算子无法满足特定需求（比如特殊均线计算），此时就需要自定义算子；若内置基础因子也无法覆盖场景，还可进行[自定义基础因子开发](#custom-factor)。

### 自定义非横截面算子

我们以一个对时间序列进行指数加权的算子为例，说明如何定义一个算子。这个算子实现如下功能：

- 半衰期为 22 个交易日；
- 时间窗口长度可设置；
- 输出值为加权平均值；

我们先看一下这个自定义算子的代码：

```python
import numpy as np

from rqfactor.extension import rolling_window
from rqfactor.extension import RollingWindowFactor

def my_ema(series, window):
    # series: np.ndarray, 一维数组
    # window: int, 窗口大小
    q = 0.5 ** (1 / 22)
    weight = np.array(list(reversed([q ** i for i in range(window)])))
    r = rolling_window(series, window)
    return np.dot(r, weight) / window

def MY_EMA(f, window):
    return RollingWindowFactor(my_ema, window, f)

```

我们来逐行看一下这个代码：

```python
import numpy as np
```

这一行引入了`numpy`这个包。

```python
from rqfactor.extension import rolling_window
```

`rolling_window`是定义在`rqfactor.extension`中的一个辅助函数，能对一维数组做滑动窗口处理，具体演示如下（其中第一个参数是一个一维数组，第二个参数代表滑动窗口的大小）：

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

上述代码从一个长度为 100 的数组生成了 81 个长度为 20 的数组，每一个数组的长度都是 20，起止索引都比前一个数组多 1。

```python
from rqfactor.extension import RollingWindowFactor
```

`RollingWindowFactor` 封装了滑动窗口算子的细节，接收 “实际运算函数（如 my_ema）、窗口大小、待处理因子” 三个参数。

```python
def my_ema(series, window):
    # series: np.ndarray, 一维数组
    # window: int, 窗口大小
    q = 0.5 ** (1 / 22)
    weight = np.array(list(reversed([q ** i for i in range(window)])))
    r = rolling_window(series, window)
    return np.dot(r, weight) / window
```

这是实际的运算逻辑，`q`计算指数加权的衰减系数,`weight`是反向权重数组，实现指数加权。

```python
def MY_EMA(f, window):
    return RollingWindowFactor(my_ema, window, f)

```

我们在此定义了算子`MY_EMA`，它包含两个参数

| 参数名         | 说明        |
| --------------|------------|
| f          | 输入因子 |
| window       | 指定计算窗口大小       |


该函数的返回值是一个 `RollingWindowFactor`对象

``` python
RollingWindowFactor(my_ema, window, f)
```

#### 参数

| 参数名         | 说明        |
| --------------|------------|
| my_era         | 实际执行数据变换的函数（本例中为my_ema，负责实现指数加权平均的计算逻辑） |
| window       | 指定计算窗口大小, (与MY_EMA的window参数对应，决定滑动窗口的长度)       |
|f|待变换的因子（即MY_EMA的f参数，为算子提供原始数据输入）|


通过这种封装，MY_EMA算子能够像系统内置算子一样，接收因子作为输入并返回新的复合因子，后续可直接通过`execute_factor`函数计算其值。

我们来试试这个刚定义的算子：

```python
In[]:
f3 = MY_EMA(Factor('close'), 60)
execute_factor(f3, ['000001.XSHE', '600000.XSHG'], '20180101', '20180201')

Out[]:
    000001.XSHE	600000.XSHG
2018-01-02	595.519641	71.160893
2018-01-03	596.415462	71.127573
2018-01-04	597.134786	71.096515
2018-01-05	597.910246	71.072833
2018-01-08	598.141833	71.051230
2018-01-09	598.508616	71.031295
2018-01-10	599.535419	71.078636
2018-01-11	600.368100	71.105770
2018-01-12	601.440555	71.124114
2018-01-15	603.602941	71.167961
2018-01-16	605.771385	71.191253
2018-01-17	607.872235	71.253908
2018-01-18	610.756388	71.341881
2018-01-19	613.707366	71.429583
2018-01-22	615.869869	71.417998
2018-01-23	618.315959	71.437837
2018-01-24	620.674527	71.596174
2018-01-25	622.260534	71.768031
2018-01-26	623.511577	71.886025
2018-01-29	624.244004	72.008997
2018-01-30	624.831171	72.060310
2018-01-31	625.906664	72.120089
2018-02-01	626.862451	72.203242
```

`execute_factor` 会调用因子计算引擎来计算因子值。

### 自定义横截面算子

上面我们定义了一个非横截面类型的算子，下面我们看看如何定义一个横截面算子。系统内置的`INDUSTRY_NEUTRALIZE`算子采用申万一级行业分类，现在希望使用中信行业分类，为此我们可自定义如下算子：

```python
import pandas as pd

import rqdatac
from rqfactor.extension import UnaryCrossSectionalFactor

def zx_industry_neutralize(df):
    # 横截面算子在计算时，输入是一个 pd.DataFrame，其 index 为 trading date，columns 为 order_book_id

    latest_day = df.index[-1]
    # 事实上我们需要每个交易日获取行业分类，这样是最准确的。不过这里我们简化处理，直接用最后一个交易日的行业分类
    # 无需担心 rqdatac 的初始化问题，在因子计算引擎中已经有适当的初始化，因此这里可以直接调用
    industry_tag = rqdatac.zx_instrument_industry(df.columns, date=latest_day)['first_industry_name']

    # 在处理时，对 inf 当做 null 处理，避免一个 inf 的影响扩大
    with pd.option_context('mode.use_inf_as_null', True):
        # 每个股票的因子值减去行业均值
        result = df.T.groupby(industry_tag).apply(lambda g: g - g.mean()).T
        # reindex 确保输出的 DataFrame 含有输入的所有股票
        return result.reindex(columns=df.columns)


def ZX_INDUSTRY_NEUTRAILIZE(f):
    return UnaryCrossSectionalFactor(zx_industry_neutralize, f)

```

返回的`UnaryCrossSectionalFactor` 封装了横截面算子的一些细节，其原型如下：

``` python
UnaryCrossSectionalFactor(func, factor, *args, **kwargs)
```

其中`func` 和 `df` 为必填参数，（本例中为`zx_industry_neutralize` 和 `f`）；`*args`, `**kwargs` 为非必填参数，计算引擎在调用 `func` 时，会一并传入。

我们来试试这个新的算子：

``` python
In[]:
f4 = ZX_INDUSTRY_NEUTRAILIZE(Factor('pb_ratio'))
execute_factor(f4, index_components('000300.XSHG', '20180201'), '20180101', '20180201')

Out[]:
002508.XSHE	601727.XSHG	600362.XSHG
2018-01-02	4.772367	-1.187943	-2.622838
2018-01-02	4.772367	-1.187943	-2.622838
......
```

自定义算子方面我们就介绍到这里。为帮助更高效地定义各类算子，RQFactor 框架内置了一系列工具类，这些类封装了不同类型算子的通用逻辑，可直接复用。以下是框架提供的核心工具类及使用规范：

### 自定义算子参考 

#### 非横截面算子

非横截面算子主要处理单只股票的时间序列数据，按计算逻辑分为两类：

1. 简单算子（基于当期值计算）
适用于 “仅依赖输入因子当期值” 的场景（如`LOG`, `+`等），输出因子长度与输入一致。

    - `CombinedFactor(func, *factors)`: 定义在`rqfactor.extension`中，需传入一个运算函数 `func`，其原型为 `func(*series)`，其中 `series` 为各输入因子的时间序列（一维数组）。

2. 滑动窗口算子（基于时间序列计算）
适用于 “依赖输入因子历史窗口数据” 的场景（如均线、波动率等）。

    框架提供两类工具类：

    - 单因子输入： `RollingWindowFactor(func, window, factor)`, 定义在`rqfactor.extension`中；
    运算函数 `func` 原型为 `def func(series, window)`，其中 `series` 为单因子的时间序列，`window` 为窗口大小。
    
    - 多因子输入：`CombinedRollingWindowFactor(func, window, *factors)`，定义在`rqfactor.extension`中，接受多个因子作为输入，`func`函数原型为`def func(window, *series)`，其中 `series` 为多个因子的时间序列，`window` 为窗口大小。

#### 横截面算子

对于横截面算子，我们提供了以下预定义的类：

- `CombinedCrossSectionalFactor(func, *factors)`: 定义在 `rqfactor.extension` 中，其中 `func` 的原型为 `func(*dfs)`，其中 `dfs` 为各输入因子的横截面数据框（索引为交易日，列为股票代码）。


## 自定义基础因子 {#custom-factor}

自定义算子解决的是自定义转换方法的问题，自定义基础因子用于解决 “内置基础因子无法覆盖数据源或计算逻辑” 的问题。以 “计算股票日内波动率（分钟线收盘价波动率）” 为例，代码如下：

```python
import numpy as np
import pandas as pd
import rqdatac

# 所有自定义基础因子都是 UserDefinedLeafFactor 的实例
from rqfactor.extension import UserDefinedLeafFactor


# 计算因子值
def get_factor_value(order_book_ids, start_date, end_date):
    """
    @param order_book_ids: 股票/指数代码列表，如 000001.XSHE
    @param start_date: 开始日期，pd.Timestamp 类型
    @param end_date: 结束日期，pd.Timestamp 类型

    @return pd.DataFrame, index 为 pd.DatatimeIndex 类型，可通过 pd.to_datetime(rqdatac.get_trading_dates(start_date, end_date)) 生成；column 为 order_book_id；注意，仅包含交易日
    """
    data = rqdatac.get_price(order_book_ids, start_date, end_date, fields='close', frequency='1m', adjust_type='none')
    if data is None or data.empty:
        return pd.DataFrame(
            index=pd.to_datetime(rqdatac.get_trading_dates(start_date, end_date)),
            columns=order_book_ids)
    result = data.groupby(lambda d: d.date()).apply(lambda g: g.pct_change().std())

    # index 转换为 pd.DatetimeIndex
    result.index = pd.to_datetime(result.index)
    return result


f5 = UserDefinedLeafFactor('day_volatility', get_factor_value)

```

`UserDefinedLeafFactor`的原型如下：

```python
UserDefiendLeafFactor(name, func)
```

其中，参数`name`是因子名称，`func`则是因子值的计算方法，返回符合格式的因子值 DataFrame。其原型如上面代码中注释所示。

我们来使用一下这个因子：

```python
In[]:
execute_factor(f5, ['000001.XSHE', '600000.XSHG'], '20180101', '20180201')

Out[]:
    000001.XSHE	600000.XSHG
2018-01-02	0.001672	0.000872
2018-01-03	0.001680	0.000772
2018-01-04	0.001232	0.000767
2018-01-05	0.000830	0.000639
2018-01-08	0.000943	0.000619
2018-01-09	0.000999	0.000585
2018-01-10	0.001251	0.001110
2018-01-11	0.001203	0.000852
2018-01-12	0.001065	0.000694
2018-01-15	0.001562	0.000817
2018-01-16	0.001791	0.000909
2018-01-17	0.002437	0.001630
2018-01-18	0.001841	0.001025
2018-01-19	0.001785	0.001460
2018-01-22	0.001730	0.001036
2018-01-23	0.001777	0.001054
2018-01-24	0.002149	0.002010
2018-01-25	0.001493	0.001465
2018-01-26	0.001483	0.001591
2018-01-29	0.001488	0.001163
2018-01-30	0.001303	0.001158
2018-01-31	0.001268	0.001162
2018-02-01	0.002066	0.001315
```

这时候，`f5`作为一个自定义因子，已经可以如其他基础因子一样使用了，下面展示与其他因子结合使用：

```python
In[]:
execute_factor(f5 * Factor('pb_ratio'), ['000001.XSHE', '600000.XSHG'], '20180101', '20180201')

Out[]:
    000001.XSHE	600000.XSHG
2018-01-02	0.001946	0.000823
2018-01-03	0.001903	0.000725
2018-01-04	0.001387	0.000723
2018-01-05	0.000938	0.000602
2018-01-08	0.001038	0.000583
2018-01-09	0.001110	0.000551
2018-01-10	0.001432	0.001073
2018-01-11	0.001370	0.000818
2018-01-12	0.001227	0.000665
2018-01-15	0.001885	0.000790
2018-01-16	0.002160	0.000870
2018-01-17	0.002947	0.001585
2018-01-18	0.002303	0.001008
2018-01-19	0.002245	0.001434
2018-01-22	0.002123	0.000982
2018-01-23	0.002212	0.001009
2018-01-24	0.002673	0.002024
2018-01-25	0.001801	0.001484
2018-01-26	0.001770	0.001584
2018-01-29	0.001737	0.001161
2018-01-30	0.001511	0.001126
2018-01-31	0.001513	0.001136
2018-02-01	0.002463	0.001298
```
