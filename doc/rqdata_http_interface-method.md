# 接口方法 {#interface-method}

## 规则 {#interface-rule}

HTTP 接口方法与 [Python API](../python/index-rqdatac.md) 是通用的，这里举几个不同返回类型的示例。

## 示例 {#interface-example}

### Instrument{#interface-instrument}

#### 范例

- 获取000001.XSHE 合约的最新基本信息，返回一个 instrument 对象。详见 [instruments](../python/generic-api.md#rqdata-API-instruments)

```python
[In] instruments(order_book_ids='000001.XSHE', market='cn')
[Out]
Instrument(order_book_id='000001.XSHE', industry_code='J66', market_tplus=1, symbol='平安银行', special_type='Normal', exchange='XSHE', status='Active', type='CS', de_listed_date='0000-00-00', listed_date='1991-04-03', sector_code_name='金融', abbrev_symbol='PAYH', sector_code='Financials', round_lot=100, trading_hours='09:31-11:30,13:01-15:00', board_type='MainBoard', industry_name='货币金融服务', issue_price=40.0, trading_code='000001', office_address='中国广东省深圳市深南东路5047号;中国广东省深圳市福田区益田路5023号平安金融中心B座', province='广东省', citics_industry_code='40', citics_industry_name='银行')
```

- HTTP 请求：
```json
{
  "method": "instruments",
  "order_book_ids": "000001.XSHE",
  "market": "cn"
}
```

- HTTP 返回：
```
order_book_id,industry_code,market_tplus,symbol,special_type,exchange,status,type,de_listed_date,listed_date,sector_code_name,abbrev_symbol,sector_code,round_lot,trading_hours,board_type,industry_name,issue_price,trading_code,office_address,province
000001.XSHE,J66,1,平安银行,Normal,XSHE,Active,CS,0000-00-00,1991-04-03,金融,PAYH,Financials,100,"09:31-11:30,13:01-15:00",MainBoard,货币金融服务,40.0,000001,中国广东省深圳市深南东路5047号;中国广东省深圳市福田区益田路5023号平安金融中心B座,广东省


```


### Tick{#interface-tick}

#### 范例

- 获取期权合约 000001.XSHE 当前快照数据，返回一个Tick 对象。详见 [current_snapshot](../python/generic-api.md#rqdata-API-current_snapshot)

```python
[In] current_snapshot(order_book_ids='000001.XSHE', market='cn')
[Out]
Tick(ask_vols: [298000.0, 310000.0, 250500.0, 455600.0, 322200.0], asks: [11.62, 11.63, 11.64, 11.65, 11.66], bid_vols: [600.0, 197900.0, 285800.0, 1248000.0, 911100.0], bids: [11.61, 11.6, 11.59, 11.58, 11.57], close: nan, datetime: 2025-11-25 09:43:30, high: 11.64, iopv: nan, last: 11.61, limit_down: 10.44, limit_up: 12.76, low: 11.58, num_trades: 7350, open: 11.61, open_interest: None, order_book_id: 000001.XSHE, prev_close: 11.6, prev_iopv: nan, prev_settlement: None, settlement: nan, total_turnover: 166692935, trading_phase_code: T, volume: 14367878.0)
```
- HTTP 请求：
```json
{
  "method": "current_snapshot",
  "order_book_ids": "000001.XSHE",
  "market": "cn"
}
```
- HTTP 返回：
```
order_book_id,close,datetime,high,iopv,last,limit_down,limit_up,low,num_trades,open,open_interest,prev_close,prev_iopv,prev_settlement,settlement,total_turnover,trading_phase_code,volume,ask0,ask1,ask2,ask3,ask4,ask_vol0,ask_vol1,ask_vol2,ask_vol3,ask_vol4,bid0,bid1,bid2,bid3,bid4,bid_vol0,bid_vol1,bid_vol2,bid_vol3,bid_vol4
000001.XSHE,,2025-11-25 09:43:45,11.64,,11.61,10.44,12.76,11.58,7384,11.61,,11.6,,,,167144493,T,14406778.0,11.61,11.62,11.63,11.64,11.65,300.0,366200.0,681000.0,250600.0,405600.0,11.6,11.59,11.58,11.57,11.56,231600.0,311100.0,1270100.0,913100.0,1055700.0

```

### List{#interface-list}

#### 范例

- 获取期货可交易合约列表, 返回可交易的合约List。详见 [futures.get_contracts](../python/futures-mod.md#rqdata-API-futures-get_contracts)

```python
[In]
futures.get_contracts(underlying_symbol='IF', date=20240107, market='cn')
[Out]
['IF2401', 'IF2402', 'IF2403', 'IF2406']
```
- HTTP 请求：
```json
{
  "method": "futures.get_contracts",
  "underlying_symbol": "IF",
  "date": 20250107,
  "market": "cn"
}
```
- HTTP 返回：
```
order_book_id
IF2501
IF2502
IF2503
IF2506

```


### Series{#interface-series}

#### 范例

- 获取某一期货品种对应主力合约，返回Pandas.Series。详见 [futures.get_dominant](../python/futures-mod.md#rqdata-API-futures-get_dominant)

```python
[In]
futures.get_dominant(underlying_symbol='IF', start_date=20250107, end_date=20250108,  market='cn')
[Out]
date
2025-01-07    IF2501
2025-01-08    IF2501
Name: dominant, dtype: object
```

- HTTP 请求：
```json
{
  "method": "futures.get_dominant",
  "underlying_symbol": "IF",
  "start_date": 20250107,
  "end_date": 20250108,
  "market": "cn"
}
```

- HTTP 返回：
```
date,dominant
2025-01-07,IF2501
2025-01-08,IF2501

```


### Dataframe{#interface-dataframe}

#### 范例

- 获取股票列表不复权日线，返回Pandas.Dataframe。详见 [get_price](../python/generic-api.md#rqdata-API-get_price-genericapi)

```python
[In]
get_price(order_book_ids=['000001.XSHE', '000002.XSHE'], start_date='2019-04-01', end_date='2019-04-01',adjust_type='none')
[Out]
                        low	total_turnover	open	limit_up	volume	limit_down	num_trades	high	close	prev_close
order_book_id	date										
000001.XSHE	2019-04-01	12.83	2.588269e+09	12.83	14.10	195140119.0	11.54	79511.0	13.55	13.18	12.82
000002.XSHE	2019-04-01	31.00	3.449266e+09	31.02	33.79	107851511.0	27.65	76969.0	33.10	32.07	30.72

```

- HTTP 请求：
```json
{
  "method": "get_price",
  "order_book_ids": ["000001.XSHE", "000002.XSHE"],
  "start_date": 20190401,
  "end_date": 20190401,
  "adjust_type": "none"
}
```

- HTTP 返回
```
order_book_id,datetime,close,high,limit_down,limit_up,low,num_trades,open,prev_close,total_turnover,volume
000001.XSHE,2019-04-01,13.18,13.55,11.54,14.1,12.83,79511.0,12.83,12.82,2588268668.0,195140119.0
000002.XSHE,2019-04-01,32.07,33.1,27.65,33.79,31.0,76969.0,31.02,30.72,3449265526.0,107851511.0

```