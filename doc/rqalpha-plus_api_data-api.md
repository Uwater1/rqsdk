# 数据查询接口 {#rqalpha-plus-api-data}

### 市场基础数据 {#rqalpha-plus-api-data-market-basic}

#### all_instruments - 所有合约基础信息

```python
rqalpha.api.all_instruments(type=None)
```

获取某个国家市场的所有合约信息。使用者可以通过这一方法很快地对合约信息有一个快速了解，目前仅支持中国市场。

#### 参数

| 参数名 | 类型                               | 说明                                                      |
|-----|-----|-----|
| type   | _Optional[str]_                    | 需要查询合约类型，例如：type='CS'代表股票。默认是所有类型 |

##### 其中 type 参数传入的合约类型和对应的解释如下：

| 合约类型    | 说明                                                              |
|-----|-----|
| CS          | Common Stock, 即股票                                              |
| ETF         | Exchange Traded Fund, 即交易所交易基金                            |
| LOF         | Listed Open-Ended Fund，即上市型开放式基金 （以下分级基金已并入） |
| INDX        | Index, 即指数                                                     |
| Future      | Futures，即期货，包含股指、国债和商品期货                         |
| Spot        | Spot，即现货，目前包括上海黄金交易所现货合约                      |
| Option      | 期权，包括目前国内已上市的全部期权合约                            |
| Convertible | 沪深两市场内有交易的可转债合约                                    |

#### 返回

_pandas DataFrame_ - 所有合约的基本信息。

#### 范例

- 获取中国内地市场所有 LOF 基金的基础信息：

```python
[In]all_instruments(type='LOF')
[Out]
    abbrev_symbol order_book_id product sector_code  symbol
0 CYGA 150303.XSHE null null 华安创业板50A
1 JY500A 150088.XSHE null null 金鹰500A
2 TD500A 150053.XSHE null null 泰达稳健
3 HS500A 150110.XSHE null null 华商500A
4 QSAJ 150235.XSHE null null 鹏华证券A
```

#### instruments - 合约详细信息

```python
rqalpha.api.instruments(id_or_symbols)
```

获取某个国家市场内一个或多个合约的详细信息。目前仅支持中国市场。

#### 参数

| 参数名        | 类型                    | 说明                     |
|-----|-----|-----|
| id_or_symbols | _Union[str, List[str]]_ | 合约代码或者合约代码列表 |

#### 返回

