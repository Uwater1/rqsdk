# 优化器

```python
portfolio_optimize(order_book_ids, date, objective= MinVariance(), bnds=None, cons=None, benchmark=None, cov_model=CovModel.FACTOR_MODEL_DAILY)
```

#### 参数
| 参数名         | 类型         | 说明        |
| -------------- | ----------- | ----------- |
| order_book_ids | _list_      | 股票代码列表 |
| date           | _string_    | 日期        |
| objective      |     | 优化目标函数，默认MinVariance() |
| bnds           | _Dictionary_| 个股头寸约束 |
| cons           | _list_      | 约束条件     |
| benchmark      | _string_ or _OptimizeBenchmark_ | 基准组合，默认为 None。支持股票指数，自定义基准需要继承自 OptimizeBenchmark 的类实例。    |
| cov_model      |     | 协方差估计模型，默认为CovModel.FACTOR_MODEL_DAILY - 日度预测模型。<br />此外可选用CovModel.FACTOR_MODEL_MONTHLY- 月度预测模型，<br /> CovModel.FACTOR_MODEL_QUARTERLY - 季度预测模型  |
| factor_risk_aversion | _float_     | 因子风险厌恶系数，默认为1 |
| specific_risk_aversion| _float_  | 特异风险厌恶系数，默认为1        |
| solver         |     | 使用指定的solver求解，默认为 None，表示使用默认的 solver |
| risk_model     |    | 风险模型版本，支持v1/v2 |
| solver_options |    | solver 参数，如对于 MOSEK，可以传入 mosek_params={...}   |



::: tip OptimizeBenchmark自定义基准

```python
get_weight(date)
```
获取日期的持仓权重。**此函数必需实现。**

**参数**

| 参数     | 数据类型         | 说明                       |
| -------- |-------------    | --------------------------- |
| date     | _datetime.date_ |**必填参数**，日期|

**返回**

_pandas.Series_, index为order_book_id, value 为对应持仓权重


```python
get_expected_returns(date, window=252)
```
获得日期的年化期望收益。 仅当使用 `MaxInformationRatio` / `ActiveMeanVariance` 目标函数， 且不指定 `expected_active_returns` 时需要实现此函数


**参数**

| 参数     | 数据类型         | 说明                       |
| -------- |-------------    | --------------------------- |
| date     | _datetime.date_ |**必填参数**，日期|
| window   | _int_           |回溯窗口大小，默认252|

**返回**

_float_, 年化预期期望收益

**示例**

```python
from rqoptimizer import *

class Benchmark(OptimizeBenchmark):
    def get_weight(self, date):
        return rqdatac.index_weights('000905.XSHG', date)

portfolio_optimize(order_book_ids, date, benchmark=Benchmark(), ...)
```


:::



## 约束条件

优化器的约束条件中包含可选和不可选两类，具体说明如下：

- 不可选条件

  - 不能做空个股，不能加杠杆做多个股。通用公式如下，其中$w_i$为投资组合中个股$i$的权重：

  $$
        0 \lt w_i \lt 1
  $$

  - 投资组合为满仓组合。通用公式如下，若用户希望得到不满仓的优化权重，可对返回的优化结果乘以股票仓位比例。例如，若用户希望的现金和股票占比分别为 20%和 80%，则可对股票优化权重统一乘以 0.8：

  $$
        \Sigma_i w_i =1
  $$

