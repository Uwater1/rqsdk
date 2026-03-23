
## API
```python

performance_attribute( model, daily_weights, daily_return=None, benchmark_info=None)

```

### 参数

| 参数           | 类型                | 说明                                                                                                                                                                                                                                                                                                                                                                                                                                   |
|-----|-----|-----|
| model          | _str_ OR _str list_ | 模型类型，可选以下几种的混合： "equity/brinson"、"equity/factor" 、"equity/factor_v2"                                                                                                                                                                                                                                                                                                                                                  |
| daily_weights  | _pd.Series_         | 每日每个合约的权重, index 为 ['date', 'order_book', 'asset_type'] , 值为 weight, 其中 asset_type 字段支持 'stock' 和 'cash'                                                                                                                                                                                                                                                                                                            |
| daily_return   | _pd.Series_         | 每日的总收益率, 其中 index 为 'date', 值为收益率，收益率的开始时间应是权重的开始时间的下一个交易日, 结束时间应是权重结束时间的下一个交易日                                                                                                                                                                                                                                                                                             |
| benchmark_info | _dict_              | 基准，无基准信息输入则以上证 300 作为基准。基准支持 4 种类型, 如下所示: <br>1. {'type': 'index', 'name': '上证 300', 'detail': '000300.XSHG'} <br>2. {'type': 'mixed_index', 'name': '20% 上证 300 + 80% 上证综指', 'detail': {'000300.XSHG': 0.2, '000008.XSHG': 0.8}} <br>3. {'type': 'yield_rate', 'name': '1 年期国债', 'detail': 'YIELD1Y'} <br>4. {'type': 'cash', 'name': "零收益现金", 'detail': 0.0} <br>其中 name 为可选字段 |

::: tip daily_return日期说明

daily_weights 的 date 每一项都向后取一个交易日即为 daily_return 的日期

:::
### 其他可选参数

| 参数                  | 类型                   | 说明                                                                    |
|-----|-----|-----|
| leverage_ratio        | _pd.Series_ OR _float_ | 杠杆率, 组合收益率当日的杠杆率                                          |
| standard              | _str_                  | brinson 行业归因标准，可选：'sws', 'citics'                             |
| special_assets_return | _pd.Series_            | index 为 date, order_book_id，value return， 其中收益率为真实组合收益率 |

### 返回

_dict_，包含下述内容

| 参数                  | 类型                   | 说明                                                                    |
|-----|-----|-----|
| returns_decomposition       | _list_ | 混合资产 Brinson 归因                                          |
| attribution              | _dict_              | 根据选择的模型，返回以下相应结果<br>`"equity/brinson"`：brinson 归因<br> `"equity/factor"`：<br>factor_attribution：各因子对投资组合与基准组合收益贡献<br>factor_exposure：投资组合与基准组合对因子的风险暴露<br> sensitivity：敏感度分析<br>` "equity/factor_v2"` ：<br> factor_attribution：各因子对投资组合与基准组合收益贡献<br>factor_exposure：投资组合与基准组合对因子的风险暴露<br>sensitivity：敏感度分析                            |
| excel_report | _dict_            | 收益趋势 |
