# 仓位查询接口 {#rqalpha-plus-api-position}

### get_position - 获取持仓对象 {#rqalpha-plus-api-position-get-position}

```python
rqalpha.api.get_position(order_book_id, direction=POSITION_DIRECTION.LONG)
```

获取某个标的的持仓对象。

#### 参数 {#rqalpha-plus-api-position-get-position-params}

| 参数名        | 类型                                                                                | 说明     |
| ------------- | ----------------------------------------------------------------------------------- | -------- |
| order_book_id | _str_                                                                               | 标的编号 |
| direction     | _Optional[[POSITION_DIRECTION](./enums#rqalpha-plus-api-enums-position-direction)]_ | 持仓方向 |

#### 返回 {#rqalpha-plus-api-position-get-position-return}

_Position_

#### 范例 {#rqalpha-plus-api-position-get-position-example}

```python
[In] get_position('000001.XSHE', POSITION_DIRECTION.LONG)
[Out]
StockPosition(order_book_id=000001.XSHE, direction=LONG, quantity=268600, market_value=4995960.0, trading_pnl=0.0, position_pnl=0)
```

### get_positions - 获取全部持仓对象 {#rqalpha-plus-api-position-get-positions}

```python
rqalpha.api.get_positions()
```

获取所有持仓对象列表。

#### 参数 {#rqalpha-plus-api-position-get-positions-params}

无

#### 返回 {#rqalpha-plus-api-position-get-positions-return}

_List[Position]_

#### 范例 {#rqalpha-plus-api-position-get-positions-example}

```python
[In] get_positions()
[Out]
[StockPosition(order_book_id=000001.XSHE, direction=LONG, quantity=1000, market_value=19520.0, trading_pnl=0.0, position_pnl=0),
StockPosition(order_book_id=RB2112, direction=SHORT, quantity=2, market_value=-111580.0, trading_pnl=0.0, position_pnl=0)]
```
