# 买卖申赎接口 {#rqalpha-plus-api-order}

### OrderStyle - 订单类型 {#rqalpha-plus-api-order-style}

该类型可供后续下单接口中 price_or_style 参数使用。

#### 市价单

```python
class rqalpha.model.order.MarketOrder
```

#### 参数

无

#### 范例

```python
order_shares("000001.XSHE", amount=100, price_or_style=MarketOrder())
```

<br/>

#### 限价单

```python
class rqalpha.model.order.LimitOrder(limit_price)
```

#### 参数

| 参数名      | 类型    | 说明 |
| ----------- | ------- | ---- |
| limit_price | _float_ | 价格 |

#### 范例

```python
order_shares("000001.XSHE", amount=100, price_or_style=LimitOrder(10))
```

<br/>

#### 算法时间加权价格订单

```python
class rqalpha.model.order.TWAPOrder(start_min, end_min)
```

#### 参数

| 参数名    | 类型  | 说明         |
| --------- | ----- | ------------ |
| start_min | _int_ | 分钟起始时间 |
| end_min   | _int_ | 分钟结束时间 |

#### 范例

```python
order_shares("000001.XSHE", amount=100, price_or_style=TWAPOrder(931, 945))
```

<br/>

#### 算法成交量加权价格订单

```python
class rqalpha.model.order.VWAPOrder(start_min, end_min)
```

#### 参数

| 参数名    | 类型  | 说明         |
| --------- | ----- | ------------ |
| start_min | _int_ | 分钟起始时间 |
| end_min   | _int_ | 分钟结束时间 |

#### 范例

```python
order_shares("000001.XSHE", amount=100, price_or_style=VWAPOrder(931, 945))
```

### submit_order - 自由参数下单「通用」 {#rqalpha-plus-api-order-submit-order}

```python
rqalpha.api.submit_order(id_or_ins, amount, side, price=None, position_effect=None)
```

通用下单函数，策略可以通过该函数自由选择参数下单。

#### 参数