- 可选条件

  - 个股头寸约束。通用公式如下，其中 $a$ 和 $b$ 分别为用户所选择的约束条件上下限：

  $$
        a \lt w_i \lt b
  $$

  - 基准成分股占比约束。通用公式如下：

  $$
        a \leq \Sigma_{i\in 基准成分股} w_i
  $$

  - 风格暴露约束。通用公式如下，其中$x_i$为投资组合中个股 i 的风格暴露度：

  $$
    a \leq \Sigma_{i\in style}w_i x_i \lt b
  $$

  - 行业权重约束。通用公式：

  $$
    a \leq \Sigma_{i\in industry}w_i \lt b
  $$

  - 行业内个股权重约束。通用公式：

  $$
        a\Sigma_{i\in industry}w_i \lt w_i \lt b\Sigma_{i\in industry}w_i
  $$

  - 追踪误差上限约束。通用公式如下，其中$\Sigma$ 为收益协方差矩阵：

  $$
        \sqrt{ (w_p-w_b)^T \Sigma(w_p-w_b)} \lt b
  $$

  - 换手率上限约束。通用公式如下，其中$n$为$t-1$和$t$期曾持仓的股票总数量，$w_i (t-1)$和$w_i (t)$分别为$t-1$和$t$期股票$i$的权重：

  $$
        \Sigma_{i=1}^{n} \lvert\frac{w_i (t)-w_i (t-1)}{2}\rvert
  $$

  - 指数权重约束。通用公式如下，其中 $a$和$b$ 分别为用户所选择的约束条件上下限：

  $$
        a \lt \Sigma_{i\in 指数成分股} w_i \lt b
  $$

  - 自定义组合权重约束。通用公式如下，其中 $a$和$b$ 分别为用户所选择的约束条件上下限：

  $$
        a \lt \Sigma_{i\in 股票池成分股} w_i \lt b
  $$

  - 成交量约束。在进行换手的情况下考虑，对换手的每个股票数量占该股票前 i 个交易日成交量的百分比进行约束

  - 成交量市值约束。在进行换手的情况下考虑，对换手的每个股票市值占该股票前 i 个交易日日总市值的百分比进行约束


### 个股头寸约束

```python
bnds(Dictionary|None)
```

#### 类型
Dictionary 或者 None，默认为 None。输入 Dictionary 时 key 为 order_book_ids，value 为对应股票的上下限组成的 tuple。当 key 为 '\*' 时，表示所有未指定约束的股票均设置相同的权重上下限。

#### 示例

以设置中国平安股票上下限为 5~ 10%，其它个股上下限约束为 0~5%为例，输入示例如下：

```python
bnds={"000001.XSHG":(0.05,0.1),"*":(0,0.05)}
```

### 约束列表

```python
cons(list|None)
```

#### 类型
list 或者 None，默认为 None。若输入list，仅支持下述约束。

#### 年化追踪误差上限约束

```python
TrackingErrorLimit(upper_limit, hard=True)
```

#### 参数

| 参数       | 数据类型   | 说明                                                                     |
| ---------- |-------    | ------------------------------------------------------------------------ |
| upper_limit| _float_   |年化追踪误差上限。例如 upper_limit 设置为 0.15，即表示年化追踪误差上限为 15%。|
| hard       | _bool_    |是否设置为硬约束。默认为 True，即优化结果不满足该约束时报错；若选择 False，即优化结果不满足该约束时，将去掉该约束重新优化。|


#### 示例

以设置年化追踪误差上限为 5%，约束类型为硬约束为例，输入示例如下：

```python
cons = [TrackingErrorLimit(upper_limit=0.05, hard=True)]
```

当追踪误差约束类型为硬约束时，若优化器无法得到可行解时将抛出异常，导致优化器中断策略回测。为避免这种情况出现，优化器支持添加多个追踪误差限制。例如用户希望优化中可以满足追踪误差低于 8%的约束，若该约束无法满足，则允许放松追踪误差约束至 12%。其输入示例如下：

```python
cons = [TrackingErrorLimit(upper_limit=0.08, hard=False),TrackingErrorLimit(upper_limit=0.12, hard=True)]
```

上述软硬约束的设置形式同样适用于换手率约束、风格约束、以及行业约束。

#### 换手率约束

```python
TurnoverLimit(current_holding, upper_limit, hard=True)
```

#### 参数

| 参数            | 数据类型          | 说明                                                                     |
| --------------- |--------------    | ------------------------------------------------------------------------ |
| current_holding | _pandas.Series_ |初始仓位权重，其中 index 是股票合约代码，value 是股票归一化权重。|
| upper_limit     | _float_         |换手率上限，例如 upper_limit 为 0.5 表示换手率上限为 0.5。|
| hard            | _bool_          |是否设置为硬约束。默认为 True，即优化结果不满足该约束时报错；若选择 False，即优化结果不满足该约束时，将去掉该约束重新优化。|



#### 示例

以设置换手率约束上限为 0.3，约束类型为硬约束为例，其输入示例如下：

