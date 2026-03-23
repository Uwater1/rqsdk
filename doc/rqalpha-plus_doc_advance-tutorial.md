# 进阶教程 {#rqalpha-plus-advanced-tutorial}

## 账户和持仓 {#rqalpha-plus-account-position}

RQAlphaPlus 内部维护了多层级的账户和持仓结构，可以简化成如下的树形结构：

```
Portfolio()                                     # 投资组合
│
└─── Account("STOCK")                           # 股票账户
│       │
│       └─── Position("000001.XSHE")            # 平安银行持仓
│       │
│       └─── Position("90000003", "SHORT")      # 300ETF购1月3900义务方持仓
│       │
│       └─── Position("128032.XSHE")            # 双环转债持仓
│       │
│       └─── Position("AU9999.SGEX", "LONG")    # 上金所Au99.99黄金现货合约多头持仓
│       |
│       └─── Position("004241")                 # 中欧时代先锋股票C持仓
│
└─── Account("FUTURE")                          # 期货账户
        │
        └─── Position("RB2010", "LONG")         # 螺纹钢2010多头持仓
        │
        └─── Position("RB2010", "SHORT")        # 螺纹钢2010空头持仓
        │
        └─── Position("IO2004C4150", "LONG")    # 300INDEX2004购4150权利方持仓


```

