# 其他接口 {#rqalpha-plus-api-other}

## 其他接口 {#rqalpha-plus-api-other-general}

### update_universe - 更新合约池 {#rqalpha-plus-api-other-update-universe}

```python
rqalpha.api.update_universe(id_or_symbols)
```

该方法用于更新现在关注的证券的集合（e.g.：股票池）。PS：会在下一个 bar 事件触发时候产生（新的关注的股票池更新）效果。并且 update_universe 会是覆盖（overwrite）的操作而不是在已有的股票池的基础上进行增量添加。比如已有的股票池为['000001.XSHE', '000024.XSHE']然后调用了 update_universe(['000030.XSHE'])之后，股票池就会变成 000030.XSHE 一个股票了，随后的数据更新也只会跟踪 000030.XSHE 这一个股票了。

#### 参数 {#rqalpha-plus-api-other-update-universe-params}

| 参数名        | 类型                                                                                                                                                    | 说明   |
|-----|-----|-----|
| id_or_symbols | _Union[str, [Instrument](./types#rqalpha-plus-api-types-instrument), Iterable[str], Iterable[[Instrument](./types#rqalpha-plus-api-types-instrument)]]_ | 标的物 |

#### 返回 {#rqalpha-plus-api-other-update-universe-return}

_None_

#### 范例 {#rqalpha-plus-api-other-update-universe-example}

- 下面的代码是将股票池变更为只有 2 个股票 000001.XSHE 和 000024.XSHE:

```python
update_universe(['000001.XSHE', '000024.XSHE'])
```

- 当然，您也可以使用合约简称：

```python
update_universe(['平安银行', '招商地产'])
```

### subscribe - 订阅合约 {#rqalpha-plus-api-other-subscribe}

```python
rqalpha.api.subscribe(id_or_symbols)
```

订阅合约行情。

在日级别回测中不需要订阅合约。

在分钟回测中，若策略只设置了股票账户则不需要订阅合约；若设置了期货账户，则需要订阅策略关注的期货合约，框架会根据订阅的期货合约品种触发对应交易时间的 handle_bar。为了方便起见，也可以以直接订阅主力连续合约。

在 tick 回测中，策略需要订阅每一个关注的股票/期货合约，框架会根据订阅池触发对应标的的 handle_tick。

#### 参数

| 参数名        | 类型                                                                                                                                                    | 说明   |
|-----|-----|-----|
| id_or_symbols | _Union[str, [Instrument](./types#rqalpha-plus-api-types-instrument), Iterable[str], Iterable[[Instrument](./types#rqalpha-plus-api-types-instrument)]]_ | 标的物 |

#### 返回

_None_

### unsubscribe - 取消订阅合约 {#rqalpha-plus-api-other-unsubscribe}

```python
rqalpha.api.unsubscribe(id_or_symbols)
```

取消订阅合约行情。取消订阅会导致合约池内合约的减少，如果当前合约池中没有任何合约，则策略直接退出。

#### 参数

| 参数名        | 类型                                                                                                                                                    | 说明   |
|-----|-----|-----|
| id_or_symbols | _Union[str, [Instrument](./types#rqalpha-plus-api-types-instrument), Iterable[str], Iterable[[Instrument](./types#rqalpha-plus-api-types-instrument)]]_ | 标的物 |

#### 返回

_None_

### subscribe_event - 订阅事件 {#rqalpha-plus-api-other-subscribe-event}

```python
rqalpha.api.subscribe_event(event_type, handler)
```

订阅框架内部事件，注册事件处理函数

#### 参数

| 参数名     | 类型                                                                                  | 说明     |
|-----|-----|-----|
| event_type | _EVENT_                                                                               | 事件类型 |
| handler    | _Callable[[ [StrategyContext](./types#rqalpha-plus-api-types-context), Event], None]_ | 处理函数 |

#### 返回

_None_

#### 范例

精确控制订单生命周期。您可以使用 RQAlpha 策略框架提供的事件订阅机制来控制订单生命周期, 例如成交发生、订单被撤销等。可以在策略初始化时通过 subscribe_event 这一 API 从 支持的事件列表 中选择对应的事件进行订阅并注册回调函数。这样, 当事件发生的时候, 对应回调函数会被触发。

下面的例子展示了回调函数的注册机制, 当订单创建成功以及成交发生的时候, 对应的回调函数将会分别被触发。

```python
def init(context):
    # 注册成交事件
    subscribe_event(EVENT.TRADE, on_trade)
    # 注册订单成功创建事件
    subscribe_event(EVENT.ORDER_CREATION_PASS, on_order_created)
    context.count = 0
    context.s1 = '000001.XSHE'

# 回调函数定义中需要包含 context, event 参数
def on_trade(context, event):
    # 获取成交信息
    trade = event.trade
    if trade.order_book_id == context.s1:
     print(trade)

# 回调函数定义中需要包含 event 这一参数
def on_order_created(context, event):
    # 获取订单信息
    order = event.order
    print(order)

def handle_bar(context, bar_dict):
    px = bar_dict['000001.XSHE'].last + 0.2
    if context.count == 0:
        # 订单创建, 并使用关键字 context 保存全局变量
        submit_order(context.s1, amount=100, side=SIDE.BUY, price=px)
        context.count += 1
```

### plot - 画图 {#rqalpha-plus-api-other-plot}

```python
rqalpha.api.plot(series_name, value)
```

在策略运行结束后的收益图中，加入自定义的曲线。 每次调用 plot 函数将会以当前时间为横坐标，value 为纵坐标加入一个点，series_name 相同的点将连成一条曲线。

#### 参数

| 参数名      | 类型     | 说明         |
|-----|-----|-----|
| series_name | _str_    | 曲线名称     |
| value       | _number_ | 点的纵坐标值 |

#### 返回

_None_

#### 范例

```python
def handle_bar(context, bar_dict):
    plot("OPEN", bar_dict["000001.XSHE"].open)
```

## 技术分析 {#rqalpha-plus-api-other-technical}

### reg_indicator - 注册指标 {#rqalpha-plus-api-other-reg-indicator}

```python
reg_indicator(name, factor, freq='1d', win_size=10)
```

将函数注册为技术指标，注册后可以通过调用 [get_indicator()](#rqalpha-plus-api-other-get-indicator) 获取技术指标计算结果。

#### 参数

| 参数名   | 类型                      | 说明                                                                                             |
|-----|-----|-----|
| name     | _str_                     | 指标名称                                                                                         |
| factor   | _Union[Callable, Factor]_ | 指标函数对象                                                                                     |
| freq     | _str_                     | 指标的计算周期，支持日级别与分钟级别，'1d'代表每日，'5m'代表 5 分钟                              |
| win_size | _int_                     | 获取数据回溯窗口。该指标用于在注册指标时让系统获取回溯获取数据的最大窗口，便于数据的加载与预计算 |

#### 返回

_None_

#### 范例

```python
# 定义指标函数体本身
def KDJ_SIGNAL():
    # 连续两个周期J值一直在超买区
    K, D, J = KDJ()
    return EVERY(J > 80, 2)

# 注册技术指标
reg_indicator('kdj', KDJ_SIGNAL, '1d', win_size=20)
```

### get_indicator - 获取指标 {#rqalpha-plus-api-other-get-indicator}

```python
get_indicator(self, order_book_id, name)
```

获取技术指标的计算结果

#### 参数

| 参数名        | 类型  | 说明     |
|-----|-----|-----|
| order_book_id | _str_ | 标的代码 |
| name          | _str_ | 指标名称 |

#### 返回

定义指标返回值

#### 范例

```python
# 定义指标函数体本身
def KDJ_SIGNAL():
    # 连续两个周期J值一直在超买区
    K, D, J = KDJ()
    return EVERY(J > 80, 2)

# 注册技术指标
reg_indicator('kdj', KDJ_SIGNAL, '1d', win_size=20)

# 获取指标计算结果
get_indicator('000001.XSHE', 'kdj')
```

## 股票投资优化器 {#rqalpha-plus-api-other-optimizer}

### portfolio_optimize - 组合优化 {#rqalpha-plus-api-other-portfolio-optimize}

```python
rqalpha_mod_optimizer2.api.portfolio_optimize(order_book_ids, objective=<rqoptimizer.objective.MinVariance object>, bnds=None, cons=None, benchmark=None, cov_model=<CovModel.FACTOR_MODEL_DAILY: 'factor_model/daily'>, factor_risk_aversion=1.0, specific_risk_aversion=1.0)
```

组合优化，根据给定的约束及目标函数计算最优组合权重。

#### 参数

| 参数名                 | 类型                       | 说明                                                                                                                                                                                                                                                                                                                         |
|-----|-----|-----|
| order_book_ids         | _str_                      | 候选合约                                                                                                                                                                                                                                                                                                                     |
| objective              | _OptimizationObjective_    | 目标函数，默认为 MinVariance（风险最小化）。支持的目标函数见下表                                                                                                                                                                                                                                                             |
| bnds                   | _Dict_                     | {order_book_id \| "_": (lower_limit, upper_limit)} 个股权重上下界字典，key 为 order_book_id，value 为(lower_limit, upper_limit)组成的 tuple。lower_limit/upper_limit 取值可以是[0, 1]的数或 None。当取值为 None 时，表示对应的界不做限制。当 key 为'_'时，表示所有未在此字典中明确指定的其他合约。所有合约默认上下界为[0, 1] |
| cons                   | _OptimizationConstraint_   | 约束列表。支持的约束类型见下表                                                                                                                                                                                                                                                                                               |
| benchmark              | _str or OptimizeBenchmark_ | 基准，目前仅支持指数基准                                                                                                                                                                                                                                                                                                     |
| cov_model              | _str_                      | 协方差模型，支持 daily/monthly/quarterly                                                                                                                                                                                                                                                                                     |
| factor_risk_aversion   | _float_                    | 因子风险厌恶系数，默认为 1                                                                                                                                                                                                                                                                                                   |
| specific_risk_aversion | _float_                    | 特异风险厌恶系数，默认为 1                                                                                                                                                                                                                                                                                                   |

##### objective 支持的目标函数： {#rqalpha-plus-api-other-objective-functions}

| 目标函数            | 说明                         |
|-----|-----|
| MinVariance         | 风险最小化                   |
| MeanVariance        | 均值（收益）方差（风险）模型 |
| RiskParity          | 风险平价                     |
| MinTrackingError    | 最小追踪误差                 |
| MaxInformationRatio | 最大信息比率                 |
| MaxSharpeRatio      | 最大夏普率                   |
| MaxIndicator        | 指标值最大化                 |
| MinStyleDeviation   | 风格偏离最小化               |

##### cons 支持的约束类型： {#rqalpha-plus-api-other-constraints}

| 约束类型                      | 说明                                                                           |
|-----|-----|
| TrackingErrorLimit            | 跟踪误差约束                                                                   |
| TurnoverLimit                 | 换手率约束                                                                     |
| BenchmarkComponentWeightLimit | 成分股权重约束，即要求优化结果中，基准成分股的权重之和的下限                   |
| IndustryConstraint            | 行业权重约束，默认行业分类为申万一级。可选中信一级及申万一级(拆分非银金融行业) |
| WildcardIndustryConstraint    |                                                                                |
| StyleConstraint               | 风格约束                                                                       |
| WildcardStyleConstraint       |                                                                                |

#### 返回

_pd.Series 组合最优化权重_

## scheduler 定时器 {#rqalpha-plus-api-other-scheduler}

### scheduler.run_daily - 每天运行 {#rqalpha-plus-api-other-scheduler-run-daily}

```python
scheduler.run_daily(function)
```

每日运行一次指定的函数，只能在 init 内使用。

::: tip 注意，schedule 一定在其对应时间点的 handle_bar 之后执行。
:::

#### 参数

| 参数名   | 类型   | 说明                                                                                                    |
|-----|-----|-----|
| function | _func_ | 使传入的 function 每日运行。注意，function 函数一定要包含（并且只能包含）context, bar_dict 两个输入参数 |

#### 返回

_None_

#### 范例

- 以下的范例代码片段是一个非常简单的例子，在每天交易后查询现在 portfolio 中剩下的 cash 的情况:

```python
#scheduler调用的函数需要包括context, bar_dict两个输入参数
def log_cash(context, bar_dict):
    logger.info("Remaning cash: %r" % context.portfolio.cash)

def init(context):
    #...
    # 每天运行一次
    scheduler.run_daily(log_cash)
```

### scheduler.run_weekly - 每周运行 {#rqalpha-plus-api-other-scheduler-run-weekly}

```python
scheduler.run_weekly(function, weekday=x, tradingday=t)
```

每周运行一次指定的函数，只能在 init 内使用。

::: tip 注意:

- tradingday 中的负数表示倒数。
- tradingday 表示交易日。如某周只有四个交易日，则此周的 tradingday=4 与 tradingday=-1 表示同一天。
- weekday 和 tradingday 不能同时使用。

:::

#### 参数

| 参数名     | 类型   | 说明                                                                                                              |
|-----|-----|-----|
| function   | _func_ | 使传入的 function 每日交易开始前运行。注意，function 函数一定要包含（并且只能包含）context, bar_dict 两个输入参数 |
| weekday    | _int_  | 1~5 分别代表周一至周五，用户必须指定                                                                              |
| tradingday | _int_  | 范围为[-5,1],[1,5] 例如，1 代表每周第一个交易日，-1 代表每周倒数第一个交易日，用户可以不填写                      |

#### 返回

_None_

#### 范例

- 以下的代码片段非常简单，在每周二固定运行打印一下现在的 portfolio 剩余的资金:

```python
#scheduler调用的函数需要包括context, bar_dict两个参数
def log_cash(context, bar_dict):
    logger.info("Remaning cash: %r" % context.portfolio.cash)

def init(context):
    #...
    # 每周二打印一下剩余资金：
    scheduler.run_weekly(log_cash, weekday=2)
    # 每周第二个交易日打印剩余资金：
    #scheduler.run_weekly(log_cash, tradingday=2)
```

### scheduler.run_monthly - 每月运行 {#rqalpha-plus-api-other-scheduler-run-monthly}

```python
scheduler.run_monthly(function, tradingday=t)
```

每月运行一次指定的函数，只能在 init 内使用。

::: tip 注意:

- tradingday 的负数表示倒数。
- tradingday 表示交易日，如某月只有三个交易日，则此月的 tradingday=3 与 tradingday=-1 表示同一。
  :::

#### 参数

| 参数名     | 类型   | 说明                                                                                                              |
|-----|-----|-----|
| function   | _func_ | 使传入的 function 每日交易开始前运行。注意，function 函数一定要包含（并且只能包含）context, bar_dict 两个输入参数 |
| tradingday | _int_  | 范围为[-23,1], [1,23] ，例如，1 代表每月第一个交易日，-1 代表每月倒数第一个交易日，用户必须指定。                 |

#### 返回

_None_

#### 范例

- 以下的代码片段非常简单的展示了每个月第一个交易日的时候我们进行一次财务数据查询，这对根据财务数据来调节股票组合的策略会非常有用:

```python
#scheduler调用的函数需要包括context, bar_dict两个参数
def query_fundamental(context, bar_dict):
        # 查询revenue前十名的公司的股票并且他们的pe_ratio在25和30之间。打fundamentals的时候会有auto-complete方便写查询代码。
    fundamental_df = get_fundamentals(
        query(
            fundamentals.income_statement.revenue, fundamentals.eod_derivative_indicator.pe_ratio
        ).filter(
            fundamentals.eod_derivative_indicator.pe_ratio > 25
        ).filter(
            fundamentals.eod_derivative_indicator.pe_ratio < 30
        ).order_by(
            fundamentals.income_statement.revenue.desc()
        ).limit(
            10
        )
    )

    # 将查询结果dataframe的fundamental_df存放在context里面以备后面只需：
    context.fundamental_df = fundamental_df

    # 实时打印日志看下查询结果，会有我们精心处理的数据表格显示：
    logger.info(context.fundamental_df)
    update_universe(context.fundamental_df.columns.values)

 # 在这个方法中编写任何的初始化逻辑。context对象将会在你的算法策略的任何方法之间做传递。
def init(context):
    # 每月的第一个交易日查询以下财务数据，以确保可以拿到最新更新的财务数据信息用来调整仓位
    scheduler.run_monthly(query_fundamental, tradingday=1)
```

### time_rule - 定时间运行 {#rqalpha-plus-api-other-time-rule}

scheduler 还可以用来做定时间运行，比如在每天开盘后的一小时后或一分钟后定时运行，这里有很多种组合可以让您达到各种自己想要达到的定时运行的目的。

使用的方法是和上面的 scheduler.run_daily() , scheduler.run_weekly() 和 scheduler.run_monthly() 进行组合加入 time_rule 来一起使用。

::: tip 注意:

- market_open 与 market_close 都跟随中国 A 股交易时间进行设置，即 09:31~15:00。

- physical_time 用于设置物理时间，与 market_open 和 market_close 的相对时间不同。

- physical_time 更多用于交易时间不确定的品种，如商品期货。

- 使用 time_rule 定时运行会在分钟级别回测和实时模拟交易中有定义的效果，在日回测中只会默认依然在该天运行，并不能在固定的时间运行。

- 在分钟回测中如未指定 time_rule,则默认在开盘后一分钟运行,即 09:31 分。

- 目前暂不支持开盘交易(即 09:30 分交易)。

- market_open(minute=120)将在 11:30 执行， market_open(minute=121)在 13:01 执行，中午休市的区间会被忽略。

- time_rule='before_trading'表示在开市交易前运行 scheduler 函数。该函数运行时间将在 before_trading 函数运行完毕之后 handle_bar 运行之前。
  :::

`time_rule`: 定时具体几点几分运行某个函数。time_rule='before_trading' 表示开始交易前运行；market_open(hour=x, minute=y)表示 A 股市场开市后 x 小时 y 分钟运行，market_close(hour=x, minute=y)表示 A 股市场收市前 x 小时 y 分钟运行。如果不设置 time_rule 默认的值是中国 A 股市场开市后一分钟运行。

#### 参数

market_open, market_close, physical_time 参数如下：

| 参数   | 类型                 | 注释                                                                                                                                             |
|-----|-----|-----|
| hour   | int - option [1,4]   | 具体在 market_open/market_close 后/前第多少小时执行, 股票的交易时间为[9:31 - 11:30],[13:01 - 15:00]共 240 分钟，所以 hour 的范围为 [1,4]         |
| minute | int - option [1,240] | 具体在 market_open/market_close 的后/前第多少分钟执行,同上，股票每天交易时间 240 分钟，所以 minute 的范围为 [1,240],中午休市的时间区间会被忽略。 |

#### 返回

_None_

#### 范例

- 每天的开市后 10 分钟运行:

```python
scheduler.run_daily(function, time_rule=market_open(minute=10))
```

- 每周的第 t 个交易日闭市前 1 小时运行:

```python
scheduler.run_weekly(function, tradingday=t, time_rule=market_close(hour=1))
```

- 每月的第 t 个交易日开市后 1 小时运行:

```python
scheduler.run_monthly(function, tradingday=t, time_rule=market_open(hour=1))
```

- 每天开始交易前运行:

```python
scheduler.run_daily(function, time_rule='before_trading')
```

- 每天十点运行

```python
scheduler.run_daily(function, time_rule=physical_time(hour=10, minute=0))
```