| 参数名          | 类型                                                                           | 说明                              |
| --------------- | ------------------------------------------------------------------------------ | --------------------------------- |
| id_or_ins       | _Union [str, [Instrument](./types#rqalpha-plus-api-types-instrument)]_         | 下单标的物                        |
| amount          | _float_                                                                        | 下单量，需为正数                  |
| side            | _[SIDE](./enums#rqalpha-plus-api-enums-side)_                                  | 多空方向                          |
| price           | _Optional [float]_                                                             | 下单价格，默认为 None，表示市价单 |
| position_effect | _Optional [[POSITION_EFFECT](./enums#rqalpha-plus-api-enums-position-effect)]_ | 开平方向，交易股票不需要该参数    |

#### 返回

_Optional[Order]_

#### 范例

```python
# 购买 2000 股的平安银行股票，并以市价单发送：
submit_order('000001.XSHE', 2000, SIDE.BUY)
# 平 10 份 RB1812 多方向的今仓，并以 4000 的价格发送限价单
submit_order('RB1812', 10, SIDE.SELL, price=4000, position_effect=POSITION_EFFECT.CLOSE_TODAY)
```

### order - 智能下单「通用」 {#rqalpha-plus-api-order-order}

```python
rqalpha.api.order(order_book_id, quantity, price_or_style=None, price=None, style=None)
```

全品种通用智能调仓函数

如果不指定 price, 则相当于下 MarketOrder

如果 order_book_id 是股票，等同于调用 order_shares

如果 order_book_id 是期货，则进行智能下单

#### 参数

| 参数名         | 类型                                                                   | 说明                                                                                                                                       |
| -------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| order_book_id  | _Union [str, [Instrument](./types#rqalpha-plus-api-types-instrument)]_ | 下单标的物                                                                                                                                 |
| quantity       | _int_                                                                  | 调仓量，如果 quantity 为正数，则先平 Sell 方向仓位，再开 Buy 方向仓位；<br/> 如果 quantity 为负数，则先平 Buy 反向仓位，再开 Sell 方向仓位 |
| price_or_style | _Union[int, float, OrderStyle, None]_                                  | 默认为 None，表示市价单，可设置价格，表示限价单，也可以直接设置订单类型，有如下选项：MarketOrder、LimitOrder、 TWAPOrder、VWAPOrder        |

#### 返回

_List[Order]_

#### 范例

```python
# 当前仓位为0
# RB1710 多方向调仓2手：调整后变为 BUY 2手
order('RB1710', 2)

# RB1710 空方向调仓3手：先平多方向2手 在开空方向1手，调整后变为 SELL 1手
order('RB1710', -3)
```

### order_to - 智能下单「通用」 {#rqalpha-plus-api-order-order-to}

```python
rqalpha.api.order_to(order_book_id, quantity, price_or_style=None, price=None, style=None)
```

全品种通用智能调仓函数

如果不指定 price, 则相当于 MarketOrder

如果 order_book_id 是股票，则表示仓位调整到多少股

如果 order_book_id 是期货，则进行智能调仓

#### 参数

| 参数名         | 类型                                                                   | 说明                                                                                                                                                                            |
| -------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| order_book_id  | _Union [str, [Instrument](./types#rqalpha-plus-api-types-instrument)]_ | 下单标的物                                                                                                                                                                      |
| quantity       | _int_                                                                  | 调仓量，表示调整至某个仓位，quantity 如果为正数，则先平 SELL 方向仓位，再 BUY 方向开仓 quantity 手<br/> quantity 如果为负数，则先平 BUY 方向仓位，再 SELL 方向开仓 -quantity 手 |
| price_or_style | _Union[int, float, OrderStyle, None]_                                  | 默认为 None，表示市价单，可设置价格，表示限价单，也可以直接设置订单类型，有如下选项：MarketOrder、LimitOrder、 TWAPOrder、VWAPOrder                                             |

#### 返回

_List[Order]_

#### 范例

```python
# 当前仓位为0
# RB1710 调仓至 BUY 2手
order_to('RB1710', 2)

# RB1710 调仓至 SELL 1手
order_to('RB1710', -1)
```

### order_shares - 指定股数交易 {#rqalpha-plus-api-order-order-shares}

```python
rqalpha.api.order_shares(id_or_ins, amount, price_or_style=None, price=None, style=None)
```

指定股数的买/卖单，最常见的落单方式之一。如有需要落单类型当做一个参量传入，如果忽略掉落单类型，那么默认是市价单（market order）。

#### 参数

| 参数名         | 类型                                                                   | 说明                                                                                                                                |
| -------------- | ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| id_or_ins      | _Union [str, [Instrument](./types#rqalpha-plus-api-types-instrument)]_ | 下单标的物                                                                                                                          |
| amount         | _int_                                                                  | 下单量, 正数代表买入，负数代表卖出。将会根据一手 xx 股来向下调整到一手的倍数，比如中国 A 股就是调整成 100 股的倍数。                |
| price_or_style | _Union[int, float, OrderStyle, None]_                                  | 默认为 None，表示市价单，可设置价格，表示限价单，也可以直接设置订单类型，有如下选项：MarketOrder、LimitOrder、 TWAPOrder、VWAPOrder |

#### 返回

_Optional[Order]_

#### 范例

```python
#购买Buy 2000 股的平安银行股票，并以市价单发送：
order_shares('000001.XSHE', 2000)
#卖出2000股的平安银行股票，并以市价单发送：
order_shares('000001.XSHE', -2000)
#购买1000股的平安银行股票，并以限价单发送，价格为￥11：
order_shares('000001.XSHG', 1000, price_or_style=11)
#购买1000股的平安银行股票，并以限价单发送，价格为￥10：
order_shares('000001.XSHG', 1000, price_or_style=LimitOrder(10))
#购买1000股的平安银行股票，并以 9:31 到 9:45 的VWAP价格发送：
order_shares('000001.XSHG', 1000, price_or_style=VWAPOrder(931, 945))
```

### order_lots - 指定手数交易 {#rqalpha-plus-api-order-order-lots}

```python
rqalpha.api.order_lots(id_or_ins, amount, price_or_style=None, price=None, style=None)
```

指定手数发送买/卖单。如有需要落单类型当做一个参量传入，如果忽略掉落单类型，那么默认是市价单（market order）。

#### 参数

| 参数名         | 类型                                                                   | 说明                                                                                                                                |
| -------------- | ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| id_or_ins      | _Union [str, [Instrument](./types#rqalpha-plus-api-types-instrument)]_ | 下单标的物                                                                                                                          |
| amount         | _int_                                                                  | 下单量, 正数代表买入，负数代表卖出。将会根据一手 xx 股来向下调整到一手的倍数，比如中国 A 股就是调整成 100 股的倍数。                |
| price_or_style | _Union[int, float, OrderStyle, None]_                                  | 默认为 None，表示市价单，可设置价格，表示限价单，也可以直接设置订单类型，有如下选项：MarketOrder、LimitOrder、 TWAPOrder、VWAPOrder |

#### 返回

_Optional[Order]_

#### 范例

```python
#买入20手的平安银行股票，并且发送市价单：
order_lots('000001.XSHE', 20)
#买入10手平安银行股票，并且发送限价单，价格为￥10：
order_lots('000001.XSHE', 10, price_or_style=LimitOrder(10))
```

### order_value - 指定价值交易 {#rqalpha-plus-api-order-order-value}

```python
rqalpha.api.order_value(id_or_ins, cash_amount, price_or_style=None, price=None, style=None)
```

使用想要花费的金钱买入/卖出股票，而不是买入/卖出想要的股数，正数代表买入，负数代表卖出。股票的股数总是会被调整成对应的 100 的倍数（在 A 中国 A 股市场 1 手是 100 股）。 如果资金不足，该 API 将会使用最大可用资金发单。

::: tip 需要注意： 当您提交一个买单时，cash_amount 代表的含义是您希望买入股票消耗的金额（包含税费），最终买入的股数不仅和发单的价格有关，还和税费相关的参数设置有关。 当您提交一个卖单时，cash_amount 代表的意义是您希望卖出股票的总价值。如果金额超出了您所持有股票的价值，那么您将卖出所有股票。
:::

#### 参数

| 参数名         | 类型                                                                   | 说明                                                                                                                                |
| -------------- | ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| id_or_ins      | _Union [str, [Instrument](./types#rqalpha-plus-api-types-instrument)]_ | 下单标的物                                                                                                                          |
| cash_amount    | _float_                                                                | 需要花费现金购买/卖出证券的数目。正数代表买入，负数代表卖出。                                                                       |
| price_or_style | _Union[int, float, OrderStyle, None]_                                  | 默认为 None，表示市价单，可设置价格，表示限价单，也可以直接设置订单类型，有如下选项：MarketOrder、LimitOrder、 TWAPOrder、VWAPOrder |

#### 返回

_Optional[Order]_

#### 范例

```python
#花费最多￥10000买入平安银行股票，并以市价单发送。具体下单的数量与您策略税费相关的配置有关。
order_value('000001.XSHE', 10000)
#卖出价值￥10000的现在持有的平安银行, 以10￥价格发出限价单：
order_value('000001.XSHE', -10000, price_or_style=10)
```

### order_percent - 一定比例下单 {#rqalpha-plus-api-order-order-percent}

```python
rqalpha.api.order_percent(id_or_ins, percent, price_or_style=None, price=None, style=None)
```

发送一个花费价值等于目前投资组合（市场价值和目前现金的总和）一定百分比现金的买/卖单，正数代表买，负数代表卖。股票的股数总是会被调整成对应的一手的股票数的倍数（1 手是 100 股）。百分比是一个小数，并且小于或等于 1（<=100%），0.5 表示的是 50%.需要注意，如果资金不足，该 API 将会使用最大可用资金发单。

::: tip 需要注意：

发送买单时，percent 代表的是期望买入股票消耗的金额（包含税费）占投资组合总权益的比例。 发送卖单时，percent 代表的是期望卖出的股票总价值占投资组合总权益的比例。
:::

#### 参数

| 参数名         | 类型                                                                   | 说明                                                                                                                                |
| -------------- | ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| id_or_ins      | _Union [str, [Instrument](./types#rqalpha-plus-api-types-instrument)]_ | 下单标的物                                                                                                                          |
| percent        | _float_                                                                | 占有现有的投资组合价值的百分比。正数表示买入，负数表示卖出。                                                                        |
| price_or_style | _Union[int, float, OrderStyle, None]_                                  | 默认为 None，表示市价单，可设置价格，表示限价单，也可以直接设置订单类型，有如下选项：MarketOrder、LimitOrder、 TWAPOrder、VWAPOrder |

#### 返回

_Optional[Order]_

#### 范例

```python
#花费等于现有投资组合50%价值的现金买入平安银行股票：
order_percent('000001.XSHG', 0.5)
#花费等于现有投资组合50%价值的现金买入平安银行股票, 以10￥限价单：
order_percent('000001.XSHG', 0.5, price_or_style=10)
```

### order_target_value - 目标价值下单 {#rqalpha-plus-api-order-order-target-value}

```python
rqalpha.api.order_target_value(id_or_ins, cash_amount, price_or_style=None, price=None, style=None)
```

买入/卖出并且自动调整该证券的仓位到一个目标价值。 加仓时，cash_amount 代表现有持仓的价值加上即将花费（包含税费）的现金的总价值。 减仓时，cash_amount 代表调整仓位的目标价至。

::: tip 需要注意，如果资金不足，该 API 将会使用最大可用资金发单。
:::

#### 参数

| 参数名         | 类型                                                                                                                                                                 | 说明                                                                                                                                |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| id_or_ins      | _Union [str, [Instrument](./types#rqalpha-plus-api-types-instrument)]_                                                                                               | 下单标的物                                                                                                                          |
| cash_amount    | _float_                                                                                                                                                              | 最终的该证券的仓位目标价值。                                                                                                        |
| price_or_style | _Union[float, OrderStyle, None, Tuple, Tuple[Union[int, float, OrderStyle, None]], Tuple[Union[int, float, OrderStyle, None], Union[int, float, OrderStyle, None]]]_ | 默认为 None，表示市价单，可设置价格，表示限价单，也可以直接设置订单类型，有如下选项：MarketOrder、LimitOrder、 TWAPOrder、VWAPOrder |

#### 返回

_Optional[Order]_

#### 范例

```python
#如果现在的投资组合中持有价值￥3000的平安银行股票的仓位，以下代码范例会发送花费 ￥7000 现金的平安银行买单到市场。（向下调整到最接近每手股数即100的倍数的股数）：
order_target_value('000001.XSHE', 10000)
#如果现在的投资组合中持有价值￥3000的平安银行股票的仓位，以下代码范例会发送10￥限价单共花费 ￥7000 现金的平安银行买单到市场
#或者如果现在的投资组合中持有价值￥13000的平安银行股票的仓位，以下代码范例会发送11￥限价单共花费 ￥3000 现金的平安银行卖单到市场
order_target_value('000001.XSHE', 10000, price_or_style=(10, 11))
```

### order_target_percent - 目标比例下单 {#rqalpha-plus-api-order-order-target-percent}

```python
rqalpha.api.order_target_percent(id_or_ins, percent, price_or_style=None, price=None, style=None)
```

买入/卖出证券以自动调整该证券的仓位到占有一个目标价值。

加仓时，percent 代表证券已有持仓的价值加上即将花费的现金（包含税费）的总值占当前投资组合总价值的比例。 减仓时，percent 代表证券将被调整到的目标价至占当前投资组合总价值的比例。

其实我们需要计算一个 position_to_adjust (即应该调整的仓位)

position_to_adjust = target_position - current_position

投资组合价值等于所有已有仓位的价值和剩余现金的总和。买/卖单会被下舍入一手股数（A 股是 100 的倍数）的倍数。目标百分比应该是一个小数，并且最大值应该<=1，比如 0.5 表示 50%。

如果 position_to_adjust 计算之后是正的，那么会买入该证券，否则会卖出该证券。<b>需要注意，如果需要买入证券而资金不足，该 API 将使用最大可用资金发出订单</b>。

另外，如果您希望大量调整股票仓位，推荐使用 order_target_portfolio 而非在循环中调取 order_target_percent，前者将拥有更好的性能。

#### 参数

| 参数名         | 类型                                                                                                                                                                 | 说明                                                                                                                                |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| id_or_ins      | _Union [str, [Instrument](./types#rqalpha-plus-api-types-instrument)]_                                                                                               | 下单标的物                                                                                                                          |
| percent        | _float_                                                                                                                                                              | 仓位最终所占投资组合总价值的目标百分比。                                                                                            |
| price_or_style | _Union[float, OrderStyle, None, Tuple, Tuple[Union[int, float, OrderStyle, None]], Tuple[Union[int, float, OrderStyle, None], Union[int, float, OrderStyle, None]]]_ | 默认为 None，表示市价单，可设置价格，表示限价单，也可以直接设置订单类型，有如下选项：MarketOrder、LimitOrder、 TWAPOrder、VWAPOrder |

#### 返回

_Optional[Order]_

#### 范例

```python
#如果投资组合中已经有了平安银行股票的仓位，并且占据目前投资组合的10%的价值，那么以下代码会消耗相当于当前投资组合价值5%的现金买入平安银行股票：
order_target_percent('000001.XSHE', 0.15)
#如果投资组合中已经有了平安银行股票的仓位，并且占据目前投资组合的10%的价值，那么以下代码会消耗相当于当前投资组合价值5%的现金以10￥限价单买入平安银行股票：
#或者如果投资组合中已经有了平安银行股票的仓位，并且占据目前投资组合的20%的价值，那么以下代码会消耗相当于当前投资组合价值5%的现金以11￥限价单卖出平安银行股票：
order_target_percent('000001.XSHE', 0.15, price_or_style=(10, 11))
```

### order_target_portfolio - 批量调仓 {#rqalpha-plus-api-order-order-target-portfolio}

```python
rqalpha.api.order_target_portfolio(target_portfolio, price_or_styles={})
```

批量调整股票仓位至目标权重。
::: tip 注意：股票账户中未出现在 target_portfolio 中的资产将被平仓！
:::

该 API 的参数 target_portfolio 为字典，key 为 order_book_id 或 Instrument，value 为权重。 此时将根据参数 price_or_styles 中设置的价格来计算目标持仓数量并调仓。

#### 参数

| 参数名           | 类型                                                                                                                                                                            | 说明                                                                                       |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| target_portfolio | _Dict[str, float]_                                                                                                                                                              | 目标权重字典，key 为 order_book_id，value 为权重。                                         |
| price_or_style   | _Dict[str, Union[float, OrderStyle, None, Tuple, Tuple[Union[int, float, OrderStyle, None]], Tuple[Union[int, float, OrderStyle, None], Union[int, float, OrderStyle, None]]]]_ | 目标下单价格字典，key 为 order_book_id, value 为价格或订单类型或订单类型和价格组成的 tuple |

#### 返回

_Optional[Order]_

#### 范例

```python
# 调整仓位，以使平安银行和万科 A 的持仓占比分别达到 10% 和 15%, 同时发送市价单
order_target_portfolio({
    '000001.XSHE': 0.1,
    '000002.XSHE': 0.15
})

# 调整仓位，分别以 14 和 26 元发出限价单，目标是使平安银行和万科 A 的持仓占比分别达到 10% 和 15%
order_target_portfolio({
    '000001.XSHE': 0.1,
    '000002.XSHE': 0.15
}, {
    '000001.XSHE': 14,
    '000002.XSHE': 26,
})

# 调整仓位，使平安银行和万科 A 的持仓占比分别达到 10% 和 15%。
# 其中平安银行的平仓价为 14 元，开仓价为 15 元；万科 A 的平仓价为 26 元，开仓价为 27 元。
order_target_portfolio({
    '000001.XSHE': 0.1,
    '000002.XSHE': 0.15
}, {
    '000001.XSHE': (15, 14),
    '000002.XSHE': (27, 26)
})
```

### buy_open(期货期权)- 买开 {#rqalpha-plus-api-order-buy-open}

```python
rqalpha.api.buy_open(id_or_ins, amount, price_or_style=None, price=None, style=None)
```

买入开仓。

#### 参数

| 参数名         | 类型                                                                   | 说明                                                                                                                                |
| -------------- | ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| id_or_ins      | _Union [str, [Instrument](./types#rqalpha-plus-api-types-instrument)]_ | 下单标的物                                                                                                                          |
| amount         | _int_                                                                  | 下单手数                                                                                                                            |
| price_or_style | _Union[int, float, OrderStyle, None]_                                  | 默认为 None，表示市价单，可设置价格，表示限价单，也可以直接设置订单类型，有如下选项：MarketOrder、LimitOrder、 TWAPOrder、VWAPOrder |

#### 返回

_Union[Order, List[Order], None]_

#### 范例

```python
#以价格为3500的限价单开仓买入2张上期所AG1607合约：
buy_open('AG1607', amount=2, price_or_style=3500)
```

### sell_close(期货期权) - 平买仓 {#rqalpha-plus-api-order-sell-close}

```python
rqalpha.api.sell_close(id_or_ins, amount, price_or_style=None, price=None, style=None, close_today=False)
```

平买仓

#### 参数

| 参数名         | 类型                                                                   | 说明                                                                                                                                |
| -------------- | ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| id_or_ins      | _Union [str, [Instrument](./types#rqalpha-plus-api-types-instrument)]_ | 下单标的物                                                                                                                          |
| amount         | _int_                                                                  | 下单手数                                                                                                                            |
| close_today    | _Optional[bool]_                                                       | 是否指定发平今仓单，默认为 False，发送平仓单                                                                                        |
| price_or_style | _Union[int, float, OrderStyle, None]_                                  | 默认为 None，表示市价单，可设置价格，表示限价单，也可以直接设置订单类型，有如下选项：MarketOrder、LimitOrder、 TWAPOrder、VWAPOrder |

#### 返回

_Union[Order, List[Order], None]_

#### 范例

```python
# 以市价单将现有IF1603买入平仓2张：
sell_close('IF1603', 2, price_or_style=MarketOrder())
```

### sell_open(期货期权) - 卖开 {#rqalpha-plus-api-order-sell-open}

```python
rqalpha.api.sell_open(id_or_ins, amount, price_or_style=None, price=None, style=None)
```

卖出开仓

#### 参数

| 参数名         | 类型                                                                   | 说明                                                                                                                                |
| -------------- | ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| id_or_ins      | _Union [str, [Instrument](./types#rqalpha-plus-api-types-instrument)]_ | 下单标的物                                                                                                                          |
| amount         | _int_                                                                  | 下单手数                                                                                                                            |
| price_or_style | _Union[int, float, OrderStyle, None]_                                  | 默认为 None，表示市价单，可设置价格，表示限价单，也可以直接设置订单类型，有如下选项：MarketOrder、LimitOrder、 TWAPOrder、VWAPOrder |

#### 返回

_Union[Order, List[Order], None]_

#### 范例

```python
# 以3100发出限价单将现有IF1603卖出开仓2张：
sell_open('IF1603', 2, price_or_style=3100)
```

### buy_close(期货期权) - 平卖仓 {#rqalpha-plus-api-order-buy-close}

```python
buy_close(order_book_id, quantity, price_or_style=MarketOrder())
```

平卖仓

#### 参数

| 参数名         | 类型                                                                   | 说明                                                                                                                                |
| -------------- | ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| id_or_ins      | _Union [str, [Instrument](./types#rqalpha-plus-api-types-instrument)]_ | 下单标的物                                                                                                                          |
| amount         | _int_                                                                  | 下单手数                                                                                                                            |
| close_today    | _Optional[bool]_                                                       | 是否指定发平今仓单，默认为 False，发送平仓单                                                                                        |
| price_or_style | _Union[int, float, OrderStyle, None]_                                  | 默认为 None，表示市价单，可设置价格，表示限价单，也可以直接设置订单类型，有如下选项：MarketOrder、LimitOrder、 TWAPOrder、VWAPOrder |

#### 返回

_Union[Order, List[Order], None]_

#### 范例

```python
#市价单将现有IF1603空仓买入平仓2张：
buy_close('IF1603', 2)
```

### exercise(期权/转债) - 行权 {#rqalpha-plus-api-order-exercise}

```python
rqalpha.api.exercise(id_or_ins, amount, convert=False)
```

行权。针对期权、可转债等含权合约，行使合约权利方被赋予的权利。

#### 参数

| 参数名    | 类型                                                                   | 说明                                                                                    |
| --------- | ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| id_or_ins | _Union [str, [Instrument](./types#rqalpha-plus-api-types-instrument)]_ | 行权合约，order_book_id 或 [Instrument](./types#rqalpha-plus-api-types-instrument) 对象 |
| amount    | _int_                                                                  | 参与行权的合约数量                                                                      |
| convert   | _Optional[bool]_                                                       | 是否为转股（转债行权时可用）                                                            |

#### 返回

_Optional[Order]_

#### 范例

```python
# 行使一张豆粕1905购2350的权力
exercise("M1905C2350", 1)
```

### cancel_order - 撤单 {#rqalpha-plus-api-order-cancel-order}

```python
rqalpha.api.cancel_order(order)
```

撤单

#### 参数

| 参数名 | 类型                                            | 说明                  |
| ------ | ----------------------------------------------- | --------------------- |
| order  | _[Order](./types#rqalpha-plus-api-types-order)_ | 需要撤销的 order 对象 |

#### 返回

_[Order](./types#rqalpha-plus-api-types-order)_

### get_open_orders - 获取未成交订单数据 {#rqalpha-plus-api-order-get-open-orders}

```python
rqalpha.api.get_open_orders()
```

获取当日未成交订单数据

#### 参数

无

#### 返回

_List[[Order](./types#rqalpha-plus-api-types-order)]_

### subscribe_value - 基金申购指令 {#rqalpha-plus-api-order-subscribe-value}

```python
rqalpha_mod_fund.api.subscribe_value(order_book_id, cash_amount)
```

按申购金额申购基金。

#### 参数

| 参数名        | 类型                                                                   | 说明         |
| ------------- | ---------------------------------------------------------------------- | ------------ |
| order_book_id | _Union [str, [Instrument](./types#rqalpha-plus-api-types-instrument)]_ | 申购基金     |
| cash_amount   | _int_                                                                  | 申购所用资金 |

#### 返回

_None or Order_

#### 范例

```python
# 申购五千块的'华夏成长混合'(000001)
order = subscribe_value('000001', 5000)
assert order.avg_price * order.quantity + order.transaction_cost <= 5000
```

### subscribe_percent - 按权重申购基金 {#rqalpha-plus-api-order-subscribe-percent}

```python
rqalpha_mod_fund.api.subscribe_percent(order_book_id, percent)
```

按账户资金百分比申购基金

#### 参数

| 参数名        | 类型                                                                   | 说明         |
| ------------- | ---------------------------------------------------------------------- | ------------ |
| order_book_id | _Union [str, [Instrument](./types#rqalpha-plus-api-types-instrument)]_ | 申购基金     |
| percent       | _int_                                                                  | 可用资金权重 |

#### 返回

_None or Order_

#### 范例

```python
# 用当前账户资金的20%申购
order = subscribe_percent('000001', 0.2)
```

### subscribe_shares - 按照份额申购 {#rqalpha-plus-api-order-subscribe-shares}

```python
rqalpha_mod_fund.api.subscribe_shares(order_book_id, shares)
```

按份额申购。

#### 参数

| 参数名        | 类型                                                                   | 说明     |
| ------------- | ---------------------------------------------------------------------- | -------- |
| order_book_id | _Union [str, [Instrument](./types#rqalpha-plus-api-types-instrument)]_ | 申购基金 |
| shares        | _int_                                                                  | 份额     |

#### 返回

_None or Order_

#### 范例

```python
# 申购3000份'华夏成长混合'(000001)
order = subscribe_shares('000001', 3000)
```

### redeem_percent - 按权重赎回基金 {#rqalpha-plus-api-order-redeem-percent}

```python
rqalpha_mod_fund.api.redeem_percent(order_book_id, percent)
```

按权重赎回基金，需要根据赎回总金额，计算份额。 按比例赎回时，不足 0.01 份则不赎回

#### 参数

| 参数名        | 类型                                                                   | 说明           |
| ------------- | ---------------------------------------------------------------------- | -------------- |
| order_book_id | _Union [str, [Instrument](./types#rqalpha-plus-api-types-instrument)]_ | 赎回基金       |
| percent       | _int_                                                                  | 可赎回份额权重 |

#### 返回

_None or Order_

#### 范例

```python
# 赎回20%的'华夏成长混合'(000001)
order = redeem_percent('000001', 0.2)
```

### redeem_shares - 按份额赎回基金 {#rqalpha-plus-api-order-redeem-shares}

```python
rqalpha_mod_fund.api.redeem_shares(order_book_id, shares)
```

按份额赎回基金。

#### 参数

| 参数名        | 类型                                                                   | 说明     |
| ------------- | ---------------------------------------------------------------------- | -------- |
| order_book_id | _Union [str, [Instrument](./types#rqalpha-plus-api-types-instrument)]_ | 赎回基金 |
| shares        | _int_                                                                  | 赎回份额 |

#### 返回

_None or Order_

#### 范例

```python
#赎回200份'华夏成长混合'(000001)
order = redeem_percent('000001', 200)
```

### redeem_value - 根据赎回总金额计算份额 {#rqalpha-plus-api-order-redeem-value}

```python
rqalpha_mod_fund.api.redeem_value(order_book_id, cash_amount)
```

根据赎回总金额计算份额

#### 参数

| 参数名        | 类型                                                                   | 说明     |
| ------------- | ---------------------------------------------------------------------- | -------- |
| order_book_id | _Union [str, [Instrument](./types#rqalpha-plus-api-types-instrument)]_ | 赎回基金 |
| cash_amount   | _int_                                                                  | 赎回金额 |

#### 返回

_None or Order_

#### 范例

```python
# 赎回价值5000块'华夏成长混合'(000001)
order = redeem_value('000001', 5000)
```