```python
cons = [TurnoverLimit(current_holding=current_holding, upper_limit=0.3, hard=True)]
```

其中 current_holding 变量类型为 pandas.Series，输入示例如下表所示：

| order_book_id | weight |
| ------------- | ------ |
| 000001.XSHE   | 0.0940 |
| 000002.XSHE   | 0.1683 |
| ...           | ...    |

```python
current_holding=pd.Series(data=[0.0940,0.01683,...], index=pd.Index(['000001.XSHE','000002.XSHE',...],name='order_book_id'),  name='weight')
```

#### 基准成分股权重限制

```python
BenchmarkComponentWeightLimit(lower_limit, hard=True)
```

#### 参数
| 参数        | 数据类型   | 说明                                                                     |
| ----------- |-------    | ------------------------------------------------------------------------ |
| lower_limit | _float_   | 基准成分股占比下限。若输入为 0.8，即优化结果中基准成分股权重之和不低于 80%。|
| hard        | _bool_    | 是否设置为硬约束。默认为 True，即优化结果不满足该约束时报错；若选择 False，即优化结果不满足该约束时，将去掉该约束重新优化。|


#### 示例

```python
cons = [BenchmarkComponentWeightLimit(lower_limit=0.8, hard=True)]
```

#### 行业权重约束

```python
IndustryConstraint(industries, lower_limit=None, upper_limit=None, relative=False, classification=IndustryClassification.SWS, hard=True)
```

#### 参数

| 参数        | 数据类型                   | 说明                                                                     |
| ----------- |-----------------------    | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| industries  | _list_ or _str_ | 行业名称，只对单个行业有限制时，输入单个行业名称，若对多个行业有限制，输入多个行业名称的列表。|
| lower_limit | _float_                   | 行业权重下限。默认为 None。|
| upper_limit | _float_                   | 行业权重上限。默认为 None。|
| relative    | _bool_                    | 是否相对于基准的行业偏离约束。默认为 False。例如银行业的权重上下限分别设置为 0 和 0.02，当 relative 取值为 True 时，表示投资组合相对于基准组合的银行业权重的允许偏离为 0~2% ；若 relative 为 False，即表示投资组合的银行业目标权重约束为 0~2%。|
| classification|                         | 选择行业分类标准，默认'IndustryClassification.SWS' - 申万一级行业分类。可选'IndustryClassification.ZX' - 中信一级行业分类，或'IndustryClassification.SWS_1' - 申万一级行业分类金融细分（非银金融拆分成证券、保险和多元金额）。|
| hard        | _bool_                 | 是否设置为硬约束。默认为 True，即优化结果不满足该约束时报错；若选择 False，即优化结果不满足该约束时，将去掉该约束重新优化。|


#### 扩展

可指定除`exclude`列表外其他行业的权重限制，与`IndustryConstraint` 配合使用，可方便实现对所有行业的权重限制，API 如下：

```python
WildcardIndustryConstraint(exclude=None, lower_limit=None, upper_limit=None, relative=False, classification=IndustryClassification.SWS, hard=True)
```

::: tip 参数说明
参数 `exclude` （类型：list，默认 None）为排除的行业名称列表，其他参数含义与 `IndustryConstraint` 的参数含义一样。
:::


#### 示例

按照中信一级行业分类，以基准行业中性，允许偏离为 ±1%为例，其输入形式如下：

```python
cons = [WildcardIndustryConstraint(lower_limit=-0.01, upper_limit=0.01, relative=True, classification=IndustryClassification.ZX,hard=True)]
```

#### 行业内个股权重约束

```python
IndustryComponentLimit(industry,lower_limit=None,upper_limit=None,classification=IndustryClassification.SWS,hard=True)
```

#### 参数

| 参数        | 数据类型    | 说明                                                                                               |
| ----------- |----------  | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| industry    | _str_                     | 行业名称。                       |
| lower_limit | _float_                   | 个股占行业权重比例下限。默认为 None。|
| upper_limit | _float_                   | 个股占行业权重比例上限。默认为 None。例如当前银行业权重为 20%，银行业内个股占行业权重比例的上下限分别为 10~30%，则银行业内个股在组合内实际权重上下限为 2%-6%。|
| classification|                         | 选择行业分类标准，默认 IndustryClassification.SWS - 申万一级行业分类。可选IndustryClassification.ZX - 中信一级行业分类，或 IndustryClassification.SWS_1 - 申万一级行业分类金融细分（非银金融拆分成证券、保险和多元金额）。|
| hard        | _bool_                 | 是否设置为硬约束。默认为 True，即优化结果不满足该约束时报错；若选择 False，即优化结果不满足该约束时，将去掉该约束重新优化。|