- portfolio：投资组合，对应上图中最顶层的结构，表示当前策略中所有投资标的和剩余现金的总和。

  - 通过 `context.portfolio` 可以访问当前策略的 [Portfolio 对象](../api/types#rqalpha-plus-api-types-portfolio)。
  - [Portfolio 对象](../api/types#rqalpha-plus-api-types-portfolio) 具有 `portfolio_value`（总权益）、`unit_net_value`（净值）、`daily_pnl`（当日盈亏）、`daily_returns`（日收益率）等属性，如：
    ```python
    # 获取当前策略总权益
    context.portfolio.portfolio_value
    ```

- account: 账户，对应上图中的第二层结构，RQAlphaPlus 最多支持股票（STOCK）、期货（FUTURE）两种账户。

  - 运行策略需要为每个账户配置初始资金：
    - 命令行运行时，通过 `-a stock 100000 -a future 100000` 配置出初始资金
    - 函数入口运行时，通过如下配置设置初始资金：
      ```python
      {"base: {"accounts": {
          "STOCK": 100000,
          "FUTURE": 100000,
      }}}
      ```
    - 策略中可通过 `context.portfolio.accounts` 访问账户字典，通过 `context.portfolio.accounts["STOCK"]` 访问单个 [Account 对象](../api/types#rqalpha-plus-api-types-account)
    - [Account 对象](../api/types#rqalpha-plus-api-types-account) 具有 `cash`（可用资金）、`market_value`（持仓市值）、`total_value`（账户权益）等属性

- position：持仓，对应上图的底层结构，表示策略所持有的每一只金融标的的仓位。
  - 持有的每个标的都有自己的 [Position 对象](../api/types.md)，具有多空头的标的（期货、期权等）有多空两方向两个[Position 对象](../api/types.md)。
  - 可以通过 `get_position` 和 `get_positions` 两个接口获取持仓对象
    - get_position 接收标的代码、方向（可选）两个参数，方向参数默认为多头，返回对应的 [Position 对象](../api/types.md)，如：
      ```python
      get_position("000001.XSHE")
      get_position("004241")
      get_position("RB2010", "SHORT")
      ```
    - get_positions 无参数，返回包含所有 [Position 对象](../api/types.md)的**列表**，如：
      ```python
      get_positions()
      ```
  - 通过 `context.portfolio.positions` 或 `account.positions` 访问持仓的方式在未来的版本中或被弃用，如无必要 <em><strong>请勿</strong></em> 使用。

## 回测频率 {#rqalpha-plus-frequency}

RQAlphaPlus 支持日、分钟、tick 三种频率级别的回测。

三种频率的回测会在相同的时机触发盘外约定函数 `init`、`before_trading`、`after_trading` 和集合竞价约定函数 `open_auction`，而盘中约定函数 `handle_bar` 和 `handle_tick` 在不同频率的回测中的触发情况则有所不同。

#### 日回测 {#rqalpha-plus-frequency-daily}

日回测适用于相对长周期的策略，日回测会忽略掉盘中所有市场变动细节，将每个标的每日的行情变动情况汇总成一根 k 线。

在日回测中，盘中约定函数 `handle_bar` 会在每个交易日**收盘**时被触发一次，在该函数中访问 `bar_dict` 参数可以获取到当前交易日的日 k 线，在该函数中发出的订单都会被以当日的**收盘价**撮合。

#### 分钟回测 {#rqalpha-plus-frequency-minute}

分钟回测适用于关注日内行情变动情况的策略，分钟回测会把交易时间按分钟切片，每个标的每分钟内的所有行情变动情况会被合成为一根具有高开低收等信息的分钟 k 线。

分钟回测中盘中约定函数 `handle_bar` 会在每分钟**结束**时触发一次，在该函数中访问 `bar_dict` 参数可以获取到刚刚结束的一分钟的分钟 k 线。例如，股票策略在每个交易日的 9:31 会首次触发 `handle_bar`，此次触发的 `handle_bar` 中可以访问到的分钟线为 9:30-9:31 的分钟线。分钟回测中亦可以通过 `history_bars` 接口获取历史日 k 线。

分钟回测可以[设置撮合方式](#rqalpha-plus-matching-type)为**立即使用当前分钟线的收盘价撮合**或**在下一分钟以下一个分钟线的开盘价撮合**。

需要注意，因为不同品种的交易时间段不同，故需要策略告知 RQAlphaPlus 该策略关注的标的品种，以便 RQAlphaPlus 在正确的时间触发对应的 `handle_bar`：

- 若用户配置了股票账户的资金账号，则 RQAlphaPlus 会在股票交易时间内触发 `handle_bar`，即 9:31 - 11:30 和 13:01 - 15:00。
- 若策略交易期货、期权合约，则需要预先（在 `init` 或 `handle_bar` 中）使用 `subscribe` 接口订阅所关注的合约，RQAlphaPlus 将会触发对应合约交易时间的 `handle_bar`，`subscribe` 的使用方法：
  ```python
  subscribe('RB2010')
  ```
- 若订阅了多种交易时间不同的合约，或同时交易期货和股票，`handle_bar` 触发的时间段将是这些交易时间段的并集。
- 若在 `handle_bar` 中从 `bar_dict` 获取当前**未在交易**的标的的 k 线，策略将会获取到"无效"的 Bar 对象，该对象所有字段的值均为 NaN。

#### tick 回测 {#rqalpha-plus-frequency-tick}

tick 回测为 RQAlphaPlus 提供的最细粒度的回测。此处的 tick 实际上指的是 A 股市场的快照（snapshot）行情，通常情况下期货合约每 500ms 一个快照，股票每 3s 一个快照（Ricequant 提供的快照行情直接来源于交易所，故以交易所发出的行情为准）。

tick 回测中盘中约定函数 `handle_tick` 接受两个参数 `context` 和 `tick`。参数 `tick` 的类型为 `TickObject`，不同于 `handle_bar` 中的 `bar_dict`，此处的 `tick` 仅包含单个标的的快照行情，也就是说，**每个标的的快照行情更新都会分别触发 `handle_tick` 的运行**。

运行 tick 回测时，策略所关注的所有标的都需要使用 `subscribe` 接口订阅，以便 RQAlphaPlus 触发对应标的的 `handle_tick` 的运行。

## 标的品种 {#rqalpha-plus-instruments}

RQAlphaPlus 支持股票、期货、期权、可转债、场内基金和上金所现货合约等多种金融标的的回测。不同品种的标的在发单接口、费用计算、账户和仓位计算等方面有所差异。

#### 股票和场内基金 {#rqalpha-plus-instruments-stocks}

RQAlphaPlus 支持 A 股和 ETF、LOF 等场内基金回测

- 发单接口：股票和场内基金的六个发单函数在[快速上手](quick-start.md#rqalpha-plus-write-strategy)已介绍过，此处不再赘述
- 账户设置：股票和场内基金的持仓归属于股票（STOCK）账户
- 分红拆分和复权：RQAlphaPlus 中撮合、计算收益等适用的价格均为未复权价格，发生分红拆分等行为时 RQAlphaPlus 会按照实际情况为策略账户补充现金和持仓。使用 `history_bars` 接口可以获取到在策略运行过程中动态复权的价格。
  - 分红再投资：开启分红再投资后 RQAlphaPlus 会自动使用分红得到的现金买入相同的股票或场内基金持仓
    - 命令行运行时，使用 `--dividend-reinvestment` 参数开启分红再投资
    - 函数入口运行时，使用如下配置开启分红再投资：
      ```python
      {"mod": {"sys_accounts": {"dividend_reinvestment": True}}}
      ```
- 佣金和印花税：股票交易会产生佣金和印花税。佣金费率默认万八，单笔订单最小佣金为 5 元；印花税对卖方单边征收，税率为 0.1%
  - 可以通过配置佣金倍率控制费率，如佣金倍率设置为 1.1，则 RQAlphaPlus 使用的费率为 0.00088
    - 命令行运行时，使用 `--commission-multiplier 1.1` 配置佣金倍率
    - 函数入口运行时，使用如下配置设置佣金赔率：
      ```python
      {"mod": {"sys_transaction_cost": {"commission_multiplier": 1.1}}}
      ```
- T+1：股票交易默认开启 T+1 限制，即当日买入的股票需要等到下个交易日才能卖出
  - 命令行运行时，使用 `--no-stock-t1` 关闭 T+1 限制
  - 函数入口运行时，使用如下配置关闭 T+1 限制
    ```python
    {"mod": {"sys_accounts": {"stock_t1": False}}}
    ```

#### 期货 {#rqalpha-plus-instruments-futures}

RQAlphaPlus 支持期货回测

- 发单接口：不同于股票，期货可使用如下四个接口发单，详细用法可查阅 [API 手册](../api/order-api.md)。
  - buy_open：多头开仓，接受合约代码、交易数量、限价单价格（可选）为参数，例如：
    ```python
    buy_open("RB2010", 2)
    ```
  - sell_close：多头平仓，接受合约代码、交易数量、限价单价格（可选）、是否平今（可选）为参数，例如：
    ```python
    sell_close("RB2010", 1, price=3100, close_today=True)
    ```
  - sell_open：空头开仓，参数与 `buy_open` 相同
  - buy_close：空头平仓，参数与 `sell_close` 相同
- 账户设置：期货持仓归属于期货（FUTURE）账户
- 保证金交易：期货采用保证金交易，持有期货仓位会占用保证金，这部分资金会被冻结，不能再用于发单，保证金会在平仓时解冻。
  - RQAlphaPlus 使用的保证金率可以通过 `instruments` 接口查看，该接口接收合约代码参数，返回 `Instrument` 对象，例如使用如下代码查询 RB2010 的保证金率：
    ```python
    instruments("RB2010").margin_rate
    ```
  - 可以通过设置保证金倍率来调整 RQAlphaPlus 的保证金率，实际使用的保证金率为默认的保证金率乘以保证金倍率
    - 命令行运行时，使用 `-mm 1.1` 或 `--margin-muliplier 1.1` 设置保证金倍率
    - 函数入口运行时，使用如下配置设置保证金倍率
      ```python
      {"base": {"margin_multiplier": 1.1}}
      ```
- 逐日盯市：期货采用“逐日盯市”制度，每日盘后会进行结算，将浮盈浮亏计入现金。

#### 期权 {#rqalpha-plus-instruments-options}

RQAlphaPlus 支持商品、股指、ETF 期权回测。

- 发单接口：交易期权使用与期货相同的四个发单接口。
- 账户设置：根据实际市场中所在交易所不同，期权持仓分属股票（STOCK）和期货（FUTURE）账户，其中 ETF 期权属于股票账户，商品期权和股指期权属于期货账户。
- 行权
  - 行权采用现金交割，即将行权产生的盈利或亏损直接计入现金中。
  - 主动行权：期权可通过 [`exercise` 接口](../api/order-api#rqalpha-plus-api-order-exercise) 主动行权，该函数接收合约代码和行权数量两个参数，例如：
    ```python
    exercise("M1905C2350", 2)
    ```
  - 被动行权：期权持有至到期日将会触发自动行权。对于权利方（多头）持仓，若 RQAlphaPlus 判定行权可以盈利，则触发自动行权，否则仓位作废；而义务方（空头）持仓会在 RQAlphaPlus 判定对手方可以盈利时触发行权
  - 行权滑点：为了模拟真实市场中行权委托与到账间这段时间段内底层标的价格发生波动带来的风险，RQAlphaPlus 提供了行权滑点功能，通过配置行权滑点，可以使得行权盈利的判定更为严苛。对于认购期权，0.1 的滑点代表即使在交割日标的价格降低 10%，本次行权仍然能盈利；而对于认沽期权，代表在交割日即使标的价格上涨 10%，仍然能盈利。默认行权滑点为 0 。行权滑点只会影响自动行权的判定，而不影响行权交割的金额。
    - 命令行运行时，使用如下参数设置行权滑点：
      ```bash
      -mc option.exercise_slippage 0.1
      ```
    - 函数入口运行时，使用如下配置设置行权滑点：
      ```python
      {"mod": {"option": {"exercise_slippage": 0.1}}}
      ```
- 权利金和保证金
  - 权利方（多头）：开仓需要缴纳权利金，该过程与股票的开仓类似
  - 义务方（空头）：开仓会收取权利金并付出保证金，保证金会被冻结（类似期货开仓）；同时义务方也采取逐日盯市制度，每日盘后结算，浮盈浮亏将被计入现金。

#### 可转债 {#rqalpha-plus-instruments-convertible}

RQAlphaPlus 支持可转换债券、场内公开交易的可交换债券、分离交易可转债（债券等）的回测。

- 发单接口：可转债使用 `order_shares`、`order_value`、`order_percent`、`order_target_value`、`order_target_percent` 五个接口下单，用法与股票相同
- 账户设置：可转债持仓归属于股票（STOCK）账户
- 回售和转股：可转债支持主动发起回售或转股，使用 [`exercise` 接口](../api/order-api#rqalpha-plus-api-order-exercise)，相比于期权行权，除了合约代码和数量两个参数，还加入了第三个参数用于区分本次行权是转股还是回售，如：
  ```python
  exercise("132003.XSHG", 100, convert=False)  # 回售
  exercise("132003.XSHG", 100, convert=True)   # 转股
  ```
- 本息偿付：可转债发生付息时，利息将进入对应账户的现金；发生强制赎回时，仓位将被清空，对应账户的现金会按照强赎时实际的现金流变动。

#### 场外基金 {#rqalpha-plus-instruments-fund}

- 发单接口：场外基金可使用如下六个接口发单，详细用法可查阅 [API 手册](../api/order-api#rqalpha-plus-api-order-subscribe-value)
  - subscribe_value：按申购金额申购基金，接受合约代码、交易金额为参数，例如：
    ```python
    subscribe_value("004241", 1000)
    ```
  - subscribe_shares：按份额申购基金，接受合约代码、交易数量为参数，例如：
    ```python
    subscribe_shares("004241", 500)
    ```
  - subscribe_percent：按可用资金权重申购基金，接受合约代码、占现有可用资金的百分比为参数，例如：
    ```python
    subscribe_percent("004241", 0.1)
    ```
  - redeem_shares：按份额赎回基金，接受合约代码、交易数量为参数，例如：
    ```python
    redeem_shares("004241", 500)
    ```
  - redeem_value：按金额赎回基金，接受合约代码、交易金额为参数，例如：
    ```python
    redeem_value("004241", 1000)
    ```
  - redeem_percent：按剩余份额权重赎回基金，接受合约代码、占剩余份额的百分比为参数，例如：
    ```python
    redeem_percent("004241", 0.1)
    ```
- 账户设置：场外基金持仓归属于股票（STOCK）账户
- 费用：所有基金前端收费,支持通过参数配置前端费率，默认前端费率 1.5%

  - 命令行运行时，使用 `--fee-ratio 0.015` 设置基金前端费率
  - 函数入口运行时，使用如下配置设置前端费率：
    ```python
      {"fund": {"fee_ratio": 0.015}}
    ```
  - 赎回不收取费用

- 申购赎回状态限制：可通过参数配置是否根据状态限制申赎，默认开启申购赎回状态限制
  - 命令行运行时，使用 `--status-limit` 参数开启申购赎回状态限制
  - 函数入口运行时，使用如下配置开启申购赎回状态限制：
    ```python
      {"fund": {"status_limit": True}}
    ```
- 申购金额限制：是否限制申购金额的上下限，默认开启。

  - 命令行运行时，使用 `--subscription-limit` 参数开启申购金额限制，若开启申购上下限限制，则超过上限时部分成交，低于下限时拒单，若不开启则以申购金额成交。
  - 函数入口运行时，使用如下配置开启申购金额限制：
    ```python
      {"fund": {"subscription_limit": True}}
    ```

- 申购赎回到账时间：可通过参数设置所有基金的申购赎回到账时间。

  - 函数入口运行时，使用如下配置设置基金申购赎回到账时间：

  ```python
    {"fund": {
        # 基金申购份额到账时间
        "subscription_receiving_days": 1,
        # 基金赎回金额到账时间
        "redemption_receiving_days": 3,
        }
    }

  ```

- 分红拆分：基金发生分红拆分时，RQAlpha 自动处理为策略账户补充现金或持仓，
  - 分红再投资：前文介绍的股票分红再投资参数同样适用于场外公募基金，开启分红再投资后 RQAlpha 会自动使用分红得到的现金买入基金份额，分红再投资份额到账时间和基金申购设置到账时间一致。
    - 命令行运行时，使用 `--dividend-reinvestment` 参数开启分红再投资
    - 函数入口运行时，使用如下配置开启分红再投资：
      ```python
      {"mod": {"sys_accounts": {"dividend_reinvestment": True}}}
      ```
      _对于货币基金一律采用分红再投资，不受`--dividend-reinvestment` 参数影响_

#### 上金所现货 {#rqalpha-plus-instruments-spot}

RQAlphaPlus 支持上海黄金交易所交易的黄金、白银、铂金等现货合约的回测。

- 发单接口：与期货交易相同，上金所现合约货使用 `buy_open`、`sell_close`、`sell_open` 和 `sell_close` 四个接口下单。
- 账户设置：上金所现货合约持仓归属于股票（STOCK）账户。
- 保证金交易：与期货类似，上金所现货合约采用保证金交易，同样可以配置保证金倍率，同样采用“逐日盯市”制度。

## 事前风控 {#rqalpha-plus-risk-control}

RQAlphaPlus 中发出的订单在撮合前会经过多项事前风控，某项风控不通过会导致下单失败，部分事前风控可以自定义配置。

- 验资风控：检验当前可用资金是否足够下单，默认开启。关闭该风控项可能导致剩余资金为负数
  - 命令行运行策略时，使用 `--no-cash-validation` 以关闭验资风控
  - 函数入口运行策略时，使用如下配置以关闭验资风控：
    ```python
    {"mod": {"sys_risk": {"validate_cash": False}}}
    ```
- 验券风控：针对卖单（平仓单、行权单）检验当前可平仓位是否足够平仓
- 自成交风控：针对新发订单，检验当前是否有方向相反的、存在和新发订单相互成交风险的挂单
  - 自成交风控默认关闭，通过命令行运行策略时，可以使用如下参数开启：
    ```bash
    -mc sys_risk.validate_self_trade true
    ```
  - 通过函数入口运行时，可以使用如下配置开启：
    ```python
    {"mod": {"sys_risk": {"validate_self_trade": True}}}
    ```
- 债券发行总额风控：针对可转债订单，检验新发订单和已有持仓票面价值总和是否超过债券发行总额
- 行权日期风控：检验行权日期是否合法，如欧式期权仅可在到期日行权，可转债仅可在转股期内转股、仅可在回售登记日期范围内回售

## 模拟撮合 {#rqalpha-plus-matching}

RQAlphaPlus 在回测中会模拟交易所的行为撮合策略发出的订单。RQAlphaPlus 内置多种撮合和滑点模型，可按需呈现出对真实市场不同程度对模拟。

#### 撮合方式 {#rqalpha-plus-matching-type}

RQAlphaPlus 支持五种撮合模型，不同撮合模型之前的区别在于撮合的时机以及如何决定撮合使用的参考价格。

使用命令行运行时，使用 `-mt` 或 `--matching-type` 参数设置撮合类型，如：

```bash
# 设置撮合类型为当前 bar 收盘价撮合
--matching-type current_bar
```

使用函数入口运行时，使用如下的配置设置撮合类型：

```python
# 设置撮合类型为当前 bar 收盘价撮合
{"mod": {"sys_simulation": {"matching_type": "current_bar"}}}
```

所有可用的撮合方式如下：

- `current_bar`：立即使用当前 k 线的收盘价作为参考价撮合，可在日回测和分钟回测中使用，该回测方式是 RQAlphaPlus 默认的撮合方式
- `next_bar`：在下一个 `handle_bar` 触发前使用下一跟 k 线的开盘价撮合，可在分钟回测中使用
- `last`：在下一个 `handle_tick` 触发前使用该 tick 的最新价撮合，可在 tick 回测中使用
- `best_own`：在下一个 `handle_tick` 触发前使用该 tick 的己方最优报盘价格撮合，可在 tick 回测中使用
- `best_counterparty`：在下一个 `handle_tick` 触发前使用该 tick 的对手方最优报盘价格撮合，可在 tick 回测中使用
- `vwap`：成交量加权平均价撮合，可在日回测和分钟回测中使用

**需要注意：**

- `next_bar` 撮合方式在日回测中已不适用，如果需要当前开盘成交撮合，可以使用[open_auction](../api/callback#rqalpha-plus-api-callback-open-auction)函数在盘前集合竞价时发单，以当日开盘价撮合。
- 对于场外基金全部采用当日单位净值成交。

#### 滑点 {#rqalpha-plus-matching-slippage}

RQAlphaPlus 支持两种滑点模型，以模拟真实交易中实际成交价与挂单价格存在差异的情况

使用命令行运行时，使用 `--slippage-model` 参数设置滑点模型，使用 `-sp` 或 `--slippage` 参数设置“滑点值”，如：

```bash
# 成交价会产生千分之一的恶化
--slippage-model PriceRatioSlippage --slippage 0.001
```

使用命令行运行时，使用如下的配置设置滑点：

```python
# 成交价会产生千分之一的恶化
{"mod":{"sys_simulation": {
    "slippage_model": "PriceRatioSlippage",
    "slippage": 0.001
}}}
```

可选的滑点模型如下：

- `PriceRatioSlippage`：成交价格按照一定比例进行恶化，“滑点值” 即为价格恶化的比例
- `TickSizeSlippage`：成交价按照最小价格变动单位进行恶化，价格恶化的值为“滑点值”乘以标的的最小价格变动单位

**_场外基金不支持滑点设置。_**

#### 成交量限制 {#rqalpha-plus-matching-volume}

在日和分钟回测中，RQAlphaPlus 会对订单的成交量进行限制，每个 `handle_bar` 中发出的订单总成交量不能超过当前 k 线所覆盖时间段内市场上该标的总成交量的一定比例，订单在该比例内的部分会被撮合，超出部分会被拒单。该比例默认为 0.25。

使用命令行运行时，通过 `-mc sys_simulation.volume_limit` 和 `-mc sys_simulation.volume_percent` 参数设置成交量限制情况，如：

```bash
# 开启成交量限制并把订单成交量限制在市场上总成交量的 10%
-mc sys_simulation.volume_limit true -mc sys_simulation.volume_percent 0.1

# 关闭成交量限制
-mc sys_simulation.volume_limit false
```

使用函数入口运行策略时，使用如下配置设置成交量限制情况：

```python
# 开启成交量限制并把订单成交量限制到市场上总成交量的 10%
{"mod": {"sys_simulation": {
    "volume_limit": True,
    "volume_percent": 0.1
}}}

# 关闭成交量限制
{"mod": {"sys_simulation": {
    "volume_limit": False,
}}}
```

**_场外基金不支持成交量限制设置。_**

## 自定义基准 {#rqalpha-plus-benchmark}

RQAlpha 支持设置单个合约作为基准外，还对支持 order_book_id 加权作为回测的基准。
使用命令行运行时，使用如下的配置设置指数加权基准：

```bash
--benchmark 000300.XSHE:0.7,000905.XSHG:0.3
```

使用函数入口运行策略时，使用如下配置设置指数加权基准：

```python
"mod": {"sys_analyser": {
        "benchmark": {
            "000300.XSHE": 0.7,
            "000905.XSHG": 0.3
            }
        }
    }


```

## 出入金 {#rqalpha-plus-cash-flow}

RQAlpha 支持回测过程中增加或减少资金，以满足回测过程中账户资金调整的需求，支持在 handle_bar 中调用。

- 出金：通过`withdraw(account_type, amount)`接口对账户减少资金，举例如下：

```python
    #对期货账户减少10w资金
   withdraw("FUTURE", 100000)

```

- 入金：通过`deposit(account_type, amount)`接口对账户增加资金，举例如下：

```python
   #对股票账户增加10w资金
   deposit("STOCK", 100000)
```

## 管理费用 {#rqalpha-plus-management-fee}

RQAlpha 支持通过参数配置管理费，每日计提管理费。
使用命令行运行时，使用如下的配置对股票账户收取 0.02%的管理费（每个交易日收取，也可以对 future 账户收取管理费） ：

```bash
--management-fee stock 0.02%

#管理费 = total_value * 管理费率,每日计提

```

使用函数入口运行时，使用如下配置设置管理费率：

```python
"mod": {"sys_simulation":{
            "enabled": True,
            "management_fee": [("stock", 0.02%)],

        }

}
```

## 增量回测 {#rqalpha-plus-incremental}

RQAlpha 支持日级别增量回测的功能，即将当前策略回测的结果数据保存到本地，后续对相同策略运行回测时在该策略本地回测结果的基础上继续运行。

- mod 操作
  可以使用如下命令开启增量回测的 mod，默认增量回测的 mod 是关闭的。
  ```bash
  rqalpha-plus mod enable incremental
  ```
  使用如下命令关闭增量回测的 mod
  ```bash
  rqalpha-plus mod disable incremental
  ```
  使用如下命令查看目前开启了哪些 mod
  ```bash
  rqalpha-plus mod list
  ```
- 参数设置
  开启增量回测的 mod 后，使用命令行运行时，使用`--persist-folder`指定存储文件路径（启动 mod 不设置路径增量无效），使用--strategy-id 指定策略运行 id（若不指定，默认为 1），举例如下：

  ```bash
  # 在当前目录的/persist下查看是否有文件名为2的文件夹，若有则读取文件内容，在本地保存回测结果的基础上运行增量回测，若没有则在当前目录/persist下生成一个命名为2的文件夹保存本次回测的结果
  --persist-folder . --strategy-id 2
  ```

  使用函数入口运行时，配置如下：

  ```python
  {
      "mod": {
          "incremental":{
              'enabled': True,
              "persist_folder": '.',
              "strategy_id": 2,
          }
      }
  }
  ```

## 策略内参数配置 {#rqalpha-plus-config}

使用命令行运行策略时，可以使用与函数入口运行策略时传入的 `config` 相同的格式编写配置，并把配置写在策略文件内。策略内参数配置的优先级低于命令行参数的优先级。

策略内配置需要赋值给策略文件内的全局变量 `__config__`，如将下述内容写入 macd_000001.py 文件：

```python
import talib

__config__ = {
    "base": {
        "accounts": {
            "STOCK": 100000,
        },
        "start_date": "20190101",
        "end_date": "20191231",
    },
    "mod": {
        "sys_analyser": {
            "plot": True,
            "benchmark": "000300.XSHG"
        }
    }
}


def init(context):
    context.stock = "000001.XSHE"

    context.SHORTPERIOD = 12
    context.LONGPERIOD = 26
    context.SMOOTHPERIOD = 9
    context.OBSERVATION = 100


def handle_bar(context, bar_dict):
    prices = history_bars(context.stock, context.OBSERVATION, '1d', 'close')
    macd, macd_signal, _ = talib.MACD(
        prices, context.SHORTPERIOD, context.LONGPERIOD, context.SMOOTHPERIOD
    )

    if macd[-1] > macd_signal[-1] and macd[-2] < macd_signal[-2]:
        order_target_percent(context.stock, 1)

    if macd[-1] < macd_signal[-1] and macd[-2] > macd_signal[-2]:
        if get_position(context.stock).quantity > 0:
            order_target_percent(context.stock, 0)
```

可以直接使用如下命令运行策略，仅仅需要使用 `-f` 参数指定策略文件，不再需要传入更多参数：

```bash
rqalpha-plus run -f macd_000001.py
```

## 定时器 {#rqalpha-plus-scheduler}

除了约定函数以供策略逻辑在市场发生变动时运行外，RQAlphaPlus 还提供了定时器功能以供策略逻辑周期性地执行。

定时器暂只支持**股票日、分钟级回测**。

定时器的使用方式是在 `init` 中通过定时器接口注册函数，被注册的函数会在符合指定的“时间规则”时被调用，如：

```python
# 每日开市时打印当前剩余资金

#scheduler调用的函数需要包括context, bar_dict两个输入参数
def log_cash(context, bar_dict):
    logger.info("Remaning cash: %r" % context.portfolio.cash)

def init(context):
    #...
    # 每天运行一次
    scheduler.run_daily(log_cash)
```

除每日运行之外，定时器还支持注册每周、每月运行的函数，并且支持指定如“每月的第 N 个交易日”或“每天的第 N 分钟”的时间规则。详细的使用方法可查阅 scheduler 定时器接口手册。

<!-- TODO: ### 自定义因子 -->

<!-- TODO: ### 股票投资优化器 -->

## 读取本地持仓权重运行回测 {#rqalpha-plus-local-holdings}

支持读取本地持仓权重样例运行回测，举例如本地调仓权重样例如下：

| TRADE_DT | TICKER      | NAME     | TARGET_WEIGHT |
| -------- | ----------- | -------- | ------------- |
| 20191202 | 000001.XSHE | 平安银行 | 0.03          |
| 20191202 | 002916.XSHE | 深南电路 | 0.02          |
| ...      | ...         | ...      | ...           |
| 20200102 | 002916.XSHE | 深南电路 | 0.02          |

简单样例策略如下，若需要一个完整的策略范例请点击：[根据本地持仓权重运行回测范例](#rqalpha-plus-local-holdings)

```python
import pandas
import numpy

import rqdatac

# pip install -i https://pypi.tuna.tsinghua.edu.cn/simple xlrd
# rqalpha-plus run -f holding_target_position_simplified.py

__config__ = {
    "base": {
        "start_date": "20191201",
        "end_date": "20200930",
        "accounts": {
            "stock": 100000000,
        },
    },
}


# 在这个方法中编写任何的初始化逻辑。context对象将会在你的算法策略的任何方法之间做传递。
def init(context):
    df = pandas.read_excel('调仓权重样例.xlsx', dtype={
        'TARGET_WEIGHT': numpy.float64, 'TICKER': numpy.str_, 'TRADE_DT': numpy.int32
    })
    df['TICKER'] = df['TICKER'].apply(lambda x: rqdatac.id_convert(x) if ".OF" not in x else x)
    context.target = {d: t.set_index("TICKER")["TARGET_WEIGHT"].to_dict() for d, t in df.groupby("TRADE_DT")}


# 你选择的证券的数据更新将会触发此段逻辑，例如日或分钟历史数据切片或者是实时数据切片更新
def handle_bar(context, bar_dict):
    today = context.now.year * 10000 + context.now.month * 100 + context.now.day
    if today not in context.target:
        return
    order_target_portfolio(context.target[today])
```
