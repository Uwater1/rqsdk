# 选股

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
| benchmark      | _string_    | 基准组合，默认为None。支持股票指数，例如沪深 300（'000300.XSHG'）或中证 500（’000905.XSHG’）。  |

#### 返回

_list_ - 股票代码列表

## 选股目标列表

### 选股数量目标

```python 
TotalStockCountTarget(count)
```

#### 参数

| 参数  | 数据类型 | 说明                                                             |
| ------|-------  | ----------------------------------------------------------------|
| count | _int_   |总选股数目选择。例如 count 取值为 120，即从备选股票池选取 120 只股票。|

### 行业内选股目标

```python
IndustryStockCountTarget(industry, classification, count)
```

#### 参数

| 参数    | 数据类型 | 说明                                                             |
| --------|-------  | ----------------------------------------------------------------|
| industry | _string_ |行业名称。行业名称需与行业分类参数 classification 匹配。|
| classification |          |行业分类标准。可选择申万一级行业分类（'IndustryClassification.SWS'），中信一级行业分类（'IndustryClassification.ZX'），以及申万一级行业分类金融细分（拆分非银金融）（'IndustryClassification.SWS_1'）|
| count     | _int_    |行业目标选股数目。|


#### 示例

例如计划选取股票总数量为 120 只，并按照中信一级行业分类，选取 5 只银行业股票，则输入形式如下：

```python
targets=[TotalStockCountTarget(120),
IndustryStockCountTarget(industry='银行',classification= IndustryClassification.ZX, count=5)]

```

## 个股得分


### 个股得分序列

```python
score_series
```

类型：_pandas.Series_，index 为备选股票代码，value 为个股得分。股票得分不能相同，得分类型可为整数或浮点数。

#### 示例

```python
data=[1.1,0.5,2,3.1,2.2,3,1.2,0.8,0.2,3.2]
score = pd.Series(data, index=pd.Index(index_components('000300.XSHG')[0:10],name='order_book_id'))
```

若用户不输入个股得分序列，则可根据不同的优化目标选择下述几种输入。

### 个股风格暴露度得分

```python
TargetStyleScore(target_style, relative=False)
```

选择该选股方式时，个股风格暴露度与目标风格暴露度越接近，个股得分越高。当优化目标为风格偏离最小化时，可考虑该选股方式。

#### 参数

| 参数    | 数据类型 | 说明                                                             |
| --------|-------  | ----------------------------------------------------------------|
| target_style | _pandas.Series_ |目标风格暴露度，index 为风格因子名称，value 为目标风格暴露度。|
| relative | _bool_         |是否相对于基准的风格偏离目标。默认为 False。|

#### 示例

```python
target_style = pd.Series({'size': 0, 'beta': 1, 'book_to_price': 0, 'earnings_yield': 0, 'growth': 0, 'leverage': 0,'liquidity': 0, 'momentum': 0, 'non_linear_size': 0, 'residual_volatility': 0})
score = TargetStyleScore(target_style=target_style, relative=True)
```

### 个股风险贡献得分

```python
RiskScore()
```

选择该选股方式时，个股在等权重组合中波动率贡献越低，个股得分越高。当优化目标为波动率最小化或风险平价时，可考虑该选股方式。

### 个股主动风险贡献得分

```python
ActiveRiskScore()
```

个股主动风险贡献得分。选择该选股方式时，个股在等权重组合中追踪误差贡献越低，个股得分越高。当优化目标为追踪误差最小化时，可选择该方法对个股打分。



### 收益风险比得分

```python
RiskReturnScore(expected_returns=None, window=126)
```

选择该选股方式时，个股预期收益率与个股在等权重组合中的波动率贡献的比值越高，个股得分越高。当优化目标为均值方差或夏普率最大化时，可选择该方法对个股打分。

#### 参数

| 参数                      | 数据类型         | 说明                                                                     |
| ------------------------- |-------------    | ------------------------------------------------------------------------------------------- |
| expected_returns          | _pandas.Series_ |个股预期年化收益率，index 是股票 order_book_ids，value 是预期年化收益率（浮点数）。若预期收益率存在缺失值，则将缺失值以 0 填补。若预期收益全部缺失，则优化问题等价于方差最小化问题。若用户不传入该参数，则使用历史收益率估计。|
| window                    | _int_           |预期年化收益率估计所使用的的历史收益率时间长度,仅在没有设置 expected_returns 参数时生效。默认为 252 个交易日，即使用最近 252 个交易日的个股日收益率计算预期年化收益率。|

#### 示例

```python
data = [ 0.02415139,  0.01156958, -0.01172305,  0.00391858, -0.00044541,0.0 ,  0.00153166, -0.00153848,-0.008744,0.004233]
stock_list =['601555.XSHG','300124.XSHE','002415.XSHE','600028.XSHG','002916.XSHE','600655.XSHG','600176.XSHG','601088.XSHG','002456.XSHE','601658.XSHG']
expected_returns  = pd.Series(data, index=pd.Index(stock_list,name='order_book_id'))
score = RiskReturnScore(expected_returns)
```

### 个股主动收益风险比得分

```python
ActiveRiskReturnScore(expected_active_returns=None, window=252)
```

选择该选股方式时，个股预期主动收益率与个股在等权重组合中的追踪误差贡献的比值越高，个股得分越高。当优化目标为信息比率最大化时，可选择该方法。

#### 参数
| 参数                      | 数据类型         | 说明                                                                     |
| ------------------------- |-------------    | ------------------------------------------------------------------------ |
| expected_active_returns    | _pandas.Series_ |个股预期主动收益率（参数解释见上文中信息比率最大化模型），若用户不传入该参数，则使用历史收益率估计。|
| window                    | _int_           |收益率估计所使用的的历史数据的时间长度,仅在没有设置 expected_active_returns  参数时生效。默认为 252 个交易日，即使用最近 252 个交易日的个股日收益率计算预期主动收益率。|