#### 示例

按照申万一级行业分类标准，银行业内个股占银行业总权重 10~30%为例，其输入形式如下：

```python
cons = [IndustryComponentLimit (industry='银行',lower_limit=0.1, upper_limit=0.3, classification=IndustryClassification.SWS, hard=True)]
```

#### 风格暴露度约束

```python
StyleConstraint(styles, lower_limit=None, upper_limit=None, relative=False, hard=True)
```

风格字段及解释如下表：

| 风格因子字段        | 解释                                             |
| ------------------- | ------------------------------------------------ |
| beta                | 个股/投资组合收益对基准组合价格变动的敏感度      |
| momentum            | 股票收益变化的总体趋势特征                       |
| size                | 上市公司的市值规模                               |
| earnings_yield      | 上市公司的营收能力                               |
| residual_volatility | 个股残余收益的波动程度                           |
| growth              | 上市公司的营收增长情况                           |
| book_to_price       | 上市公司的股东权益-市值比，反映其估值水平        |
| leverage            | 上市公司企业负债占资产比例，反映企业的经营杠杆率 |
| liquidity           | 股票换手率，反映个股交易的活跃程度               |
| non_linear_size     | 反映中等市值股票和大/小市值股票的表现差异        |

#### 参数

| 参数        | 数据类型    | 说明                                                                                               |
| ----------- |----------  | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| styles      | _str_ or _list_  | 约束风格因子字段列表，支持风格字段及其解释见上表。|
| lower_limit | _float_                   | 风格暴露度约束下限。默认为 None。|
| upper_limit | _float_                   | 风格暴露度约束上限。默认为 None。|
| relative    | _bool_                    | 是否相对于基准的风格偏离约束。默认为 False。例如 beta 因子的风格暴露度上下限取值为 0.1~0.3 ，若 relative 为 True，即表示投资组合相对于基准组合的 beta 暴露度约束为高 0.1~0.3 个标准差；若 relative 为 False，即表示投资组合的 beta 因子目标暴露度约束为 0.1~0.3 个标准差。|
| hard        | _bool_                 | 是否设置为硬约束。默认为 True，即优化结果不满足该约束时报错；若选择 False，即优化结果不满足该约束时，将去掉该约束重新优化。|

#### 扩展

可指定除`exclude`列表外的其它风格因子暴露度上下限。与`WildcardIndustryConstraint`类似。

```python
WildcardStyleConstraint(exclude, lower_limit=None, upper_limit=None, relative=False, hard=True)
```
::: tip 参数说明

参数exclude（类型：list，默认 None）为排除的风格因子列表，其他参数含义与`StyleConstraint`的参数含义一样。

:::

#### 示例

对特定风格因子添加约束。以设置贝塔因子暴露度正偏离 0.4 ~ 0.7 个标准差，市值因子暴露度在-0.3~0.3 之间，其他因子无约束为例，其输入示例如下：

```python
cons = [StyleConstraint('beta', lower_limit=0.4,upper_limit=0.7, relative=False,hard=True),StyleConstraint('size', lower_limit=-0.3,upper_limit=0.3,relative=False,hard=True)]
```

对所有风格因子添加基准中性约束，其输入形式如下：

```python
cons = [WildcardStyleConstraint(lower_limit=-0.3, upper_limit=0.3, relative=True, hard=True)]
```

对特定风格因子添加正/负偏离约束，对其它风格因子添加基准中性约束。例如用户认为贝塔因子正暴露能增强组合收益，则设置贝塔因子暴露度相对于基准正偏离 0.4~0.7 个标准差，其它因子与基准保持中性，允许偏离 ±0.3 个标准差，则输入示例如下：

```python
cons = [StyleConstraint('beta', lower_limit=0.4,upper_limit=0.7,relative=True,hard=True),WildcardStyleConstraint(exclude=['beta'], lower_limit=-0.3, upper_limit=0.3, relative=True, hard=True)]
```

