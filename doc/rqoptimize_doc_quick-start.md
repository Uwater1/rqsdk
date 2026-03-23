
## 快速上手

### 安装产品

在[安装 RQSDK](https://www.ricequant.com/doc/rqsdk/#%E5%A6%82%E4%BD%95%E5%AE%89%E8%A3%85-ricequant-sdk)的基础上，用户可通过如下命令实现优化器的一键安装：

```python
rqsdk install rqoptimizer
```

更新 rqoptimizer 版本命令如下：

```python
rqsdk update rqoptimizer
```
### 选股

选股 API 形式如下所示：

```python
stock_select(pool, targets, date, score, benchmark=None)
```
#### 参数

| 参数名         | 类型         | 说明        |
| -------------- | ----------- | ----------- |
| pool           | _pandas.Series_     | 投资组合备选股票池。<br />index 为股票代码，value 为股票优先级系数。优先级系数范围为 0~2 的整数，不同股票取值可相同，取值为 0 表示最高优先级，依次类推。选股时首先选取优先级高的股票。 |
| targets         | _list_      | 选股目标列表        |
| date           | _string_    | 日期 |
| score          |             | 个股得分|
| benchmark      | _string_    | 基准组合， 默认为None。支持股票指数，例如沪深 300（'000300.XSHG'）或中证 500（’000905.XSHG’）。  |

#### 返回

_list_ - 股票代码列表

#### 示例

```python
[In]
from rqoptimizer import *
from rqoptimizer.utils import *
import rqdatac
import pandas as pd
rqdatac.init()

def update_stock_pool(date):
    index_weight = rqdatac.index_weights('000300.XSHG', date)

    # 沪深300中权重大于3%的股票设定为第一优先级股票
    first_priority_stock_pool = index_weight[index_weight >= 0.03].index.tolist()
    first_priority_stock_pool = pd.Series(index=first_priority_stock_pool,data=0)

    # 去除第一优先级股票后，其它股票中选取beta暴露度最高的前50只作为第二优先级股票
    index_component_800 = rqdatac.index_components('000906.XSHG', date)
    beta_exposure = rqdatac.get_factor_exposure(index_component_800,date,date,factors='beta')
    beta_exposure.index = beta_exposure.index.droplevel('date')
    second_priority_stock_pool = beta_exposure['beta'].drop(first_priority_stock_pool.index).sort_values()[-50:]
    second_priority_stock_pool = pd.Series(index=second_priority_stock_pool.index, data=1)

    # 中证800中去除前两个优先级后，剩余股票作为优先级最低的股票
    last_priority_stock_pool = list(set(index_component_800).difference(set(first_priority_stock_pool.index)).difference(set(second_priority_stock_pool.index)))
    last_priority_stock_pool = pd.Series(index=last_priority_stock_pool, data=2)
    stock_pool = pd.concat([first_priority_stock_pool, second_priority_stock_pool, last_priority_stock_pool])

    return stock_pool
date = '2019-02-28'
stock_pool =  update_stock_pool(date)
#目标选取120只股票，包含5只银行股
targets=[TotalStockCountTarget(120),
IndustryStockCountTarget(industry='银行',classification= IndustryClassification.SWS, count=5)]
# 个股风险贡献得分
score = RiskScore()
stock_select(stock_pool, targets, date, score, benchmark=None)

[Out]
['601988.XSHG',
 '601288.XSHG',
 '601328.XSHG',
 '601398.XSHG',
 '601818.XSHG',
 '600519.XSHG',
 ...
 '600606.XSHG',
 '002254.XSHE',
 '601872.XSHG']

```

### 优化器 API

优化器 API 形式如下所示：

```python
portfolio_optimize(order_book_ids, date, objective= MinVariance(), bnds=None, cons=None, benchmark=None, cov_model=CovModel.FACTOR_MODEL_DAILY)
```

#### 参数
| 参数名         | 类型         | 说明        |
| -------------- | ----------- | ----------- |
| order_book_ids | _list_      | 股票代码列表 |
| date           | _string_    | 日期        |
| objective      |    | 优化目标函数，默认MinVariance() |
| bnds           | _Dictionary_| 个股头寸约束 |
| cons           | _list_      | 约束条件     |
| benchmark      | _string_    | 基准组合，默认为 None。支持股票指数，例如沪深 300（'000300.XSHG'）或中证 500（’000905.XSHG’）。     |
| cov_model      |     | 协方差估计模型，默认为CovModel.FACTOR_MODEL_DAILY - 日度预测模型。<br />此外可选用CovModel.FACTOR_MODEL_MONTHLY- 月度预测模型，<br /> CovModel.FACTOR_MODEL_QUARTERLY - 季度预测模型  |



#### 返回

_pandas.Series_ - 优化权重（index 为 order_book_ids，value 为归一化的优化权重）。

#### 示例

```python
[In]
from rqoptimizer import *
import rqdatac
from rqdatac import *
rqdatac.init()

#优化日期
date = '2019-02-28'
#候选合约
pool =  index_components('000906.XSHG',date)

#对组合中所有个股头寸添加相同的约束0~5%
bounds = {'*': (0, 0.05)}
#优化函数，风格偏离最小化，优化组合beta风格因子暴露度相对于基准组合高出1个标准差
objective = MinStyleDeviation({'size': 0, 'beta': 1, 'book_to_price': 0, 'earnings_yield': 0, 'growth': 0, 'leverage': 0, 'liquidity': 0, 'momentum': 0, 'non_linear_size': 0, 'residual_volatility': 0}, relative=True)
#约束条件，对所有风格因子添加基准中性约束，允许偏离±0.3个标准差
cons = [
        WildcardStyleConstraint(lower_limit=-0.3, upper_limit=0.3, relative=True, hard=True)
    ]

portfolio_optimize(pool, date, bnds=bounds, cons=cons, benchmark='000300.XSHG',objective = objective)

[Out]
000001.XSHE    0.018249
000002.XSHE    0.010267
000006.XSHE    0.000141
000008.XSHE    0.000148
000009.XSHE    0.000085
...
603986.XSHG    0.000010
603993.XSHG    0.001689
```


