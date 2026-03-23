# 类 {#rqalpha-plus-api-types}

### Context - 策略上下文 {#rqalpha-plus-api-types-context}

```python
class rqalpha.core.strategy_context.StrategyContext
```

| 属性           | 类型                                             | 说明                                                                                                                                                                                         |
| -------------- | ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| future_account | _[Account](#rqalpha-plus-api-types-account)_     | 期货账户                                                                                                                                                                                     |
| now            | _datetime_                                       | 当前 Bar/Tick 所对应的时间                                                                                                                                                                   |
| portfolio      | _[Portfolio](#rqalpha-plus-api-types-portfolio)_ | 策略投资组合，可通过该对象获取当前策略账户、持仓等信息                                                                                                                                       |
| run_info       | _[RunInfo](#rqalpha-plus-api-types-runinfo)_     | 策略运行信息                                                                                                                                                                                 |
| stock_account  | _[Account](#rqalpha-plus-api-types-account)_     | 股票账户                                                                                                                                                                                     |
| universe       | _Set[str]_                                       | 在运行 update_universe(), subscribe() 或者 unsubscribe() 的时候，合约池会被更新。<br/>需要注意，合约池内合约的交易时间（包含股票的策略默认会在股票交易时段触发）是 handle_bar 被触发的依据。 |

### RunInfo - 策略运行信息 {#rqalpha-plus-api-types-runinfo}

```python
class rqalpha.core.strategy_context.RunInfo(config)
```

| 属性                          | 类型    | 说明             |
| ----------------------------- | ------- | ---------------- |
| commission_multiplier         | _float_ | 手续费倍率       |
| end_date                      | _date_  | 策略的结束日期   |
| frequency                     | _str_   | '1d'或'1m'       |
| future_starting_cash          | _float_ | 期货账户初始资金 |
| futures_commission_multiplier | _float_ | 期货手续费倍率   |
| margin_multiplier             | _float_ | 保证金倍率       |
| matching_type                 | _str_   | 撮合方式         |
| run_type                      | _str_   | 运行类型         |
| slippage                      | _float_ | 滑点水平         |
| start_date                    | _date_  | 策略的开始日期   |
| stock_commission_multiplier   | _float_ | 股票手续费倍率   |
| stock_starting_cash           | _float_ | 股票账户初始资金 |

### Bar - k 线行情 {#rqalpha-plus-api-types-bar}

```python
class rqalpha.model.bar.BarObject(instrument, data, dt=None)
```

Bases: rqalpha.model.bar.PartialBarObject

| 属性            | 类型                | 说明                           |
| --------------- | ------------------- | ------------------------------ |
| close           | _float_             | 收盘价                         |
| datetime        | _datetime.datetime_ | 时间戳                         |
| high            | _float_             | 最高价                         |
| is_trading      | _bool_              | 是否有成交量                   |
| last            | _float_             | 当前最新价                     |
| limit_down      | _float_             | 跌停价                         |
| limit_up        | _float_             | 涨停价                         |
| low             | _float_             | 最低价                         |
| open            | _float_             | 开盘价                         |
| open_interest   | _float_             | 截止到当前的持仓量（期货专用） |
| order_book_id   | _str_               | 交易标的代码                   |
| prev_close      | _float_             | 昨日收盘价                     |
| prev_settlement | _float_             | 昨日结算价（期货专用）         |
| settlement      | _float_             | 结算价（期货专用）             |
| symbol          | _str_               | 合约简称                       |
| total_turnover  | _float_             | 截止到当前的成交额             |
| volume          | _float_             | 截止到当前的成交量             |

### 基金 bar 说明 {#rqalpha-plus-api-types-fund-bar}

当开启基金 mod 时，货币基金 bar 数据新增下列字段，基金的高开低收(high/open/low/close)字段为单位净值(unit_net_value)字段

| 属性                  | 类型    | 说明                                                                            |
| --------------------- | ------- | ------------------------------------------------------------------------------- |
| daily_profit          | _float_ | 每万元收益（日结型货币基金专用）                                                |
| weekly_yield          | _float_ | 7 日年化收益率（日结型货币基金专用）                                            |
| subscribe_status      | _str_   | 订阅状态。开放 - Open, 暂停 - Suspended, 限制大额申购 - Limited, 封闭期 - Close |
| redeem_status         | _str_   | 赎回状态。开放 - Open, 暂停 - Suspended, 限制大额赎回 - Limited, 封闭期 - Close |
| subscribe_upper_limit | _float_ | 申购上限（金额）                                                                |
| subscribe_lower_limit | _float_ | 申购下限（金额）                                                                |
| redeem_lower_limit    | _float_ | 赎回下限（份额）                                                                |

### Tick - 快照行情 {#rqalpha-plus-api-types-tick}

```python
class rqalpha.model.tick.TickObject(instrument, tick_dict)
```

Bases: object

| 属性            | 类型                | 说明                                             |
| --------------- | ------------------- | ------------------------------------------------ |
| ask_vols        | _list_              | 卖出报盘数量，ask_vols[0]代表盘口卖一档报盘数量  |
| asks            | _list_              | 卖出报盘价格，asks[0]代表盘口卖一档报盘价        |
| bid_vols        | _list_              | 买入报盘数量，bids_vols[0]代表盘口买一档报盘数量 |
| bids            | _list_              | 买入报盘价格，bids[0]代表盘口买一档报盘价        |
| datetime        | _datetime.datetime_ | 当前快照数据的时间戳                             |
| high            | _float_             | 截止到当前的最高价                               |
| last            | _float_             | 当前最新价                                       |
| limit_down      | _float_             | 跌停价                                           |
| limit_up        | _float_             | 涨停价                                           |
| low             | _float_             | 截止到当前的最低价                               |
| open            | _float_             | 当日开盘价                                       |
| open_interest   | _float_             | 截止到当前的持仓量（期货专用）                   |
| order_book_id   | _str_               | 标的代码                                         |
| prev_close      | _float_             | 昨日收盘价                                       |
| prev_settlement | _float_             | 昨日结算价（期货专用）                           |
| total_turnover  | _float_             | 截止到当前的成交额                               |
| volume          | _float_             | 截止到当前的成交量                               |

### Order - 订单 {#rqalpha-plus-api-types-order}

```python
class rqalpha.model.order.Order
```

Bases: object

| 属性               | 类型                                                                | 说明                                             |
| ------------------ | ------------------------------------------------------------------- | ------------------------------------------------ |
| avg_price          | _float_                                                             | 成交均价                                         |
| datetime           | _datetime.datetime_                                                 | 订单创建时间                                     |
| filled_quantity    | _int_                                                               | 订单已成交数量                                   |
| frozen_price       | _float_                                                             | 冻结价格                                         |
| init_frozen_cash   | _float_                                                             | 冻结资金                                         |
| message            | _str_                                                               | 信息。比如拒单时候此处会提示拒单原因             |
| order_book_id      | _str_                                                               | 合约代码                                         |
| order_id           | _int_                                                               | 唯一标识订单的 id                                |
| position_effect    | _[POSITION_EFFECT](./enums#rqalpha-plus-api-enums-position-effect)_ | 订单开平（期货专用）                             |
| price              | _float_                                                             | 订单价格，只有在订单类型为'限价单'的时候才有意义 |
| quantity           | _int_                                                               | 订单数量                                         |
| secondary_order_id | _str_                                                               | 实盘交易中交易所产生的订单 ID                    |
| side               | _[SIDE](./enums#rqalpha-plus-api-enums-side)_                       | 订单方向                                         |
| status             | _[ORDER_STATUS](./enums#rqalpha-plus-api-enums-order-status)_       | 订单状态                                         |
| style              | _ORDER_STYLE_                                                       | 订单类型                                         |
| trading_datetime   | _datetime.datetime_                                                 | 订单的交易日期（对应期货夜盘）                   |
| transaction_cost   | _float_                                                             | 费用                                             |
| type               | _[ORDER_TYPE](./enums#rqalpha-plus-api-enums-order-type)_           | 订单类型                                         |
| unfilled_quantity  | _int_                                                               | 订单未成交数量                                   |

### Portfolio - 投资组合 {#rqalpha-plus-api-types-portfolio}

```python
class rqalpha.portfolio.Portfolio(starting_cash, init_positions, financing_rate, start_date, data_proxy, event_bus)
```

Bases: object

投资组合，策略所有账户的集合

| 属性                  | 类型                                                                     | 说明                                                             |
| --------------------- | ------------------------------------------------------------------------ | ---------------------------------------------------------------- |
| accounts              | _Dict[DEFAULT_ACCOUNT_TYPE, [Account](#rqalpha-plus-api-types-account)]_ | 账户字典                                                         |
| annualized_returns    | _float_                                                                  | 累计年化收益率                                                   |
| cash                  | _float_                                                                  | 可用资金                                                         |
| cash_liabilities      | _float_                                                                  | 现金负债                                                         |
| daily_pnl             | _float_                                                                  | 当日盈亏                                                         |
| daily_returns         | _float_                                                                  | 当前最新一天的日收益                                             |
| deposit_withdraw      | _method_                                                                 | 出入金，deposit_withdraw(account_type, amount, receiving_days=0) |
| finance_repay         | _method_                                                                 | 融资还款，finance_repay(amount, account_type)                    |
| frozen_cash           | _float_                                                                  | 冻结资金                                                         |
| future_account        | _FutureAccount_                                                          | 期货账户                                                         |
| market_value          | _float_                                                                  | 市值                                                             |
| pnl                   | _float_                                                                  | 收益                                                             |
| portfolio_value       | _Deprecated_                                                             | 总权益                                                           |
| positions             | _dict_                                                                   | 持仓字典                                                         |
| start_date            | _datetime.datetime_                                                      | 策略投资组合的开始日期                                           |
| starting_cash         | _float_                                                                  | 初始资金                                                         |
| static_unit_net_value | _float_                                                                  | 昨日净值                                                         |
| stock_account         | _StockAccount_                                                           | 股票账户                                                         |
| total_returns         | _float_                                                                  | 累计收益率                                                       |
| total_value           | _float_                                                                  | 总权益                                                           |
| transaction_cost      | _float_                                                                  | 交易成本（税费）                                                 |
| unit_net_value        | _float_                                                                  | 实时净值                                                         |
| units                 | _float_                                                                  | 份额                                                             |

### Account - 账户 {#rqalpha-plus-api-types-account}

```python
class rqalpha.portfolio.account.Account(account_type, total_cash, init_positions, financing_rate)
```

账户，多种持仓和现金的集合。

不同品种的合约持仓可能归属于不同的账户，如股票、转债、场内基金、ETF 期权归属于股票账户，期货、期货期权归属于期货账户

| 属性                               | 类型                 | 说明                                                                                                                                                                                                                                                                                                                        |
| ---------------------------------- | -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| buy_margin                         | _float_              | 多方向保证金                                                                                                                                                                                                                                                                                                                |
| cash                               | _float_              | 可用资金                                                                                                                                                                                                                                                                                                                    |
| cash_liabilities                   | _float_              | 现金负债                                                                                                                                                                                                                                                                                                                    |
| cash_liabilities_interest          | _float_              | 现金负债当日的利息                                                                                                                                                                                                                                                                                                          |
| daily_pnl                          | _float_              | 当日盈亏                                                                                                                                                                                                                                                                                                                    |
| deposit_withdraw                   | _method_             | 出入金，deposit_withdraw(account_type, amount, receiving_days=0)                                                                                                                                                                                                                                                            |
| finance_repay                      | _method_             | 融资还款 ，finance_repay(amount)                                                                                                                                                                                                                                                                                            |
| frozen_cash                        | _float_              | 冻结资金                                                                                                                                                                                                                                                                                                                    |
| get_position                       | _Position_           | 获取某个标的的持仓对象， <br/>get_position(order_book_id, direction=POSITION_DIRECTION.LONG) <div>&nbsp;&nbsp;&nbsp;&nbsp;order_book_id (str) -- 标的编号 </div><div>&nbsp;&nbsp;&nbsp;&nbsp;direction ([POSITION_DIRECTION](./enums#rqalpha-plus-api-enums-position-direction)) -- 持仓方向</div>                          |
| get_positions                      | _Iterable[Position]_ | 获取所有持仓对象列表                                                                                                                                                                                                                                                                                                        |
| management_fees                    | _float_              | 该账户的管理费用总计                                                                                                                                                                                                                                                                                                        |
| market_value                       | _float_              | 市值                                                                                                                                                                                                                                                                                                                        |
| position_equity                    | _float_              | 持仓总权益                                                                                                                                                                                                                                                                                                                  |
| position_pnl                       | _float_              | 昨仓盈亏                                                                                                                                                                                                                                                                                                                    |
| register_management_fee_calculator | _None_               | 设置管理费用计算逻辑，该方法需要传入一个函数，<br/>def management_fee_calculator(account, rate): <div>&nbsp;&nbsp;&nbsp;&nbsp;return len(account.positions) \* rate</div>def init(context): <div>&nbsp;&nbsp;&nbsp;&nbsp;context.portfolio.accounts["STOCK"].set_management_fee_calculator(management_fee_calculator)</div> |
| sell_margin                        | _float_              | 空方向保证金                                                                                                                                                                                                                                                                                                                |
| set_management_fee_rate            | _None_               | 管理费用计算费率，set_management_fee_rate(rate)                                                                                                                                                                                                                                                                             |
| total_cash                         | _float_              | 账户总资金                                                                                                                                                                                                                                                                                                                  |
| total_value                        | _float_              | 账户总权益                                                                                                                                                                                                                                                                                                                  |
| trading_pnl                        | _float_              | 交易盈亏                                                                                                                                                                                                                                                                                                                    |
| transaction_cost                   | _float_              | 总费用                                                                                                                                                                                                                                                                                                                      |

### StockPosition - 股票持仓 {#rqalpha-plus-api-types-stock-position}

```python
class rqalpha.mod.rqalpha_mod_sys_accounts.position_model.StockPosition(order_book_id, direction, init_quantity=0, init_price=None)
```

| 属性                | 类型                                                                      | 说明                         |
| ------------------- | ------------------------------------------------------------------------- | ---------------------------- |
| avg_price           | _float_                                                                   | 开仓均价                     |
| closable            | _int_                                                                     | 可平仓位                     |
| direction           | _[POSITION_DIRECTION](./enums#rqalpha-plus-api-enums-position-direction)_ | 返回当前持仓的方向           |
| dividend_receivable | _float_                                                                   | 应收分红                     |
| last_price          | _float_                                                                   | 当前最新价                   |
| market_value        | _float_                                                                   | 返回当前持仓的市值           |
| order_book_id       | _str_                                                                     | 返回当前持仓的 order_book_id |
| pnl                 | _float_                                                                   | 返回该持仓的累积盈亏         |
| position_pnl        | _float_                                                                   | 返回当前持仓当日的持仓盈亏   |
| prev_close          | _float_                                                                   | 昨日收盘价                   |
| quantity            | _int_                                                                     | 返回当前持仓量               |
| today_closable      | _int_                                                                     | 返回今仓中的可平仓位         |
| trading_pnl         | _float_                                                                   | 返回当前持仓当日的交易盈亏   |

### FuturePosition - 期货持仓 {#rqalpha-plus-api-types-future-position}

```python
class rqalpha.mod.rqalpha_mod_sys_accounts.position_model.FuturePosition(order_book_id, direction, init_quantity=0, init_price=None)
```

| 属性           | 类型                                                                      | 说明                                              |
| -------------- | ------------------------------------------------------------------------- | ------------------------------------------------- |
| avg_price      | _float_                                                                   | 开仓均价                                          |
| closable       | _int_                                                                     | 可平仓位                                          |
| direction      | _[POSITION_DIRECTION](./enums#rqalpha-plus-api-enums-position-direction)_ | 返回当前持仓的方向                                |
| last_price     | _float_                                                                   | 当前最新价                                        |
| margin         | _float_                                                                   | 保证金 = 持仓量 \* 最新价 \* 合约乘数 \* 保证金率 |
| market_value   | _float_                                                                   | 返回当前持仓的市值                                |
| order_book_id  | _str_                                                                     | 返回当前持仓的 order_book_id                      |
| pnl            | _float_                                                                   | 返回该持仓的累积盈亏                              |
| position_pnl   | _float_                                                                   | 返回当前持仓当日的持仓盈亏                        |
| prev_close     | _float_                                                                   | 昨日收盘价                                        |
| quantity       | _int_                                                                     | 返回当前持仓量                                    |
| today_closable | _int_                                                                     | 返回今仓中的可平仓位                              |
| trading_pnl    | _float_                                                                   | 返回当前持仓当日的交易盈亏                        |

### FundPosition - 基金持仓 {#rqalpha-plus-api-types-fund-position}

```python
class rqalpha_mod_fund.position.FundPosition
```

| 属性                | 类型                                                                      | 说明                         |
| ------------------- | ------------------------------------------------------------------------- | ---------------------------- |
| avg_price           | _float_                                                                   | 开仓均价                     |
| closable            | _int_                                                                     | 可平仓位                     |
| close_queue         | _list_                                                                    | 平仓时需要按队列平仓         |
| direction           | _[POSITION_DIRECTION](./enums#rqalpha-plus-api-enums-position-direction)_ | 返回当前持仓的方向           |
| dividend_receivable | _float_                                                                   | 应收分红                     |
| equity              | _float_                                                                   | 净值                         |
| last_price          | _float_                                                                   | 当前最新价                   |
| market_value        | _float_                                                                   | 返回当前持仓的市值           |
| order_book_id       | _str_                                                                     | 返回当前持仓的 order_book_id |
| pnl                 | _float_                                                                   | 返回该持仓的累积盈亏         |
| position_pnl        | _float_                                                                   | 返回当前持仓当日的持仓盈亏   |
| prev_close          | _float_                                                                   | 昨日收盘价                   |
| quantity            | _int_                                                                     | 已到账份额                   |
| receivable_cash     | _float_                                                                   | 未到账金额                   |
| receivable_quantity | _int_                                                                     | 未到账份额                   |
| today_closable      | _int_                                                                     | 返回今仓中的可平仓位         |
| trading_pnl         | _float_                                                                   | 返回当前持仓当日的交易盈亏   |

### Instrument - 交易标的 {#rqalpha-plus-api-types-instrument}

```python
class rqalpha.model.instrument.Instrument
```

| 属性                     | 类型    | 说明                                                                                                                                                                                                                                                                                                 |
| ------------------------ | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| order_book_id            | _str_   | 股票：证券代码，证券的独特的标识符。应以'.XSHG'或'.XSHE'结尾，前者代表上证，后者代表深证。期货：期货代码，期货的独特的标识符（郑商所期货合约数字部分进行了补齐。例如原有代码'ZC609'补齐之后变为'ZC1609'）。主力连续合约 UnderlyingSymbol+88，例如'IF88' ；指数连续合约命名规则为 UnderlyingSymbol+99 |
| symbol                   | _str_   | 股票：证券的简称，例如'平安银行'。期货：期货的简称，例如'沪深 1005'。                                                                                                                                                                                                                                |
| abbrev_symbol            | _str_   | 证券的名称缩写，在中国 A 股就是股票的拼音缩写，例如：'PAYH'就是平安银行股票的证券名缩写；在期货市场中例如'HS1005'，主力连续合约与指数连续合约都为'null'。                                                                                                                                            |
| round_lot                | _int_   | 股票：一手对应多少股，中国 A 股一手是 100 股。期货：一律为 1。                                                                                                                                                                                                                                       |
| sector_code              | _str_   | 板块缩写代码，全球通用标准定义（股票专用）                                                                                                                                                                                                                                                           |
| sector_code_name         | _str_   | 以当地语言为标准的板块代码名（股票专用）                                                                                                                                                                                                                                                             |
| industry_code            | _str_   | 国民经济行业分类代码，具体可参考下方“Industry 列表”（股票专用）                                                                                                                                                                                                                                      |
| industry_name            | _str_   | 国民经济行业分类名称（股票专用）                                                                                                                                                                                                                                                                     |
| listed_date              | _str_   | 股票：该证券上市日期。期货：期货的上市日期，主力连续合约与指数连续合约都为'0000-00-00'。                                                                                                                                                                                                             |
| de_listed_date           | _str_   | 股票：退市日期；期货：交割日期                                                                                                                                                                                                                                                                       |
| type                     | _str_   | 合约类型，目前支持的类型有:'CS','INDX','LOF','ETF','Future','FUND'等                                                                                                                                                                                                                                 |
| concept_names            | _str_   | 概念股分类，如'铁路基建','基金重仓'等（股票专用）                                                                                                                                                                                                                                                    |
| exchange                 | _str_   | 交易所。股票：'XSHE' - 深交所, 'XSHG' - 上交所。期货：'DCE' - 大连商品交易所, 'SHFE' - 上海期货交易所，'CFFEX' - 中国金融期货交易所, 'CZCE'- 郑州商品交易所                                                                                                                                          |
| board_type               | _str_   | 板块类别，'MainBoard'-主板,'GEM'-创业板（股票专用）                                                                                                                                                                                                                                                  |
| status                   | _str_   | 合约状态，合约状态。'Active' - 正常上市, 'Delisted' - 终止上市, 'TemporarySuspended' - 暂停上市, 'PreIPO' - 发行配售期间, 'FailIPO' - 发行失败（股票专用）                                                                                                                                           |
| special_type             | _str_   | 特别处理状态，特别处理状态。'Normal' - 正常上市, 'ST' - ST 处理, 'StarST' - \*ST 代表该股票正在接受退市警告, 'PT' - 代表该股票连续 3 年收入为负，将被暂停交易, 'Other' - 其他（股票专用）                                                                                                            |
| contract_multiplier      | _float_ | 合约乘数，如沪深 300 股指期货的乘数为 300.0（期货专用）                                                                                                                                                                                                                                              |
| underlying_order_book_id | _str_   | 合约标的代码，目前除股指期货(IH, IF, IC)之外的期货合约，这一字段全部为'null'（期货专用）                                                                                                                                                                                                             |
| underlying_symbol        | _str_   | 合约标的名称，例如 IF1005 的合约标的名称为 'IF'（期货专用）                                                                                                                                                                                                                                          |
| maturity_date            | _str_   | 期货到期日，主力连续合约与指数连续合约都为'0000-00-00'（期货专用）                                                                                                                                                                                                                                   |
| settlement_method        | _str_   | 交割方式，'CashSettlementRequired'-现金交割,'PhysicalSettlementRequired'-实物交割（期货专用）                                                                                                                                                                                                        |
| product                  | _str_   | 产品类型，'Index'-股指期货,'Commodity'-商品期货,'Government'-国债期货（期货专用）                                                                                                                                                                                                                    |

#### Instrument 对象也支持如下方法： {#rqalpha-plus-api-types-instrument-methods}

合约已上市天数：

```python
instruments(order_book_id).days_from_listed()
```

如果合约首次上市交易，天数为 0；如果合约尚未上市或已经退市，则天数值为-1

合约距离到期天数：

```python
instruments(order_book_id).days_to_expire()
```

如果策略已经退市，则天数值为-1

最小价格变动单位：

```python
instruments(order_book_id).tick_size()
```

例如，instruments('IF1608').tick_size()获取的就是股指期货的最小价格变动单位，为 0.2，即“一跳”的水平。