#### 指数权重约束

```python
IndexComponentLimit(index_code,lower_limit=None,upper_limit=None, hard=True)
```

#### 参数

| 参数        | 数据类型    | 说明                                                                                               |
| ----------- |----------  | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| index_code | _str_   | 指数代码|
| lower_limit | _float_                   | 指数成分总占比下界。默认为 None。|
| upper_limit | _float_                   | 指数成分总占比上界。默认为 None。|
| hard        | _bool_                    | 是否设置为硬约束。默认为 True，即优化结果不满足该约束时报错；若选择 False，即优化结果不满足该约束时，将去掉该约束重新优化。|


#### 示例

以设置沪深 300 权重为 10%-30%，约束类型为硬约束为例，输入示例如下：

```python
cons = [IndexComponentLimit(index_code = '000300.XSHG',upper_limit = 0.3,lower_limit = 0.1, hard=True)]
```

#### 自定义组合权重约束

```python
StockPoolLimit (stock_list, lower_limit=None, upper_limit=None, hard=True)
```

#### 参数

| 参数        | 数据类型    | 说明                                                                                               |
| ----------- |----------  | ----------------------------------------------------------------------------------------------------------------------------------|
| stock_list | _list_      | 自定义股票列表。|
| lower_limit | _float_    | 组合内股票权重占比下界。默认为 None。|
| upper_limit | _float_    | 组合内股票权重占比上界。默认为 None。|
| hard        | _bool_     | 是否设置为硬约束。默认为 True，即优化结果不满足该约束时报错；若选择 False，即优化结果不满足该约束时，将去掉该约束重新优化。|



#### 示例

与指数权重约束类似，用户自定义一个股票池，对其中的成分股占比进行上下限头寸约束为 10%-30%，输入示例如下：

```python
cons = [StockPoolLimit(stock_list=['300357.XSHE', '001914.XSHE', '002901.XSHE', '002552.XSHE', '300482.XSHE'],
upper_limit=0.3, lower_limit=0.1, hard=True)]
```

#### 成交量约束

```python
TransactionVolumeLimit( current_holding=None, cash=None, window=1, stock_list=None, upper_limit=None, hard=True)
```

#### 参数

| 参数            | 数据类型    | 说明                                                                                               |
| -------------   |----------  | ----------------------------------------------------------------------------------------------------------------------------------|
| current_holding | _float_   | 当前持仓股票数量 |
| cash            | _float_   | 可用资金数量。默认为1 |
| window          | _float_   | 前几个交易日的平均交易量。默认为1|
| stock_list      | _list_    | 需要约束的股票列表。 |
| upper_limit     | _float_   | 成交量占比上界。默认为 None。|
| hard            | _bool_    | 是否设置为硬约束。默认为 True，即优化结果不满足该约束时报错；若选择 False，即优化结果不满足该约束时，将去掉该约束重新优化。|



#### 示例

以设置交易量占比上界约束为 0.01，约束类型为硬约束为例，输入示例如下：

```python
cons = [TransactionVolumeLimit(current_holding=current_holding_num, upper_limit=0.01, cash=1000000, window=1,
stock_list=['300482.XSHE', '300659.XSHE', '000001.XSHE', '600004.XSHG', '603369.XSHG', '600529.XSHG'])]
```

#### 成交量市值约束

```python
TransactionMarketValueLimit (current_holding=None, upper_limit=None, cash=None, window=1, stock_list=None, hard=True)
```

#### 参数

| 参数            | 数据类型    | 说明                                                                                               |
| -------------   |----------  | ----------------------------------------------------------------------------------------------------------------------------------|
| current_holding | _float_   | 当前持仓股票数量 |
| cash            | _float_   | 可用资金数量。默认为1 |
| window          | _float_   | 前几个交易日的平均交易量。默认为1|
| stock_list      | _list_    | 需要约束的股票列表。 |
| upper_limit     | _float_   | 交易市值占该股票总市值百分比上界。默认为 None。|
| hard            | _bool_    | 是否设置为硬约束。默认为 True，即优化结果不满足该约束时报错；若选择 False，即优化结果不满足该约束时，将去掉该约束重新优化。|


