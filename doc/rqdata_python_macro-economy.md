## econ.get_reserve_ratio - 获取存款准备金率 {#rqdata-API-econ-get_reserve_ratio}

```
econ.get_reserve_ratio(reserve_type,start_date,end_date,date_type, market='cn')
```

#### 参数 {#rqdata-API-econ-get_reserve_ratio-param}

| 参数         | 类型                                                           | 说明                                                                                                    |
| ------------ | -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| reserve_type | _str_ or _str list_                                            | 目前有大型金融机构（'major'） 和 其他金融机构（'other'）两种分类。<br/>默认为 all，即所有类别都会返回。 |
| start_date   | _int, str, datetime.date, datetime.datetime, pandas.Timestamp_ | 开始日期，默认为去年的查询当日（基准为信息公布日）。                                                    |
| end_date     | _int, str, datetime.date, datetime.datetime, pandas.Timestamp_ | 结束日期，默认为查询当日。                                                                              |
| market     | _str_                                                          | 默认是中国内地市场('cn')  |

#### 返回 {#rqdata-API-econ-get_reserve_ratio-return}

_pandas dataframe_

| 字段           | 类型                 | 说明                 |
| -------------- | ------------------- | -------------------- |
| reserve_type   | _str_               | 存款准备金类别       |
| info_date      | _pandas.Timestamp_   | 消息公布日期         |
| effective_date | _pandas.Timestamp_   | 存款准备金率生效日期 |
| ratio_floor    | _float_             | 存款准备金下限       |
| ratio_ceiling  | _float_             | 存款准备金上限       |

#### 范例 {#rqdata-API-econ-get_reserve_ratio-example}

```python
[In]
econ.get_reserve_ratio(reserve_type='major',start_date='20170101',end_date='20181017')

[Out]

            reserve_type 	                effective_date 	ratio_ceiling 	ratio_floor
info_date
2018-10-07 	major_financial_institution 	2018-10-15 	 	15.0 	        15.0
2018-04-17 	major_financial_institution 	2018-04-25 	 	16.0 	        16.0

```

## econ.get_money_supply - 获取货币供应量 {#rqdata-API-econ-get_money_supply}

```
econ.get_money_supply(start_date,end_date, market='cn')
```

#### 参数 {#rqdata-API-econ-get_money_supply-param}

| 参数       | 类型                                                           | 说明                                                 |
| ---------- | -------------------------------------------------------------- | ---------------------------------------------------- |
| start_date | _int, str, datetime.date, datetime.datetime, pandas.Timestamp_ | 开始日期，默认为去年的查询当日（基准为信息公布日）。 |
| end_date   | _int, str, datetime.date, datetime.datetime, pandas.Timestamp_ | 结束日期，默认为查询当日。                           |
| market     | _str_                                                          | 默认是中国内地市场('cn')  |

#### 返回 {#rqdata-API-econ-get_money_supply-return}

_pandas dataframe_

| 字段           | 类型                 | 说明                   |
| -------------- | ------------------- | ---------------------- |
| info_date      | _pandas.Timestamp_   | 消息公布日期           |
| effective_date | _pandas.Timestamp_   | 货币供应量生效日期     |
| m0             | _float_             | 市场现金流通量(百万元) |
| m1             | _float_             | 狭义货币(百万元)       |
| m2             | _float_             | 广义货币(百万元)       |
| m0_growth_yoy  | _float_             | 市场现金流通量同比     |
| m1_growth_yoy  | _float_             | 狭义货币同比           |
| m2_growth_yoy  | _float_             | 广义货币同比           |

#### 范例 {#rqdata-API-econ-get_money_supply-example}

```python
[In]
econ.get_money_supply(start_date='20180801',end_date='20181017')

[Out]

 	          effective_date 	m2 	     m1 	    m0    m2_growth_yoy  m1_growth_yoy 	m0_growth_yoy
info_date
2018-09-21 	2018-08-31 	178867043.0 	53832464.0 	6977539.0 	0.082 	  0.039 	    0.033
2018-08-16 	2018-07-31 	177619611.0 	53662429.0 	6953059.0 	0.085 	  0.051 	    0.036

```

## econ.get_factors- 获取宏观因子数据 {#rqdata-API-econ-get_factors}

```
econ.get_factors(factors, start_date, end_date, market='cn')
```

获取宏观因子数据。

#### 参数 {#rqdata-API-econ-get_factors-param}

| 参数       | 类型       | 说明                                                                                                                                 |
| ---------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| factors    | _str_      | **必填参数**，宏观因子名称，<a href="https://assets.ricequant.com/vendor/rqdata/econ_get_factors.xlsx" target="_blank">点击下载</a > |
| start_date | _int, str, datetime.date, datetime.datetime, pandas.Timestamp_ | **必填参数**，起始日期                                                                                                               |
| end_date   | _int, str, datetime.date, datetime.datetime, pandas.Timestamp_ | **必填参数**，截止日期                                                                                                               |
| market     | _str_                                                          | 默认是中国内地市场('cn')  |

#### 返回 {#rqdata-API-econ-get_factors-return}

_pandas dataframe_

| 字段       | 类型               | 说明         |
| ---------- | ----------------- | ------------ |
| info_date  | _str_             | 因子发布日期 |
| start_date | _pandas.Timestamp_ | 起始日期     |
| end_date   | _pandas.Timestamp_ | 截止日期     |
| value      | _float_           | 指标数据     |

#### 范例 {#rqdata-API-econ-get_factors-example}

- 获取工业品出厂价格指数 PPI*当月同比*(上年同月=100)在 2017-08-01 到 2018-08-01 数据。

```python
[In]econ.get_factors( factors='工业品出厂价格指数PPI_当月同比_(上年同月=100)', start_date='20170801', end_date='20180801')
[Out]
                    start_date	end_date	value
factor	info_date
工业品出厂价格指数PPI_当月同比_(上年同月=100)
2017-08-09 09:30:00	2017-06-30	2017-07-31	105.5000
2017-09-09 09:30:00	2017-07-31	2017-08-31	106.3000
2017-10-16 09:30:00	2017-08-31	2017-09-30	106.9000
2017-11-09 09:30:00	2017-09-30	2017-10-31	106.9000
2017-12-09 09:30:00	2017-10-31	2017-11-30	105.8000
 ...
```