_Union[ [Instrument](./types#rqalpha-plus-api-types-instrument), List [[Instrument](./types#rqalpha-plus-api-types-instrument)]]_

#### 范例

- 获取单一股票合约的详细信息:

```python
[In]instruments('000001.XSHE')
[Out]
Instrument(order_book_id=000001.XSHE, symbol=平安银行, abbrev_symbol=PAYH, listed_date=19910403, de_listed_date=null, board_type=MainBoard, sector_code_name=金融, sector_code=Financials, round_lot=100, exchange=XSHE, special_type=Normal, status=Active)
```

- 获取多个股票合约的详细信息:

```python
[In]instruments(['000001.XSHE', '000024.XSHE'])
[Out]
[Instrument(order_book_id=000001.XSHE, symbol=平安银行, abbrev_symbol=PAYH, listed_date=19910403, de_listed_date=null, board_type=MainBoard, sector_code_name=金融, sector_code=Financials, round_lot=100, exchange=XSHE, special_type=Normal, status=Active), Instrument(order_book_id=000024.XSHE, symbol=招商地产, abbrev_symbol=ZSDC, listed_date=19930607, de_listed_date=null, board_type=MainBoard, sector_code_name=金融, sector_code=Financials, round_lot=100, exchange=XSHE, special_type=Normal, status=Active)]
```

- 获取合约已上市天数:

```python
instruments('000001.XSHE').days_from_listed()
```

- 获取合约距离到期天数:

```python
instruments('IF1701').days_to_expire()
```

#### get_trading_dates - 交易日列表

```python
rqalpha.api.get_trading_dates(start_date, end_date)
```

获取某个国家市场的交易日列表（起止日期加入判断）。目前仅支持中国市场。

#### 参数

| 参数名     | 类型                                    | 说明     |
|-----|-----|-----|
| start_date | _Union[str, date, datetime, Timestamp]_ | 开始日期 |
| end_date   | _Union[str, date, datetime, Timestamp]_ | 结束日期 |

#### 返回

_DatetimeIndex_

#### 范例

```python
[In]get_trading_dates(start_date='2016-05-05', end_date='20160505')
[Out]
[datetime.date(2016, 5, 5)]
```

#### get_previous_trading_date - 上一交易日

```python
get_previous_trading_date(date)
```

获取指定日期的之前的第 n 个交易日。

#### 参数

| 参数名 | 类型                                    | 说明                    |
|-----|-----|-----|
| date   | _Union[str, date, datetime, Timestamp]_ | 指定日期                |
| n      | _Optional[int]_                         | 第 n 个交易日，默认为 1 |

#### 返回

_date_

#### 范例

```python
[In]get_previous_trading_date(date='2016-05-02')
[Out]
[datetime.date(2016, 4, 29)]
```

#### get_next_trading_date - 下一交易日

```python
rqalpha.api.get_next_trading_date(date)
```

获取指定日期之后的第 n 个交易日

#### 参数

| 参数名 | 类型                                    | 说明                    |
|-----|-----|-----|
| date   | _Union[str, date, datetime, Timestamp]_ | 指定日期                |
| n      | _Optional[int]_                         | 第 n 个交易日，默认为 1 |

#### 返回

_date_

#### 范例

```python
[In]get_next_trading_date(date='2016-05-01')
[Out]
[datetime.date(2016, 5, 3)]
```

#### get_yield_curve - 收益率曲线

```python
rqalpha.api.get_yield_curve(date=None, tenor=None)
```

获取某个国家市场指定日期的收益率曲线水平。

数据为 2002 年至今的中债国债收益率曲线，来源于中央国债登记结算有限责任公司。

#### 参数

| 参数名 | 类型                                          | 说明                                                              |
|-----|-----|-----|
| date   | _Union[str, date, datetime, Timestamp, None]_ | 查询日期，默认为策略当前日期前一天                                |
| tenor  | _Optional[str]_                               | 标准期限，'0S' - 隔夜，'1M' - 1 个月，'1Y' - 1 年，默认为全部期限 |

#### 返回

_DataFrame_

#### 范例

```python
[In]
get_yield_curve('20130104')

[Out]
                0S      1M      2M      3M      6M      9M      1Y      2Y          2013-01-04  0.0196  0.0253  0.0288  0.0279  0.0280  0.0283  0.0292  0.0310

                3Y      4Y   ...        6Y      7Y      8Y      9Y     10Y          2013-01-04  0.0314  0.0318   ...    0.0342  0.0350  0.0353  0.0357  0.0361
...
```

### 行情 {#rqalpha-plus-api-data-quotes}

#### history_bars - 某一合约历史 bar 数据

```python
rqalpha.api.history_bars(order_book_id, bar_count, frequency, fields=None, skip_suspended=True, include_now=False, adjust_type='pre')
```

获取指定合约的历史 k 线行情，同时支持日以及分钟历史数据。不能在 init 中调用。

日回测获取分钟历史数据：不支持

日回测获取日历史数据
| 调用时间 | 返回数据 |
|-----|-----|
| T 日 before_trading| T-1 日 day bar |
| T 日 handle_bar | T 日 day bar |

分钟回测获取日历史数据
| 调用时间 | 返回数据 |
|-----|-----|
| T 日 before_trading| T-1 日 day bar |
| T 日 handle_bar |T-1 日 day bar |

分钟回测获取分钟历史数据
| 调用时间 | 返回数据 |
|-----|-----|
| T 日 before_trading| T-1 日最后一个 minute bar |
| T 日 handle_bar |T 日当前 minute bar |

#### 参数

| 参数名         | 类型                          | 说明                                                                                                                                                                                                        |
|-----|-----|-----|
| order_book_id  | _str_                         | 合约代码，必填项                                                                                                                                                                                            |
| bar_count      | _int_                         | 获取的历史数据数量，必填项                                                                                                                                                                                  |
| frequency      | _str_                         | 获取数据什么样的频率进行。'1d'、'1m' 和 '1w' 分别表示每日、每分钟和每周，必填项                                                                                                                             |
| fields         | _Union[str, List[str], None]_ | 返回数据字段。必填项。见下方列表                                                                                                                                                                            |
| skip_suspended | _Optional[bool]_              | 是否跳过停牌，默认 True，跳过停牌                                                                                                                                                                           |
| include_now    | _Optional[bool]_              | 是否包括不完整的 bar 数据。默认为 False，不包括。举例来说，在 09:39 的时候获取上一个 5 分钟线，默认将获取到 09:31~09:35 合成的 5 分钟线。如果设置为 True，则将获取到 09:36~09:39 之间合成的"不完整"5 分钟线 |
| adjust_type    | _Optional[str]_               | 复权方式，默认为`pre`。<br />不复权 - `none`，<br />动态前复权 - `pre`，后复权 - `post`                                                                                                                     |

##### fields 可选字段：

| fields          | 字段名                 |
|-----|-----|
| datetime        | 时间戳                 |
| open            | 开盘价                 |
| high            | 最高价                 |
| low             | 最低价                 |
| close           | 收盘价                 |
| volume          | 成交量                 |
| total_turnover  | 成交额                 |
| open_interest   | 持仓量（期货专用）     |
| basis_spread    | 期现差（股指期货专用） |
| settlement      | 结算价（期货日线专用） |
| prev_settlement | 结算价（期货日线专用） |

#### 返回

_ndarray_

#### 范例

- 获取最近 5 天的日线收盘价序列（策略当前日期为 20160706）:

```python
[In]
logger.info(history_bars('000002.XSHE', 5, '1d', 'close'))
[Out]
[ 8.69  8.7   8.71  8.81  8.81]
```

#### current_snapshot - 当前快照数据

```python
rqalpha.api.current_snapshot(order_book_id)
```

获得当前市场快照数据。只能在日内交易阶段调用，获取当日调用时点的市场快照数据。 市场快照数据记录了每日从开盘到当前的数据信息，可以理解为一个动态的 day bar 数据。 在目前分钟回测中，快照数据为当日所有分钟线累积而成，一般情况下，最后一个分钟线获取到的快照数据应当与当日的日线行情保持一致。
::: tip 需要注意，在实盘模拟中，该函数返回的是调用当时的市场快照情况，所以在同一个 handle_bar 中不同时点调用可能返回的数据不同。 如果当日截止到调用时候对应股票没有任何成交，那么 snapshot 中的 close, high, low, last 几个价格水平都将以 0 表示。
:::

#### 参数

| 参数名       | 类型         | 说明           |
|-----|-----|-----|
| id_or_symbol | _Union[str]_ | 合约代码或简称 |

#### 返回

_Optional [ [TickObject](./types#rqalpha-plus-api-types-tick) ]_

#### 范例

- 在 handle_bar 中调用该函数，假设策略当前时间是 20160104 09:33:

```python
[In]
logger.info(current_snapshot('000001.XSHE'))
[Out]
2016-01-04 09:33:00.00  INFO
Snapshot(order_book_id: '000001.XSHE', datetime: datetime.datetime(2016, 1, 4, 9, 33), open: 10.0, high: 10.025, low: 9.9667, last: 9.9917, volume: 2050320, total_turnover: 20485195, prev_close: 9.99)
```

#### history_ticks - 指定合约的历史 tick 数据

```python
rqalpha.api.history_ticks(order_book_id, count)
```

获取指定合约历史（不晚于当前时间的）tick 对象，仅支持在 tick 级别的策略（回测、模拟交易、实盘）中调用。

#### 参数

| 参数名        | 类型  | 说明                     |
|-----|-----|-----|
| order_book_id | _str_ | 合约代码                 |
| count         | _int_ | 获取的历史 tick 数据数量 |

#### 返回

_List [ [TickObject](./types#rqalpha-plus-api-types-tick) ]_

#### 范例

```python
[In]
logger.info(history_ticks('TF1803', 2))
[Out]
2017-12-25  09:14:00.300000 INFO [Tick(ask_vols: [1.0], asks: [96.640000000000001], bid_vols: [1.0], bids: [96.635000000000005], datetime: 2017-12-22 15:34:34.700000, high: 96.64, last: 96.64, limit_down: 95.27, limit_up: 97.58, low: 96.425, open: 96.47, open_interest: 46121.0, order_book_id: TF1803, prev_close: 96.64, prev_settlement: 96.425, total_turnover: 7463149750.0, volume: 7729.0), Tick(ask_vols: [1.0], asks: [96.599999999999994], bid_vols: [1.0], bids: [96.579999999999998], datetime: 2017-12-25 09:14:00.300000, high: 96.6, last: 96.6, limit_down: 95.445, limit_up: 97.755, low: 96.6, open: 96.6, open_interest: 46115.0, order_book_id: TF1803, prev_close: 96.64, prev_settlement: 96.6, total_turnover: 8694000.0, volume: 9.0)]
```

#### get_price - 合约历史数据

```python
rqalpha.api.get_price(order_book_ids, start_date, end_date=None, frequency='1d', fields=None, adjust_type='pre', skip_suspended=False, expect_df=False)
```

获取指定合约或合约列表的历史行情（包含起止日期，日线或分钟线），<b>不能在'handle_bar'函数中进行调用</b>。

::: tip 注意，这一函数主要是为满足在研究平台编写策略习惯而引入。在编写策略中，使用 history_bars 进行数据获取会更方便。
:::

#### 参数

| 参数名         | 类型                                                     | 说明                                                                                                                                             |
|-----|-----|-----|
| order_book_ids | _Union[str, Iterable[str]]_                              | 合约代码，可传入 order_book_id, order_book_id list, symbol, symbol list                                                                          |
| start_date     | _Union[datetime.date, str]_                              | 开始日期，用户必须指定                                                                                                                           |
| end_date       | _Optional[Union[datetime.date, datetime.datetime, str]]_ | 结束日期，默认为策略当前日期前一天                                                                                                               |
| frequency      | _Optional[str]_                                          | 历史数据的频率。 现在支持**日/分钟级别/tick**的历史数据，默认为'1d'。使用者可自由选取不同频率，例如'5m'代表 5 分钟线                             |
| fields         | _Optional[Iterable[str]]_                                | 返回字段名称，见下方                                                                                                                             |
| adjust_type    | _Optional[str]_                                          | 权息修复方案。前复权 - `pre`，后复权 - `post`，不复权 - `none`。                                                                                 |
| skip_suspended | _Optional[bool]_                                         | 是否跳过停牌数据。默认为 False，不跳过，用停牌前数据进行补齐。True 则为跳过停牌期。注意，当设置为 True 时，函数 order_book_id 只支持单个合约传入 |
| expect_df      | _Optional[bool]_                                         | 是否期望始终返回 DataFrame。pandas 0.25.0 以上该参数应设为 True，以避免因试图构建 Panel 产生异常                                                 |

#### 返回

_Union[pd.DataFrame, pd.Panel, pd.Series]_

当 expect_df 为 False 时，返回值的类型如下

- 传入一个 order_book_id，多个 fields，函数会返回一个*pandas DataFrame*
- 传入一个 order_book_id，一个 field，函数会返回*pandas Series*
- 传入多个 order_book_id，一个 field，函数会返回一个*pandas DataFrame*
- 传入多个 order_book_id，函数会返回一个*pandas Panel*

| fields          | 类型              | 说明                                                    |
|-----|-----|-----|
| open            | _float_           | 开盘价                                                  |
| close           | _float_           | 收盘价                                                  |
| high            | _float_           | 最高价                                                  |
| low             | _float_           | 最低价                                                  |
| limit_up        | _float_           | 涨停价                                                  |
| limit_down      | _float_           | 跌停价                                                  |
| total_turnover  | _float_           | 总成交额                                                |
| volume          | _float_           | 总成交量                                                |
| acc_net_value   | _float_           | 累计净值（仅限基金日线数据）                            |
| unit_net_value  | _float_           | 单位净值（仅限基金日线数据）                            |
| discount_rate   | _float_           | 折价率（仅限基金日线数据）                              |
| settlement      | _float_           | 结算价 （仅限期货日线数据）                             |
| prev_settlement | _float_           | 昨日结算价（仅限期货日线数据）                          |
| open_interest   | _float_           | 累计持仓量（期货专用）                                  |
| basis_spread    | _float_           | 基差点数（股指期货专用，股指期货收盘价-标的指数收盘价） |
| trading_date    | _pandas.Timestamp_ | 交易日期（仅限期货分钟线数据），对应期货夜盘的情况      |

#### 范例

- 获取单一股票历史日线行情:

```python
get_price('000001.XSHE', start_date='2015-04-01', end_date='2015-04-12')
#[Out]
#open    close    high    low    total_turnover    volume    limit_up    limit_down
#2015-04-01    10.7300    10.8249    10.9470    10.5469    2.608977e+09    236637563.0    11.7542    9.6177
#2015-04-02    10.9131    10.7164    10.9470    10.5943    2.222671e+09    202440588.0    11.9102    9.7397
#2015-04-03    10.6486    10.7503    10.8114    10.5876    2.262844e+09    206631550.0    11.7881    9.6448
#2015-04-07    10.9538    11.4015    11.5032    10.9538    4.898119e+09    426308008.0    11.8288    9.6787
#2015-04-08    11.4829    12.1543    12.2628    11.2929    5.784459e+09    485517069.0    12.5409    10.2620
#2015-04-09    12.1747    12.2086    12.9208    12.0255    5.794632e+09    456921108.0    13.3684    10.9403
#2015-04-10    12.2086    13.4294    13.4294    12.1069    6.339649e+09    480990210.0    13.4294    10.9877
#...
```

#### get_price_change_rate - 历史涨跌幅

```python
rqalpha.api.get_price_change_rate(order_book_ids, count=1, expect_df=False)
```

获取股票/指数截止 T-1 日的日涨幅

#### 参数

| 参数名        | 类型                    | 说明                                                                                             |
|-----|-----|-----|
| id_or_symbols | _Union[str, List[str]]_ | 可输入 order_book_id, order_book_id list, symbol, symbol list                                    |
| count         | _Optional[int]_         | 回溯获取的数据个数。默认为当前能够获取到的最近的数据                                             |
| expect_df     | _Optional[bool]_        | 是否期望始终返回 DataFrame。pandas 0.25.0 以上该参数应设为 True，以避免因试图构建 Panel 产生异常 |

#### 返回

_Union[DataFrame, Series]_

当 expect_df 为 False 时，返回值的类型如下：

- 传入多个 order_book_id，函数会返回*pandas DataFrame*
- 传入一个 order_book_id，函数会返回*pandas Series*

#### 范例

- 获取平安银行以及沪深 300 指数一段时间的涨跌幅情况:

```python
get_price_change_rate(['000001.XSHE', '510050.XSHG'], 1)
# [Out]
# 2016-06-01 15:30:00.00  INFO   order_book_id  000001.XSHE  510050.XSHG
#                                date
#                                2016-05-31        0.026265     0.033964
# 2016-06-02 15:30:00.00  INFO   order_book_id  000001.XSHE  510050.XSHG
#                                date
#                                2016-06-01       -0.006635    -0.008308
```

### 股票 {#rqalpha-plus-api-data-stocks}

#### industry - 行业股票列表

```python
rqalpha.api.industry(code)
```

获得属于某一行业的所有股票列表。

#### 参数

| 参数名 | 类型                          | 说明                                                            |
|-----|-----|-----|
| code   | _str_ OR _industry_code item_ | 行业名称或行业代码。例如，农业可填写 industry_code.A01 或 'A01' |

##### 行业分类列表

我们目前使用的行业分类来自于中国国家统计局的国民经济行业分类，可以使用这里的任何一个行业代码来调用行业的股票列表：

| 行业代码 | 行业名称                                 |
|-----|-----|
| A01      | 农业                                     |
| A02      | 林业                                     |
| A03      | 畜牧业                                   |
| A04      | 渔业                                     |
| A05      | 农、林、牧、渔服务业                     |
| B06      | 煤炭开采和洗选业                         |
| B07      | 石油和天然气开采业                       |
| B08      | 黑色金属矿采选业                         |
| B09      | 有色金属矿采选业                         |
| B10      | 非金属矿采选业                           |
| B11      | 开采辅助活动                             |
| B12      | 其他采矿业                               |
| C13      | 农副食品加工业                           |
| C14      | 食品制造业                               |
| C15      | 酒、饮料和精制茶制造业                   |
| C16      | 烟草制品业                               |
| C17      | 纺织业                                   |
| C18      | 纺织服装、服饰业                         |
| C19      | 皮革、毛皮、羽毛及其制品和制鞋业         |
| C20      | 木材加工及木、竹、藤、棕、草制品业       |
| C21      | 家具制造业                               |
| C22      | 造纸及纸制品业                           |
| C23      | 印刷和记录媒介复制业                     |
| C24      | 文教、工美、体育和娱乐用品制造业         |
| C25      | 石油加工、炼焦及核燃料加工业             |
| C26      | 化学原料及化学制品制造业                 |
| C27      | 医药制造业                               |
| C28      | 化学纤维制造业                           |
| C29      | 橡胶和塑料制品业                         |
| C30      | 非金属矿物制品业                         |
| C31      | 黑色金属冶炼及压延加工业                 |
| C32      | 有色金属冶炼和压延加工业                 |
| C33      | 金属制品业                               |
| C34      | 通用设备制造业                           |
| C35      | 专用设备制造业                           |
| C36      | 汽车制造业                               |
| C37      | 铁路、船舶、航空航天和其它运输设备制造业 |
| C38      | 电气机械及器材制造业                     |
| C39      | 计算机、通信和其他电子设备制造业         |
| C40      | 仪器仪表制造业                           |
| C41      | 其他制造业                               |
| C42      | 废弃资源综合利用业                       |
| C43      | 金属制品、机械和设备修理业               |
| D44      | 电力、热力生产和供应业                   |
| D45      | 燃气生产和供应业                         |
| D46      | 水的生产和供应业                         |
| E47      | 房屋建筑业                               |
| E48      | 土木工程建筑业                           |
| E49      | 建筑安装业                               |
| E50      | 建筑装饰和其他建筑业                     |
| F51      | 批发业                                   |
| F52      | 零售业                                   |
| G53      | 铁路运输业                               |
| G54      | 道路运输业                               |
| G55      | 水上运输业                               |
| G56      | 航空运输业                               |
| G57      | 管道运输业                               |
| G58      | 装卸搬运和运输代理业                     |
| G59      | 仓储业                                   |
| G60      | 邮政业                                   |
| H61      | 住宿业                                   |
| H62      | 餐饮业                                   |
| I63      | 电信、广播电视和卫星传输服务             |
| I64      | 互联网和相关服务                         |
| I65      | 软件和信息技术服务业                     |
| J66      | 货币金融服务                             |
| J67      | 资本市场服务                             |
| J68      | 保险业                                   |
| J69      | 其他金融业                               |
| K70      | 房地产业                                 |
| L71      | 租赁业                                   |
| L72      | 商务服务业                               |
| M73      | 研究和试验发展                           |
| M74      | 专业技术服务业                           |
| M75      | 科技推广和应用服务业                     |
| N76      | 水利管理业                               |
| N77      | 生态保护和环境治理业                     |
| N78      | 公共设施管理业                           |
| O79      | 居民服务业                               |
| O80      | 机动车、电子产品和日用产品修理业         |
| O81      | 其他服务业                               |
| P82      | 教育                                     |
| Q83      | 卫生                                     |
| Q84      | 社会工作                                 |
| R85      | 新闻和出版业                             |
| R86      | 广播、电视、电影和影视录音制作业         |
| R87      | 文化艺术业                               |
| R88      | 体育                                     |
| R89      | 娱乐业                                   |
| S90      | 综合                                     |

#### 返回

_List[str]_

#### 范例

```python
def init(context):
    stock_list = industry('A01')
    logger.info("农业股票列表：" + str(stock_list))

#INITINFO 农业股票列表：['600354.XSHG', '601118.XSHG', '002772.XSHE', '600371.XSHG', '600313.XSHG', '600672.XSHG', '600359.XSHG', '300143.XSHE', '002041.XSHE', '600762.XSHG', '600540.XSHG', '300189.XSHE', '600108.XSHG', '300087.XSHE', '600598.XSHG', '000998.XSHE', '600506.XSHG']

```

#### sector - 板块股票列表

```python
rqalpha.api.sector(code)
```

获得属于某一板块的所有股票列表。

#### 参数

| 参数名 | 类型                          | 说明                                                            |
|-----|-----|-----|
| code   | _str_ OR _industry_code item_ | 行业名称或行业代码。例如，农业可填写 industry_code.A01 或 'A01' |

##### 板块分类列表

目前支持的 code 板块分类如下，其取值参考自 MSCI 发布的<a href="https://en.wikipedia.org/wiki/Global_Industry_Classification_Standard" target="_blank">全球行业标准分类</a>:

| 板块代码                  | 中文板块名称 | 英文板块名称               |
|-----|-----|-----|
| Energy                    | 能源         | energy                     |
| Materials                 | 原材料       | materials                  |
| ConsumerDiscretionary     | 非必需消费品 | consumer discretionary     |
| ConsumerStaples           | 必需消费品   | consumer staples           |
| HealthCare                | 医疗保健     | health care                |
| Financials                | 金融         | financials                 |
| RealEstate                | 房地产       | real estate                |
| InformationTechnology     | 信息技术     | information technology     |
| TelecommunicationServices | 电信服务     | telecommunication services |
| Utilities                 | 公共服务     | utilities                  |
| Industrials               | 工业         | industrials                |

#### 返回

_List[str]_

#### 范例

```python
def init(context):
    ids1 = sector("consumer discretionary")
    ids2 = sector("非必需消费品")
    ids3 = sector("ConsumerDiscretionary")
    assert ids1 == ids2 and ids1 == ids3
    logger.info(ids1)
#INIT INFO
#['002045.XSHE', '603099.XSHG', '002486.XSHE', '002536.XSHE', '300100.XSHE', '600633.XSHG', '002291.XSHE', ..., '600233.XSHG']

```

#### get_dividend - 获取分红数据

```python
rqalpha.api.get_dividend(order_book_id, start_date)
```

获取某只股票到策略当前日期前一天的分红情况（包含起止日期）。

#### 参数

| 参数名        | 类型                                    | 说明                           |
|-----|-----|-----|
| order_book_id | _str_                                   | 股票代码                       |
| start_date    | _Union[str, date, datetime, Timestamp]_ | 开始日期，需要早于策略当前日期 |

#### 返回

_Optional[ndarray]_

| 字段                          | 类型    | 说明                                                                            |
|-----|-----|-----|
| declaration_announcement_date | _str_   | 分红宣布日，上市公司一般会提前一段时间公布未来的分红派息事件                    |
| book_closure_date             | _str_   | 股权登记日                                                                      |
| dividend_cash_before_tax      | _float_ | 税前分红                                                                        |
| ex_dividend_date              | _str_   | 除权除息日，该天股票的价格会因为分红而进行调整                                  |
| payable_date                  | _str_   | 分红到帐日，这一天最终分红的现金会到账                                          |
| round_lot                     | _float_ | 分红最小单位，例如：10 代表每 10 股派发 dividend_cash_before_tax 单位的税前现金 |

#### 范例

- 获取平安银行 2013-01-04 到策略当前日期前一天的分红数据:

```python
get_dividend('000001.XSHE', start_date='20130104')
#[Out]
#array([(20130614, 20130619, 20130620, 20130620,  1.7 , 10),
#       (20140606, 20140611, 20140612, 20140612,  1.6 , 10),
#       (20150407, 20150410, 20150413, 20150413,  1.74, 10),
#       (20160608, 20160615, 20160616, 20160616,  1.53, 10)],
#      dtype=[('announcement_date', '<u4'), ('book_closure_date', '<u4'), ('ex_dividend_date', '<u4'), ('payable_date', '<u4'), ('dividend_cash_before_tax', '<f8'), ('round_lot', '<u4')])

```

#### is_suspended - 全天停牌判断

```python
rqalpha.api.is_suspended(order_book_id)
```

判断某只股票是否全天停牌。

#### 参数

| 参数名        | 类型            | 说明                                                             |
|-----|-----|-----|
| order_book_id | _str_           | 某只股票的代码或股票代码，可传入单只股票的 order_book_id, symbol |
| count         | _Optional[int]_ | 回溯获取的数据个数。默认为当前能够获取到的最近的数据             |

#### 返回

_Union[bool, DataFrame]_

#### 范例

```python
# 判断平安银行是否停牌
is_suspended('000001.XSHE')
```

#### is_st_stock - ST 股判断

```python
rqalpha.api.is_st_stock(order_book_id)
```

判断股票在一段时间内是否为 ST 股（包括 ST 与\*ST）。

ST 股是有退市风险因此风险比较大的股票，很多时候您也会希望判断自己使用的股票是否是'ST'股来避开这些风险大的股票。另外，我们目前的策略比赛也禁止了使用'ST'股。

#### 参数

| 参数名        | 类型            | 说明                                                   |
|-----|-----|-----|
| order_book_id | _str_           | 某只股票的代码，可传入单只股票的 order_book_id, symbol |
| count         | _Optional[int]_ | 回溯获取的数据个数。默认为当前能够获取到的最近的数据   |

#### 返回

_Union[bool, DataFrame]_

#### 范例

```python
is_st_stock('000001.XSHE')
```

#### get_split - 拆分数据

```python
rqalpha.api.get_split(order_book_ids, start_date=None)
```

获取某只股票到策略当前日期前一天的拆分情况（包含起止日期）。

#### 参数

| 参数名        | 类型                     | 说明                                              |
|-----|-----|-----|
| order_book_id | _Union[str, List[str]]_  | 证券代码，证券的独特的标识符，例如：'000001.XSHE' |
| start_date    | _Union[str, date, None]_ | 开始日期，用户必须指定，需要早于策略当前日期      |

#### 返回

_pandas DataFrame_ - 查询时间段内的某个股票的拆分数据

| 字段                   | 类型    | 说明                                           |
|-----|-----|-----|
| ex_dividend_date       | _str_   | 除权除息日，该天股票的价格会因为拆分而进行调整 |
| book_closure_date      | _str_   | 股权登记日                                     |
| split_coefficient_from | _float_ | 拆分因子（拆分前）                             |
| split_coefficient_to   | _float_ | 拆分因子（拆分后）                             |

例如：每 10 股转增 2 股，则 split_coefficient_from = 10, split_coefficient_to = 12.

#### 范例

```python
[In]
get_split('000001.XSHE', start_date='2010-01-04')

[Out]
                 book_closure_date payable_date  split_coefficient_from  \
ex_dividend_date
2013-06-20              2013-06-19   2013-06-20                      10

                  split_coefficient_to
ex_dividend_date
2013-06-20                        16.0
```

#### get_securities_margin - 融资融券信息

```python
rqalpha.api.get_securities_margin(order_book_ids, count=1, fields=None, expect_df=False)
```

获取融资融券信息。包括<a href="http://www.szse.cn/main/disclosure/rzrqxx/rzrqjy/" target="_blank">深证融资融券数据</a>以及<a href="http://www.sse.com.cn/market/othersdata/margin/detail/" target="_blank">上证融资融券数据</a>情况。既包括个股数据，也包括市场整体数据。
::: tip 需要注意，T 日的数据将在 T+1 日上午 09:00 左右更新，所以可能无法在 before_trading 阶段获取到上一交易日的最新数据。融资融券的开始日期为 2010 年 3 月 31 日。
:::

#### 参数

| 参数名        | 类型                        | 说明                                                                                                                                    |
|-----|-----|-----|
| id_or_symbols | _Union[str, Iterable[str]]_ | 可输入 order_book_id, order_book_id list, symbol, symbol list。另外，输入'XSHG'或'sh'代表整个上证整体情况；'XSHE'或'sz'代表深证整体情况 |
| count         | _Optional[int]_             | 回溯获取的数据个数。默认为当前能够获取到的最近的数据                                                                                    |
| fields        | _Optional[str]_             | 期望返回的字段，默认为所有字段。见下方列表                                                                                              |
| expect_df     | _Optional[bool]_            | 是否期望始终返回 DataFrame。pandas 0.25.0 以上该参数应设为 True，以避免因试图构建 Panel 产生异常                                        |

#### 返回

_Union[pd.Series, pd.DataFrame, pd.Panel]_

| 字段                     | 类型    | 说明         |
|-----|-----|-----|
| margin_balance           | _float_ | 融资余额     |
| buy_on_margin_value      | _float_ | 融资买入额   |
| margin_repayment         | _float_ | 融资偿还额   |
| short_balance            | _float_ | 融券余额     |
| short_balance_quantity   | _float_ | 融券余量     |
| short_sell_quantity      | _float_ | 融券卖出量   |
| short_repayment_quantity | _float_ | 融券偿还量   |
| total_balance            | _float_ | 融资融券余额 |

#### 范例

- 获取沪深两个市场一段时间内的融资余额

```python
[In]
logger.info(get_securities_margin('510050.XSHG', count=5))
[Out]
margin_balance buy_on_margin_value short_sell_quantity margin_repayment short_balance_quantity short_repayment_quantity short_balance total_balance
2016-08-01 7.811396e+09 50012306.0 3597600.0 41652042.0 15020600.0 1645576.0 NaN NaN
2016-08-02 7.826381e+09 34518238.0 2375700.0 19532586.0 14154000.0 3242300.0 NaN NaN
2016-08-03 7.733306e+09 17967333.0 4719700.0 111043009.0 16235600.0 2638100.0 NaN NaN
2016-08-04 7.741497e+09 30259359.0 6488600.0 22068637.0 17499000.0 5225200.0 NaN NaN
2016-08-05 7.726343e+09 25270756.0 2865863.0 40423859.0 14252363.0 6112500.0 NaN NaN
```

- 获取沪深两个市场一段时间内的融资余额

```python
[In]
logger.info(get_securities_margin(['XSHE', 'XSHG'], count=5, fields='margin_balance'))
[Out]
  XSHE  XSHG
2016-08-01 3.837627e+11 4.763557e+11
2016-08-02 3.828923e+11 4.763931e+11
2016-08-03 3.823545e+11 4.769321e+11
2016-08-04 3.833260e+11 4.776380e+11
2016-08-05 3.812751e+11 4.766928e+11
```

- 获取上证个股以及整个上证市场融资融券情况

```python
[In]
logger.info(get_securities_margin(['XSHG', '601988.XSHG', '510050.XSHG'], count=5))
[Out]
<class 'pandas.core.panel.Panel'>
Dimensions: 8 (items) x 5 (major_axis) x 3 (minor_axis)
Items axis: margin_balance to total_balance
Major_axis axis: 2016-08-01 00:00:00 to 2016-08-05 00:00:00
Minor_axis axis: XSHG to 510050.XSHG
```

- 获取 50ETF 融资偿还额情况

```python
[In]
logger.info(get_securities_margin('510050.XSHG', count=5, fields='margin_repayment'))
[Out]
2016-08-01     41652042.0
2016-08-02     19532586.0
2016-08-03    111043009.0
2016-08-04     22068637.0
2016-08-05     40423859.0
Name: margin_repayment, dtype: float64
```

#### concept - 概念股列表

```python
rqalpha.api.concept(*concept_names)
```

获取 T 日的概念股列表

#### 参数

| 参数名        | 类型  | 说明                                                                                           |
|-----|-----|-----|
| concept_names | _str_ | 概念名称。可以从概念列表中选择一个或多个概念填写, 可以通过 rqdatac.concept_list() 获取概念列表 |

#### 返回

_List[str]_ - 属于该概念的股票 order_book_id

#### 范例

- 得到一个概念的股票列表：

```python
concept('民营医院')
# [Out]
# ['600105.XSHG',
# '002550.XSHE',
# '002004.XSHE',
# '002424.XSHE',
# ...]
```

- 得到某几个概念的股票列表:

```python
concept('民营医院', '国企改革')
# [Out]
# ['601607.XSHG',
# '600748.XSHG',
# '600630.XSHG',
# ...]
```

#### get_margin_stocks - 融资融券列表

```python
rqalpha.api.get_margin_stocks(exchange=None, margin_type='all')
```

获取某个日期深证、上证融资融券股票列表。

#### 参数

| 参数名      | 类型            | 说明                                                                                              |
|-----|-----|-----|
| exchange    | _Optional[str]_ | 交易所，默认为 None，返回所有字段。可选字段包括：'XSHE', 'sz' 代表深交所；'XSHG', 'sh' 代表上交所 |
| margin_type | _str_           | 'stock' 代表融券卖出，'cash'，代表融资买入，'all'，代表包含融资和融券，默认为'all'                |

#### 返回

_List[str]_

#### 范例

- 获取沪深市场的融券卖出列表:

```python
get_margin_stocks(exchange=None,margin_type='stock')
# [Out]
# ['000001.XSHE',
# '000002.XSHE',
# '000006.XSHE',
# ...]
```

- 获取上证融资买入列表:

```python
get_margin_stocks(exchange='XSHG',margin_type='cash')
# [Out]
# ['510050.XSHG',
# '510160.XSHG',
# '510180.XSHG',
# ...]
```

#### get_shares - 流通股信息

```python
rqalpha.api.get_shares(order_book_ids, count=1, fields=None, expect_df=False)
```

#### 参数

| 参数名         | 类型                    | 说明                                                                                             |
|-----|-----|-----|
| order_book_ids | _Union[str, List[str]]_ | 可输入 order_book_id, order_book_id list, symbol, symbol list                                    |
| count          | _Optional[int]_         | 回溯获取的数据个数。默认为当前能够获取到的最近的数据                                             |
| fields         | _Optional[str]_         | 期望返回的字段，默认为所有字段。见下方列表                                                       |
| expect_df      | _Optional[bool]_        | 是否期望始终返回 DataFrame。pandas 0.25.0 以上该参数应设为 True，以避免因试图构建 Panel 产生异常 |

#### 返回

_Union[DataFrame, Series]_

| 字段                   | 类型    | 说明                                 |
|-----|-----|-----|
| total                  | _float_ | 总股本                               |
| circulation_a          | _float_ | 流通 A 股                            |
| management_circulation | _float_ | 已过禁售期的高管持有的股份（已废弃） |
| non_circulation_a      | _float_ | 非流通 A 股                          |
| total_a                | _float_ | A 股总股本                           |

#### 范例

- 获取平安银行总股本数据:

```python
logger.info(get_shares('000001.XSHE', count=5, fields='total'))
```

#### get_turnover_rate - 历史换手率

```python
rqalpha.api.get_turnover_rate(order_book_ids, count=1, fields=None, expect_df=False)
```

获取截止 T-1 交易日的换手率数据

#### 参数

| 参数名         | 类型                    | 说明                                                                                             |
|-----|-----|-----|
| order_book_ids | _Union[str, List[str]]_ | 可输入 order_book_id, order_book_id list, symbol, symbol list                                    |
| count          | _Optional[int]_         | 回溯获取的数据个数。默认为当前能够获取到的最近的数据                                             |
| fields         | _Optional[str]_         | 期望返回的字段，默认为所有字段。见下方列表                                                       |
| expect_df      | _Optional[bool]_        | 是否期望始终返回 DataFrame。pandas 0.25.0 以上该参数应设为 True，以避免因试图构建 Panel 产生异常 |

#### 返回

_Union[pd.Series, pd.DataFrame, pd.Panel]_

| fields       | 说明                 |
|-----|-----|
| today        | 当天换手率           |
| week         | 过去一周平均换手率   |
| month        | 过去一个月平均换手率 |
| three_month  | 过去三个月平均换手率 |
| six_month    | 过去六个月平均换手率 |
| year         | 过去一年平均换手率   |
| current_year | 当年平均换手率       |
| total        | 上市以来平均换手率   |

#### 范例

- 获取平安银行历史换手率情况:

```python
[In]
logger.info(get_turnover_rate('000001.XSHE', count=5))
[Out]
             today    week   month  three_month  six_month    year  \
2016-08-01  0.5190  0.4478  0.3213       0.2877     0.3442  0.5027
2016-08-02  0.3070  0.4134  0.3112       0.2843     0.3427  0.5019
2016-08-03  0.2902  0.3460  0.3102       0.2823     0.3432  0.4982
2016-08-04  0.9189  0.4938  0.3331       0.2914     0.3482  0.4992
2016-08-05  0.4962  0.5031  0.3426       0.2960     0.3504  0.4994

            current_year   total
2016-08-01        0.3585  1.1341
2016-08-02        0.3570  1.1341
2016-08-03        0.3565  1.1339
2016-08-04        0.3604  1.1339
2016-08-05        0.3613  1.1338
```

#### get_factor - 因子

```python
rqalpha.api.get_factor(order_book_ids, factors, count=1, universe=None, expect_df=False)
```

获取股票截止 T-1 日的因子数据

#### 参数

| 参数名         | 类型                                | 说明                                                                                                                                 |
|-----|-----|-----|
| order_book_ids | _Union[str, List[str]]_             | 合约代码，可传入 order_book_id, order_book_id list, symbol, symbol list                                                              |
| factors        | _Union[str, List[str]]_             | 因子名称，可查询 rqdatac.get_all_factor_names() 得到所有有效因子字段                                                                 |
| count          | _Optional[int]_                     | 获取多少个交易日的数据                                                                                                               |
| universe       | _Optional[Union[str, List[Union]]]_ | 当获取横截面因子时，universe 指定了因子计算时的股票池                                                                                |
| expect_df      | _Optional[bool]_                    | 默认为 False。当设置为 True 时，总是返回 multi-index DataFrame。pandas 0.25.0 以上该参数应设为 True，以避免因试图构建 Panel 产生异常 |

#### 返回

_pandas DataFrame_

#### 范例

```python
# 获取平安银行的市盈率因子数据
get_factor('000001.XSHE', 'pe_ratio',count=5)
```

#### get_industry - 行业股票列表

```python
rqalpha.api.get_industry(industry, source='citics')
```

获取指定行业的股票列表。

#### 参数

| 参数名   | 类型            | 说明                                  |
|-----|-----|-----|
| industry | _str_           | 行业名字                              |
| source   | _Optional[str]_ | 默认为中信(citics)，可选聚源(gildata) |

#### 返回

_List[str]_

#### 范例

```python
# 获取"银行"行业的所有股票
get_industry('银行')
```

#### get_instrument_industry - 股票行业分类

```python
rqalpha.api.get_instrument_industry(order_book_ids, source='citics', level=1)
```

获取指定股票所属的行业分类。

#### 参数

| 参数名         | 类型                    | 说明                                               |
|-----|-----|-----|
| order_book_ids | _Union[str, List[str]]_ | 合约代码，可传入 order_book_id, order_book_id list |
| source         | _Optional[str]_         | 默认为中信(citics)，可选聚源(gildata)              |
| level          | _Optional[int]_         | 默认为 1，可选 0 1 2 3，0 表示返回所有级别         |

#### 返回

_DataFrame_

#### 范例

```python
get_instrument_industry('000001.XSHE')
```

#### get_stock_connect - 沪深港通持股信息

```python
rqalpha.api.get_stock_connect(order_book_ids, count=1, fields=None, expect_df=False)
```

获取截止 T-1 日 A 股股票在香港上市交易的持股情况

#### 参数

| 参数名         | 类型                    | 说明                                                                                             |
|-----|-----|-----|
| order_book_ids | _Union[str, List[str]]_ | 合约代码，可输入 order_book_id, order_book_id list, symbol, symbol list，这里输入的是 A 股编码   |
| count          | _Optional[int]_         | 回溯获取的数据个数。默认为当前能够获取到的最近的数据                                             |
| fields         | _Optional[str]_         | 期望返回的字段，默认为所有字段。见下方列表                                                       |
| expect_df      | _Optional[bool]_        | 是否期望始终返回 DataFrame。pandas 0.25.0 以上该参数应设为 True，以避免因试图构建 Panel 产生异常 |

#### 返回

_DataFrame_

| 字段                   | 类型    | 说明           |
|-----|-----|-----|
| shares_holding         | _float_ | 持股量         |
| holding_ratio          | _float_ | 持股比例       |
| adjusted_holding_ratio | _float_ | 调整后持股比例 |

#### 范例

- 获取平安银行数据

```python
[In]
logger.info(get_stock_connect('000001.XSHE', count=1, fields='shares_holding'))
[Out]
2018-05-10    414866956
Name: total, dtype: float64
```

#### current_performance - 财务快报数据

```python
rqalpha.api.current_performance(order_book_id, info_date=None, quarter=None, interval='1q', fields=None)
```

默认返回给定的 order_book_id 当前最近一期的快报数据

#### 参数

| 参数名        | 类型                              | 说明                                                                                                                                                                                                                                             |
|-----|-----|-----|
| order_book_id | _str_                             | 合约代码                                                                                                                                                                                                                                         |
| info_date     | _Optional[str]_                   | yyyymmdd 或者 yyyy-mm-dd。如果不填(info_date 和 quarter 都为空)，则返回策略运行当前日期的最新发布的快报。如果填写，则从 info_date 当天或者之前最新的报告期开始抓取                                                                               |
| quarter       | _Optional[str]_                   | info_date 参数优先级高于 quarter。如果 info_date 填写了日期，则不查看 quarter 这个字段。如果 info_date 没有填写而 quarter 有填写，则财报回溯查询的起始报告期，例如'2015q2', '2015q4'分别代表 2015 年半年报以及年报。默认只获取当前报告期财务信息 |
| interval      | _Optional[str]_                   | 查询财务数据的间隔。例如，填写'5y'，则代表从报告期开始回溯 5 年，每年为相同报告期数据；'3q'则代表从报告期开始向前回溯 3 个季度。不填写默认抓取一期                                                                                               |
| fields        | _Optional[Union[str, List[str]]]_ | 抓取对应有效字段返回。默认返回所有字段。具体快报字段可参看 Ricequant 官网财务数据文档                                                                                                                                                            |

#### 返回

_pandas DataFrame_

#### 范例

```python
# 获取平安银行的财务快报数据
current_performance('000001.XSHE')
```

#### get_pit_financials_ex - 季度财务信息

```python
rqalpha.api.get_pit_financials_ex(order_book_ids, fields, count, statements='latest')
```

以给定一个报告期回溯的方式获取季度基础财务数据（三大表），即利润表，资产负债表，现金流量表。

#### 参数

| 参数名         | 类型                    | 说明                                                                                              |
|-----|-----|-----|
| order_book_ids | _Union[str, List[str]]_ | 合约代码，可传入 order_book_id, order_book_id list，这里输入的是 A 股编码                         |
| fields         | _Union[str, List[str]]_ | 需要返回的财务字段                                                                                |
| count          | _int_                   | 回溯获取的数据个数。默认为当前能够获取到的最近的数据                                              |
| statements     | _str_                   | 设置 statements 为 all 时返回所有记录，statements 等于 latest 时返回最新的一条记录，默认为 latest |

#### 返回

_Optional[DataFrame]_

| 字段        | 类型   | 说明                                                                                                                                                                                                |
|-----|-----|-----|
| fields      | _list_ | 需要返回的财务字段。支持的字段仅限**三大基础财报**,具体可以参看财务数据页介绍。                                                                                                                     |
| if_adjusted | _int_  | 是否为非当期财报数据, 0 代表当期，1 代表非当期（比如 18 年的财报会披露本期和上年同期的数值，17 年年报的财务数值在 18 年年报中披露的记录则为非当期， 17 年年报的财务数值在 17 年年报中披露则为当期。 |
| quarter     | _str_  | 报告期                                                                                                                                                                                              |
| info_date   | _str_  | 公告发布日                                                                                                                                                                                          |

#### 范例

- 获取股票最近一个报告期的 revenue、net_profit 数据

```python
[In]
get_pit_financials_ex(fields=['revenue','net_profit'], count=0,order_book_ids=['000001.XSHE'],statements='latest')
[Out]
                  info_date net_profit revenue net_profit
order_book_id quarter
000001.XSHE 2015q4     2017-03-17     2.186500e+10 9.616300e+10
```

### 指数 {#rqalpha-plus-api-data-index}

#### index_components - 指数成分股

```python
rqalpha.api.index_components(order_book_id, date=None)
```

获取某一指数的股票构成列表，也支持指数的历史构成查询。

#### 参数

| 参数名        | 类型                     | 说明                                                                   |
|-----|-----|-----|
| order_book_id | _str_                    | 指数代码，可传入 order_book_id                                         |
| date          | _Union[str, date, None]_ | 查询日期，默认为策略当前日期。如指定，则应保证该日期不晚于策略当前日期 |

#### 返回

_List[str]_

#### 范例

- 得到上证指数在策略当前日期的构成股票的列表:

```python
index_components('000001.XSHG')
#[Out]['600000.XSHG', '600004.XSHG', ...]
```

#### index_weights - 指数成分股权重

```python
rqalpha.api.index_weights(order_book_id, date=None)
```

获取 T-1 日的指数权重

#### 参数

| 参数名        | 类型                     | 说明                |
|-----|-----|-----|
| order_book_id | _str_                    | 指数                |
| date          | _Union[str, date, None]_ | 可选，默认为 T-1 日 |

#### 返回

_Series_

#### 范例

- 获取上证 50 指数上个交易日的指数构成

```python
index_weights('000016.XSHG')
# [Out]
# Order_book_id
# 600000.XSHG    0.03750
# 600010.XSHG    0.00761
# 600016.XSHG    0.05981
# 600028.XSHG    0.01391
# 600029.XSHG    0.00822
# 600030.XSHG    0.03526
# 600036.XSHG    0.04889
# 600050.XSHG    0.00998
# 600104.XSHG    0.02122
```

### 期货 {#rqalpha-plus-api-data-futures}

#### futures.get_dominant - 期货主力合约

```python
rqalpha.api.futures.get_dominant(underlying_symbol, rule=0)
```

获取某一期货品种策略当前日期的主力合约代码。 合约首次上市时，以当日收盘同品种持仓量最大者作为从第二个交易日开始的主力合约。当同品种其他合约持仓量在收盘后超过当前主力合约 1.1 倍时，从第二个交易日开始进行主力合约的切换。日内不会进行主力合约的切换。

#### 参数

| 参数名            | 类型            | 说明                                                                                                                                                                             |
|-----|-----|-----|
| underlying_symbol | _str_           | 期货合约品种，例如沪深 300 股指期货为'IF'                                                                                                                                        |
| rule              | _Optional[int]_ | 默认是 rule=0,采用最大昨仓为当日主力合约，每个合约只能做一次主力合约，不会重复出现。针对股指期货，只在当月和次月选择主力合约。当 rule=1 时，主力合约的选取只考虑最大昨仓这个条件 |

#### 返回

_Optional[str]_

#### 范例

- 获取某一天的主力合约代码（策略当前日期是 20160801）:

```python
futures.get_dominant('IF')
#[Out]
#'IF1608'
```

#### futures.get_member_rank - 期货会员持仓等排名

```python
rqalpha.api.futures.get_member_rank(which, count=1, rank_by='short')
```

获取截止 T-1 日的期货或品种的会员排名情况

#### 参数

| 参数名  | 类型  | 说明                             |
|-----|-----|-----|
| which   | _str_ | 期货合约或品种                   |
| count   | _int_ | 获取多少个交易日的数据，默认为 1 |
| rank_by | _str_ | short/long                       |

#### 返回

_DataFrame_

#### 范例

```python
futures.get_member_rank('IF2301')
```

#### futures.get_warehouse_stocks - 期货仓单数据

```python
rqalpha.api.futures.get_warehouse_stocks(underlying_symbols, count=1)
```

获取截止 T-1 日的期货仓单数据

#### 参数

| 参数名             | 类型                    | 说明                             |
|-----|-----|-----|
| underlying_symbols | _Union[str, List[str]]_ | 期货品种，可以为 str 或列表      |
| count              | _int_                   | 获取多少个交易日的数据，默认为 1 |

#### 返回

_DataFrame_

#### 范例

```python
futures.get_warehouse_stocks('CU2301')
```

#### futures.get_dominant_price - 期货主力合约连续合约行情数据

```python
rqalpha.api.futures.get_dominant_price(underlying_symbols, start_date=None, end_date=None, frequency='1d', fields=None, adjust_type='pre', adjust_method='prev_close_spread')
```

获取主力合约行情数据

#### 参数

| 参数名             | 类型                                                     | 说明                                                                                                                                                                                                      |
|-----|-----|-----|
| underlying_symbols | _str or str list_                                        | 期货合约品种，可传入 underlying_symbol, underlying_symbol list                                                                                                                                            |
| start_date         | _str, datetime.date, datetime.datetime, pandas.Timestamp_ | 开始日期, 最小日期为 20100104                                                                                                                                                                             |
| end_date           | _str, datetime.date, datetime.datetime, pandas.Timestamp_ | 结束日期                                                                                                                                                                                                  |
| frequency          | _str_                                                    | 历史数据的频率。支持/日/分钟/tick 级别的历史数据，默认为'1d'。1m-分钟线，1d-日线，分钟可选取不同频率，例如'5m'代表 5 分钟线                                                                               |
| fields             | _str or str list_                                        | 字段名称列表                                                                                                                                                                                              |
| adjust_type        | _str_                                                    | 复权方式，不复权 - none，前复权 - pre，后复权 - post                                                                                                                                                      |
| adjust_method      | _str_                                                    | 复权方法，prev_close_spread/open_spread:基于价差复权因子进行复权，prev_close_ratio/open_ratio:基于比例复权因子进行复权，默认为'prev_close_spread'，adjust_type 为 None 时，adjust_method 复权方法设置无效 |

#### 返回

_MultiIndex DataFrame_

#### 范例

- 获取基于价差前复权计算的主力合约数据（策略当前日期是 2015-01-27，则以策略当天为准，而不是已现实最新日期为准来计算复权因子）:

```python
futures.get_dominant_price(underlying_symbols='CU', start_date='2015-01-20', end_date='2015-01-23', adjust_type="pre",
                   adjust_method="prev_close_spread", fields=["close", "settlement"])
#[Out]
#                               close     settlement
# underlying_symbol date
# CU                2015-01-20  40990.0     41080.0
#                   2015-01-21  41000.0     41060.0
#                   2015-01-22  41300.0     41340.0
#                   2015-01-23  40750.0     40950.0
#                   2015-01-26  39250.0     39660.0
```

### 宏观经济 {#rqalpha-plus-api-data-macro}

#### econ.get_reserve_ratio - 存款准备金率

```python
rqalpha.api.econ.get_reserve_ratio(reserve_type='all', n=1)
```

获取截止 T 日的存款准备金率

#### 参数

| 参数名       | 类型  | 说明                                                                                             |
|-----|-----|-----|
| reserve_type | _str_ | 目前有大型金融机构（'major'） 和 其他金融机构（'other'）两种分类。默认为 all，即所有类别都会返回 |
| n            | _int_ | 返回最近 n 个生效日期的存款准备金率数据                                                          |

#### 返回

_Optional[DataFrame]_

#### 范例

```python
econ.get_reserve_ratio(reserve_type='major')
```

#### econ.get_money_supply - 货币供应量

```python
rqalpha.api.econ.get_money_supply(n=1)
```

获取货币供应量数据。

#### 参数

| 参数名 | 类型  | 说明                                        |
|-----|-----|-----|
| n      | _int_ | 返回前 n 个消息公布日期的货币供应量指标数据 |

#### 返回

_Optional[DataFrame]_

#### 范例

```python
econ.get_money_supply(n = 1)
```