#### 示例

以设置交易量市值约束为 0.05，约束类型为硬约束为例，输入示例如下：

```python
cons = [TransactionMarketValueLimit (current_holding=current_holding_num, upper_limit=0.05, cash=1000000, window=1,
stock_list=['300482.XSHE', '300659.XSHE', '000001.XSHE', '600004.XSHG', '603369.XSHG', '600529.XSHG'])]
```

## 优化目标函数

```python
objective()
```

优化器目标函数，支持的优化函数在下面详细介绍。

### 风险最小化

```python
MinVariance()
```

当用户不指定`objective`时,默认使用`MinVariance()`作为优化函数。

### 主动风险最小化

```python
MinActiveVariance()
```

### 均值方差

```pyhthon
MeanVariance(expected_returns, window=126, risk_aversion_coefficient=1，transaction_cost_model=None)
```

#### 参数
| 参数                      | 数据类型         | 说明                                                                     |
| ------------------------- |-------------    | ------------------------------------------------------------------------ |
| expected_returns          | _pandas.Series_ |个股预期年化收益率，index 是股票 order_book_ids，value 是预期年化收益率（浮点数）。若预期收益率存在缺失值，则将缺失值以 0 填补。若预期收益全部缺失，则优化问题等价于方差最小化问题。若用户不传入该参数，则使用历史收益率估计。|
| window                    | _int_           |预期年化收益率估计所使用的的历史收益率时间长度,仅在没有设置 expected_returns 参数时生效。默认为 252 个交易日，即使用最近 252 个交易日的个股日收益率计算预期年化收益率。|
| risk_aversion_coefficient | _float_         |风险厌恶系数,默认为1。|
| transaction_cost_model    |                 |交易成本模型（惩罚项），默认None。详细解释见[交易成本模型](./optimizer.md#交易成本模型)|


#### 示例

```python
data = [ 0.02415139,  0.01156958, -0.01172305,  0.00391858, -0.00044541,0.0 ,  0.00153166, -0.00153848,-0.008744,0.004233]
stock_list =['601555.XSHG','300124.XSHE','002415.XSHE','600028.XSHG','002916.XSHE','600655.XSHG','600176.XSHG','601088.XSHG','002456.XSHE','601658.XSHG']
expected_returns = pd.Series(data, index=pd.Index(stock_list,name='order_book_id'))
objective =  MeanVariance(expected_returns=expected_returns)
```
### 主动均值方差

```python
ActiveMeanVariance( expected_active_returns=None, window=252, risk_aversion_coefficient=1, transaction_cost_model=None)
```

####  参数

| 参数                      | 数据类型         | 说明                                                                     |
| ------------------------- |-------------    | ------------------------------------------------------------------------ |
| expected_active_returns          | _pandas.Series_ |个股预期年化主动收益率，index 是股票 order_book_ids，value 是预期年化主动收益率（浮点数）。若预期主动收益率存在缺失值，则将缺失值以 0 填补。若预期主动收益全部缺失，则优化问题等价于方差最小化问题。若用户不传入该参数，则使用历史收益率估计。|
| window                    | _int_           |预期年化主动收益率估计所使用的的历史收益率时间长度,仅在没有设置 expected_active_returns 参数时生效。默认为 252 个交易日，即使用最近 252 个交易日的个股日收益率计算预期年化主动收益率。|
| risk_aversion_coefficient | _float_         |风险厌恶系数,默认为1。|
| transaction_cost_model    |                 |交易成本模型（惩罚项），默认None。详细解释见[交易成本模型](./optimizer.md#交易成本模型)|


####  示例

```python
data = [ 0.02415139,  0.01156958, -0.01172305,  0.00391858, -0.00044541,0.0 ,  0.00153166, -0.00153848,-0.008744,0.004233]
stock_list =['601555.XSHG','300124.XSHE','002415.XSHE','600028.XSHG','002916.XSHE','600655.XSHG','600176.XSHG','601088.XSHG','002456.XSHE','601658.XSHG']
expected_returns = pd.Series(data, index=pd.Index(stock_list,name='order_book_id'))
objective =  ActiveMeanVariance(expected_returns=expected_returns)
```


### 风险平价

```python
RiskParity()
```


### 追踪误差最小化

```python
MinTrackingError()
```



### 最大化信息比率

```python
MaxInformationRatio(expected_active_returns, window=252)
```

#### 参数

| 参数                      | 数据类型         | 说明                                                                     |
| ------------------------- |-------------    | ------------------------------------------------------------------------ |
| expected_active_returns          | _pandas.Series_ |个股预期年化主动收益率，index 是股票 order_book_ids，value 是个股预期年化主动收益率（浮点数）。若预期主动收益率存在缺失值，则将缺失值以 0 填补。若用户不传入该参数，则使用历史收益率估计。|
| window                    | _int_           |预期年化收益率估计所使用的的历史收益率时间长度,仅在没有设置 expected_active_returns 参数时生效。默认为 252 个交易日，即使用最近 252 个交易日的个股日收益率计算预期年化收益率。|


#### 示例

```python
data = [ 0.02415139,  0.01156958, -0.01172305,  0.00391858, -0.00044541,0.0 ,  0.00153166, -0.00153848,-0.008744,0.004233]
stock_list =['601555.XSHG','300124.XSHE','002415.XSHE','600028.XSHG','002916.XSHE','600655.XSHG','600176.XSHG','601088.XSHG','002456.XSHE','601658.XSHG']
expected_active_return  = pd.Series(data, index=pd.Index(stock_list,name='order_book_id'))
objective =  MaxInformationRatio(expected_active_returns = expected_active_return)
```

### 最大化夏普率

```python
MaxSharpeRatio(expected_returns, window=252)
```
#### 参数

| 参数                      | 数据类型         | 说明                                                                     |
| ------------------------- |-------------    | ------------------------------------------------------------------------ |
| expected_returns          | _pandas.Series_ |个股预期年化收益率，index 是股票 order_book_ids，value 是预期年化收益率（浮点数）。若预期收益率存在缺失值，则将缺失值以 0 填补。若预期收益全部缺失，则优化问题等价于方差最小化问题。若用户不传入该参数，则使用历史收益率估计。|
| window                    | _int_           |预期年化收益率估计所使用的的历史收益率时间长度,仅在没有设置 expected_returns 参数时生效。默认为 252 个交易日，即使用最近 252 个交易日的个股日收益率计算预期年化收益率。|

#### 示例

```python
objective = MaxSharpeRatio(window=200)

```

### 指标最大化

```python
MaxIndicator(indicator_series)
```

#### 参数

| 参数             | 数据类型         | 说明                                                                     |
| ---------------- |-------------    | ------------------------------------------------------------------------ |
| indicator_series | _pandas.Series_ |股票指标得分序列。指标序列 index 为股票 order_book_ids，value 为指标得分，不同股票指标得分可相同，指标得分的变量类型可为浮点数或整数。需要注意的是，若用户传入的个股指标得分存在数量级的差异，可能会导致优化权重过分集中于部分得分较高的个股。因此建议用户在输入前先对指标中的离群值进行处理。此外，若指标中存在缺失值，则剔除出现缺失的股票后再进行优化。|

#### 示例

```python

date = '2014-07-16' # 优化日期
# 获取前一交易日中证800成分股的净利润增长率（TTM）
previous_date = rqdatac.get_previous_trading_date(date)
index_component = rqdatac.index_components('000906.XSHG', previous_date)
indicator_series = rqdatac.get_factor(index_component, 'net_profit_growth_ratio_ttm', previous_date,previous_date,expect_df=False).dropna()
pool = sorted(indicator_series.index)
# 个股指标得分范围调整至0.1-1.1，避免权重过分集中于部分指标得分较大的个股
adjusted_series = ((indicator_series.loc[pool] - indicator_series.loc[pool].min()) / (indicator_series.loc[pool].max() - indicator_series.loc[pool].min())) + 0.1
objective=MaxIndicator(indicator_series=adjusted_series)

```

### 风格偏离最小化

```python
MinStyleDeviation(target_style, relative=False,priority=None)
```

#### 参数
| 参数          | 数据类型         | 说明                                                                     |
| ------------- |-------------    | ------------------------------------------------------------------------ |
| target_style  | _pandas.Series_ |目标风格暴露度，index 为风格因子字段名称，value 为目标风格暴露度，以标准差为单位。|
| relative      | _bool_          |是否以相对基准的风格暴露偏离度为优化目标。默认为 False。例如 beta 因子的 target_style 取值为 0.3，若 relative 为 True，即表示优化组合 beta 风格因子暴露度相对于基准组合高出 0.3 个标准差 ；若 relative 为 False，即表示优化组合的 beta 因子目标暴露度为 0.3 个标准差。|
|priority       | _pandas.Series_ |风格因子优先级设置，默认为None。取值范围为 0~9 之间的整数，9 为最高优先级，0 为最低优先级，未指定的因子优先级默认为 5。风格因子的优先级越高，则在优化中满足其暴露度目标的重要性越高。|


::: tip 可选风格因子字段

| 风格因子字段        | 解释                                             |
| ------------------- | ------------------------------------------------ |
| beta                | 个股/投资组合收益对基准组合价格变动的敏感度      |
| momentum            | 股票收益变化的总体趋势特征                       |
| size                | 上市公司的市值规模                               |
| earnings_yield      | 上市公司的营收能力                               |
| residual_volatility | 个股残余收益的波动程度                           |
| growth              | 上市公司的营收增长情况                           |
| book_to_price       | 上市公司的股东权益-市值比，反映其估值水平        |
| leverage            | 上市公司企业负债占资产比例，反映企业的经营杠杆率 |
| liquidity           | 股票换手率，反映个股交易的活跃程度               |
| non_linear_size     | 反映中等市值股票和大/小市值股票的表现差异        |


:::

#### 示例

```python
target_style = pd.Series({'size': 0, 'beta': 1, 'book_to_price': 0, 'earnings_yield': 0, 'growth': 0, 'leverage': 0,'liquidity': 0, 'momentum': 0, 'non_linear_size': 0, 'residual_volatility': 0})
objective = MinStyleDeviation({'size': 0, 'beta': 1, 'book_to_price': 0, 'earnings_yield': 0, 'growth': 0, 'leverage': 0, 'liquidity':0,'momentum': 0, 'non_linear_size': 0, 'residual_volatility': 0}, relative=True, priority=target_style)

```

## 交易成本模型

说明：目前只支持在`Meanvariance`和`ActiveMeanVariance`目标函数内使用。

### 线性交易成本模型

```python
FixTransactionCostModel(current_holding,single_transaction_cost=0.0005,turnover_per_year=12,coefficient=1.0)
```

#### 参数 
| 参数                          | 数据类型          | 说明                                                                     |
| ----------------------------- |----------------  | ------------------------------------------------------------------------ |
| current_holding               | _pandas.Series_  |当前持仓权重|
| single_transaction_cost | _float_          |单次换手成本，默认为万分之五（单边）|
| turnover_per_year             | _int_            |年调仓次数，默认为 12，即每月调仓一次|
| coefficient                   | _float_          |交易成本系数（0-1.0，默认为 1.0），可以用于调节对交易成本的惩罚力度，1.0 表示在收益率上直接对年化交易成本进行惩罚|


#### 示例

```python
pre_weights = pd.Series(
    {
        "002444.XSHE": 0.05,
        "603019.XSHG": 0.05,
        "603766.XSHG": 0.05,
        "002491.XSHE": 0.05,
        "002545.XSHE": 0.05,
        "600751.XSHG": 0.05,
        "300058.XSHE": 0.05,
        "000800.XSHE": 0.05,
        "000758.XSHE": 0.05,
        "002176.XSHE": 0.05,
        "600981.XSHG": 0.05,
        "000761.XSHE": 0.05,
        "600143.XSHG": 0.05,
        "002249.XSHE": 0.05,
        "600869.XSHG": 0.05,
        "603899.XSHG": 0.05,
        "002437.XSHE": 0.05,
        "000869.XSHE": 0.05,
        "600226.XSHG": 0.05,
        "300180.XSHE": 0.05,
    }
)

transaction_cost = FixTransactionCostModel(
    current_holding=pre_weights, single_transaction_cost=0.0002, turnover_per_year=252
)
portfolio_optimize(order_book_ids,date,
objective=ActiveMeanVariance(transaction_cost_model=transaction_cost),
benchmark='000300.XSHG')
```