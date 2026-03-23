# 枚举常量 {#rqalpha-plus-api-enums}

### POSITION_DIRECTION - 持仓方向 {#rqalpha-plus-api-enums-position-direction}

```python
class rqalpha.const.POSITION_DIRECTION
```

| 枚举值 | 说明   |
|-----|-----|
| LONG   | 多方向 |
| SHORT  | 空方向 |

### SIDE - 交易方向 {#rqalpha-plus-api-enums-side}

```python
class rqalpha.const.SIDE
```

| 枚举值 | 说明 |
|-----|-----|
| BUY    | 买   |
| SELL   | 卖   |

### POSITION_EFFECT - 交易动作 {#rqalpha-plus-api-enums-position-effect}

```python
class rqalpha.const.POSITION_EFFECT
```

| 枚举值      | 说明 |
|-----|-----|
| OPEN        | 开仓 |
| CLOSE       | 平仓 |
| CLOSE_TODAY | 平今 |
| EXERCISE    | 行权 |
| MATCH       | 轧差 |

### RIGHT_TYPE - 权利类型 {#rqalpha-plus-api-enums-right-type}

```python
class rqalpha.const.RIGHT_TYPE
```

| 枚举值    | 说明 |
|-----|-----|
| CONVERT   | 转股 |
| SELL_BACK | 回售 |

### ORDER_TYPE - 订单类型 {#rqalpha-plus-api-enums-order-type}

```python
class rqalpha.const.ORDER_STATUS
```

| 枚举值 | 说明   |
|-----|-----|
| MARKET | 市价单 |
| LIMIT  | 限价单 |

### ORDER_STATUS - 订单状态 {#rqalpha-plus-api-enums-order-status}

```python
class rqalpha.const.ORDER_STATUS
```

| 枚举值      | 说明 |
|-----|-----|
| PENDING_NEW | 待报 |
| ACTIVE      | 已报 |
| FILLED      | 全成 |
| CANCELLED   | 已撤 |
| REJECTED    | 拒单 |

### RUN_TYPE - 策略运行类型 {#rqalpha-plus-api-enums-run-type}

```python
class rqalpha.const.RUN_TYPE
```

| 枚举值        | 说明     |
|-----|-----|
| BACKTEST      | 回测     |
| PAPER_TRADING | 实盘模拟 |

### EVENT - 事件类型 {#rqalpha-plus-api-enums-event}

```python
class rqalpha.events.EVENT
```

| 枚举值                    | 说明         |
|-----|-----|
| ORDER_PENDING_NEW         | 订单创建成功 |
| ORDER_CREATION_PASS       | 订单已报     |
| ORDER_CREATION_REJECT     | 订单创建被拒 |
| ORDER_PENDING_CANCEL      | 订单待撤     |
| ORDER_CANCELLATION_PASS   | 订单撤单成功 |
| ORDER_CANCELLATION_REJECT | 订单撤单被拒 |
| ORDER_UNSOLICITED_UPDATE  | 订单已报被拒 |
| TRADE                     | 成交         |
