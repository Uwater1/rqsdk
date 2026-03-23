# 示例策略 {#rqalpha-plus-examples}

## 多股票 RSI 算法示例 {#rqalpha-plus-examples-rsi}

```python
import talib


def init(context):

    context.s1 = "000001.XSHE"
    context.s2 = "601988.XSHG"
    context.s3 = "000068.XSHE"
    context.stocks = [context.s1, context.s2, context.s3]

    context.TIME_PERIOD = 14
    context.HIGH_RSI = 85
    context.LOW_RSI = 30
    context.ORDER_PERCENT = 0.3


def handle_bar(context, bar_dict):
    # 对我们选中的股票集合进行loop，运算每一只股票的RSI数值
    for stock in context.stocks:
        # 读取历史数据
        prices = history_bars(stock,context.TIME_PERIOD+1, '1d', 'close')

        # 用Talib计算RSI值
        rsi_data = talib.RSI(prices, timeperiod=context.TIME_PERIOD)[-1]

        cur_position = context.portfolio.positions[stock].quantity
        # 用剩余现金的30%来购买新的股票
        target_available_cash = context.portfolio.cash * context.ORDER_PERCENT

        # 当RSI大于设置的上限阀值，清仓该股票
        if rsi_data > context.HIGH_RSI and cur_position > 0:
            order_target_value(stock, 0)

        # 当RSI小于设置的下限阀值，用剩余cash的一定比例补仓该股
        if rsi_data < context.LOW_RSI:
            logger.info("target available cash caled: " + str(target_available_cash))
            # 如果剩余的现金不够一手 - 100shares，那么会被ricequant 的order management system reject掉
            order_value(stock, target_available_cash)
```

## 商品期货跨品种配对交易 {#rqalpha-plus-examples-futures-pair}

该策略为分钟级别回测。运用了简单的移动平均以及布林带（Bollinger Bands）作为交易信号产生源。有关对冲比率（HedgeRatio）的确定，您可以在我们的研究平台上面通过 import statsmodels.api as sm 引入 statsmodels 中的 OLS 方法进行线性回归估计。具体估计窗口，您可以根据自己策略需要自行选择。

策略中的移动窗口选择为 60 分钟，即在每天开盘 60 分钟内不做任何交易，积累数据计算移动平均值。当然，这一移动窗口也可以根据自身需要进行灵活选择。下面例子中使用了黄金与白银两种商品期货进行配对交易。简单起见，例子中期货的价格并未做对数差处理。

```python
# 可以自己import我们平台支持的第三方python模块，比如pandas、numpy等。
import numpy as np


# 在这个方法中编写任何的初始化逻辑。context对象将会在你的算法策略的任何方法之间做传递。
def init(context):
    context.s1 = 'AG1612'
    context.s2 = 'AU1612'

    # 设置全局计数器
    context.counter = 0

    # 设置滚动窗口
    context.window = 60

    # 设置对冲手数,通过研究历史数据进行价格序列回归得到该值
    context.ratio = 15

    context.up_cross_up_limit = False
    context.down_cross_down_limit = False

    # 设置入场临界值
    context.entry_score = 2

    # 初始化时订阅合约行情。订阅之后的合约行情会在handle_bar中进行更新
    subscribe([context.s1, context.s2])


# before_trading此函数会在每天交易开始前被调用，当天只会被调用一次
def before_trading(context):
    # 样例商品期货在回测区间内有夜盘交易,所以在每日开盘前将计数器清零
    context.counter = 0


# 你选择的期货数据更新将会触发此段逻辑，例如日线或分钟线更新
def handle_bar(context, bar_dict):

    # 获取当前一对合约的仓位情况。如尚未有仓位,则对应持仓量都为0
    position_a = context.portfolio.positions[context.s1]
    position_b = context.portfolio.positions[context.s2]

    context.counter += 1
    # 当累积满一定数量的bar数据时候,进行交易逻辑的判断
    if context.counter > context.window:

        # 获取当天历史分钟线价格队列
        price_array_a = history_bars(context.s1, context.window, '1m', 'close')
        price_array_b = history_bars(context.s2, context.window, '1m', 'close')

        # 计算价差序列、其标准差、均值、上限、下限
        spread_array = price_array_a - context.ratio * price_array_b
        std = np.std(spread_array)
        mean = np.mean(spread_array)
        up_limit = mean + context.entry_score * std
        down_limit = mean - context.entry_score * std

        # 获取当前bar对应合约的收盘价格并计算价差
        price_a = bar_dict[context.s1].close
        price_b = bar_dict[context.s2].close
        spread = price_a - context.ratio * price_b

        # 如果价差低于预先计算得到的下限,则为建仓信号,'买入'价差合约
        if spread <= down_limit and not context.down_cross_down_limit:
            # 可以通过logger打印日志
            logger.info('spread: {}, mean: {}, down_limit: {}'.format(spread, mean, down_limit))
            logger.info('创建买入价差中...')

            # 获取当前剩余的应建仓的数量
            qty_a = 1 - position_a.buy_quantity
            qty_b = context.ratio - position_b.sell_quantity

            # 由于存在成交不超过下一bar成交量25%的限制,所以可能要通过多次发单成交才能够成功建仓
            if qty_a > 0:
                buy_open(context.s1, qty_a)
            if qty_b > 0:
                sell_open(context.s2, qty_b)
            if qty_a == 0 and qty_b == 0:
                # 已成功建立价差的'多仓'
                context.down_cross_down_limit = True
                logger.info('买入价差仓位创建成功!')

        # 如果价差向上回归移动平均线,则为平仓信号
        if spread >= mean and context.down_cross_down_limit:
            logger.info('spread: {}, mean: {}, down_limit: {}'.format(spread, mean, down_limit))
            logger.info('对买入价差仓位进行平仓操作中...')

            # 由于存在成交不超过下一bar成交量25%的限制,所以可能要通过多次发单成交才能够成功建仓
            qty_a = position_a.buy_quantity
            qty_b = position_b.sell_quantity
            if qty_a > 0:
                sell_close(context.s1, qty_a)
            if qty_b > 0:
                buy_close(context.s2, qty_b)
            if qty_a == 0 and qty_b == 0:
                context.down_cross_down_limit = False
                logger.info('买入价差仓位平仓成功!')

        # 如果价差高于预先计算得到的上限,则为建仓信号,'卖出'价差合约
        if spread >= up_limit and not context.up_cross_up_limit:
            logger.info('spread: {}, mean: {}, up_limit: {}'.format(spread, mean, up_limit))
            logger.info('创建卖出价差中...')
            qty_a = 1 - position_a.sell_quantity
            qty_b = context.ratio - position_b.buy_quantity
            if qty_a > 0:
                sell_open(context.s1, qty_a)
            if qty_b > 0:
                buy_open(context.s2, qty_b)
            if qty_a == 0 and qty_b == 0:
                context.up_cross_up_limit = True
                logger.info('卖出价差仓位创建成功')

        # 如果价差向下回归移动平均线,则为平仓信号
        if spread < mean and context.up_cross_up_limit:
            logger.info('spread: {}, mean: {}, up_limit: {}'.format(spread, mean, up_limit))
            logger.info('对卖出价差仓位进行平仓操作中...')
            qty_a = position_a.sell_quantity
            qty_b = position_b.buy_quantity
            if qty_a > 0:
                buy_close(context.s1, qty_a)
            if qty_b > 0:
                sell_close(context.s2, qty_b)
            if qty_a == 0 and qty_b == 0:
                context.up_cross_up_limit = False
                logger.info('卖出价差仓位平仓成功!')
```

## 期权回测样例 {#rqalpha-plus-examples-options}

通过沪深 300 股指期权认购认沽评价构造指数的空头，结合股沪深 300 股指期货多头进行对冲买入并持有策略。

```python
import rqalpha_plus
import rqalpha_mod_option

__config__ = {
    "base": {
        "start_date": "20200101",
        "end_date": "20200221",
        'frequency': '1d',
        "accounts": {
        	# 股指期权使用 future 账户
            "future": 1000000
        }
    },
    "mod": {
        "option": {
            "enabled": True,
            "exercise_slippage": 0
        },
        'sys_simulation': {
            'enabled': True,
            'matching_type': 'current_bar',
            'volume_limit': False,
            'volume_percent': 0,
        },
        'sys_analyser': {
            'plot': True,
        },
    }
}

def init(context):
    context.s1 = 'IO2002C3900'
    context.s2 = 'IO2002P3900'
    context.s3 = 'IF2002'

    subscribe(context.s1)
    subscribe(context.s2)
    subscribe(context.s3)

    context.counter = 0
    print('******* INIT *******')

def before_trading(context):
    pass

def handle_bar(context, bar_dict):
    context.counter += 1
    if context.counter == 1:
        sell_open(context.s1, 3)
        buy_open(context.s2, 3)
        buy_open(context.s3, 1)

def after_trading(context):
    pass
```

## 转债平价溢价率作为信号的分钟回测 {#rqalpha-plus-examples-convertible}

```python
import numpy as np

__config__ = {
    "base": {
        "start_date": "20180601",
        "end_date": "20180610",
        'frequency': '1m',
        "accounts": {
            "stock": 1000000 # 可转债使用 stock 账号
        }
    },
    "mod": {
        'sys_simulation': {
            'enabled': True,
            'matching_type': 'current_bar',
            # 是否允许涨跌停状态下买入、卖出
            'price_limit': False,
            # 是否开启成交量限制
            'volume_limit': False,
        },
        "convertible": {
            "enabled": True,
            # 设置转债回测的佣金费率
            "commission_rate": 0,
            # 设置转债回测的最小佣金
    		"min_commission": 0,
        },
        "sys_analyser": {
            "plot": True,
        },
    }
}

def init(context):
    context.o = "110030.XSHG"
    subscribe(context.o)
    context.count = 0
    context.exercise_flag = False
    context.stock_id = instruments(context.o).stock_code
    context.conversion_value = 0

def handle_bar(context, bar_dict):
    context.count += 1
    cb_price = bar_dict[context.o].close
    stock_price = bar_dict[context.stock_id].close
    # 转债的转股价值
    context.conversion_value = 100/7.24 * stock_price

    # 转债的平价溢价率
    ratio = cb_price / context.conversion_value - 1
    quantity = get_position(context.o, POSITION_DIRECTION.LONG).quantity
    if ratio < 0.31 and quantity < 2000:
        print('当前可转债平价溢价率为 {}，买入转债'.format(ratio))
        order_shares(context.o, 100)

    if ratio > 0.36 and quantity > 0:
        print('当前可转债平价溢价率为 {}，卖出转债'.format(ratio))
        order_shares(context.o, -1*quantity)
```

## 公募基金回测简单样例 {#rqalpha-plus-examples-funds}

```python
INIT_CASH = 100000

__config__ = {
    "base": {
        "start_date": "20190105",
        "end_date": "20200809",
        "accounts": {
            "stock": INIT_CASH
        }
    },
    "mod": {
            "sys_progress": {
                "enabled": True,
                "show": True
            }, "sys_analyser": {
                "enabled": True,
                "plot":True
            }, "fund": {
                # 基金申购前端费率
                "fee_ratio": 0.015,
                # 基金份额到账时间
                "subscription_receiving_days": 1,
                # 赎回金回款时间
                "redemption_receiving_days": 3,
                # 申购金额上下限检查限制
                "subscription_limit": True,
                # 申购状态检查限制
                "status_limit": True,
            },
            'sys_simulation': {
            'enabled': True,
            'matching_type': 'current_bar',

    },
            }

}

# 在这个方法中编写任何的初始化逻辑。context对象将会在你的算法策略的任何方法之间做传递。
def init(context):
    logger.info("init")
    context.s1 = "004241"

    context.fired = False


def before_trading(context):
    pass


# 你选择的证券的数据更新将会触发此段逻辑，例如日或分钟历史数据切片或者是实时数据切片更新
def handle_bar(context, bar_dict):


    if not context.fired:

        subscribe_value(context.s1,INIT_CASH)
        context.fired  = True

    if context.portfolio.total_returns > 0.4 or context.portfolio.total_returns < -0.2:
        context.quantity = get_position(context.s1).quantity
        if context.quantity > 0:
            redeem_shares(context.s1,context.quantity)

```

## 黄金现货回测样例 {#rqalpha-plus-examples-spot}

- 引入黄金现货 AUTD.SGEX 合约和黄金期货主力合约 AU2006 进行配对交易。
- 两个合约的合约乘数相同，都是 1000，所以价差数量比例为 1:1 。合约乘数可以通过 rqdatac.instruments 查询到，对应字段为 contract_multiplier
- 计算期货、现货历史价差的最大最小值，如果当前价差超过历史 10 日最大价差，认为价差即将收敛，做多现货做空期货。

```python
__config__ = {
    'base': {
        'start_date': '20200101',
        'end_date': '20200321',
        'frequency': '1d',
        # 保证金倍率。基于基础保证金水平进行调整
        'margin_multiplier': 1,
        # 商品现货回测这里使用 stock 账户
        'accounts': {
            'stock': 1000000,
            'future': 1000000,
        },
        # 期货交易佣金设置
        'future_info': {
            # 期货品种，如不设置，则按照默认费用进行收取
            'AU': {
                # 平仓费率
                'close_commission_ratio': 0.00005,
                # 开仓费率
                'open_commission_ratio': 0.00005,
                # 平今费率
                'close_commission_today_ratio': 0,
                # BY_MONEY 为按照名义价值收取, BY_VOLUME 为根据成交合约张数收取
                'commission_type': 'BY_MONEY',
            },
        },
    },
    'mod': {
        'spot': {
            'enabled': True,
            'commission_multiplier': 0,
        },
        'sys_simulation': {
            'enabled': True,
            # 是否开启信号模式。如果开启，限价单将按照指定价格成交，并且不受撮合成交量限制
            'signal': False,
            'matching_type': 'current_bar',
            'volume_limit': True,
            'volume_percent': 0.001,
        },
        'sys_analyser': {
            'plot': True,
        },
    }
}

def init(context):
    context.s1 = 'AUTD.SGEX'
    context.s2 = 'AU2006'
    subscribe(context.s1)
    context.counter = 0

def handle_bar(context, bar_dict):
	# 通过 bar_dict 获得当日数据计算当日价差
    current_spread = bar_dict[context.s2].close - bar_dict[context.s1].close

    # 通过 history_bars 获得历史价格序列，计算移动窗口历史价差的最大、最小值
    spot_price = history_bars(context.s1, 10, '1d', 'close')
    future_price = history_bars(context.s2, 10, '1d', 'close')
    max_spread = max(future_price - spot_price)
    min_spread = min(future_price - spot_price)

    if current_spread >= max_spread:
        print('当前价差为 {} 大于过去10天历史最大价差 {}, 买入现货卖出期货'.format(current_spread, max_spread))
        buy_open(context.s1, 5)
        sell_open(context.s2, 5)

    if current_spread < min_spread:
        print('当前价差为 {} 小于过去10天历史最小价差 {}, 买入期货卖出现货'.format(current_spread, min_spread))
        buy_open(context.s2, 5)
        sell_open(context.s1, 5)
```

## 优化器回测样例 {#rqalpha-plus-examples-optimizer}

对于回测中使用优化器的场景，rqalpha 做了简单封装，用户无需传入时间参数， 策略中的优化器 API 参数见：[portfolio_optimize](../api/other-api#rqalpha-plus-api-other-portfolio-optimize)

```python
__config__ = {
    'base': {
        'accounts': {
            'stock': 10000000,
        },
        'start_date': "20170101",
        'end_date': "20200101",
        'frequency': '1d',
    },
    "mod": {
        "optimizer2": {
            "enabled": True,
        },
        'sys_analyser': {
            'enabled': True,
            'benchmark': '000300.XSHG',
        },
    }
}
def rebalance(context, bar_dict):
    cons = [
        WildcardIndustryConstraint(lower_limit=-0.01, upper_limit=0.1, relative=True,
                                   classification=IndustryClassification.ZX, hard=False),
        WildcardStyleConstraint(lower_limit=-0.3, upper_limit=0.3, relative=True, hard=False)
    ]
    pool = [s for s in index_components('000906.XSHG') if not is_suspended(s)]
    s = portfolio_optimize(pool, cons=cons, benchmark='000300.XSHG')
    s = s[s > 0.0001]

    for order_book_id, position in context.stock_account.positions.items():
        if order_book_id not in s:
            order_target_value(order_book_id, 0)

    s = s.sort_values()
    portfolio_value = context.portfolio.total_value

    for order_book_id, weight in s.items():
        order_target_value(order_book_id, portfolio_value * weight)


def init(context):
    scheduler.run_monthly(rebalance, 1)
```

## 根据本地持仓权重运行回测范例 {#rqalpha-plus-examples-local-weights}

这里的样例与前面的精简版相比考虑了更复杂的场景，例如若调仓当天因为风控等原因发单失败，第二个交易日会继续发单，仅供用户参考。

```python
import pandas
import numpy
from rqalpha.apis import *

__config__ = {
    "base": {
        "start_date": "20191201",
        "end_date": "20200930",
        "accounts": {
            "stock": 100000000,
        },
    },
}

def read_tables_df():
    # need  pandas version 0.21.0+
    # need xlrd
    d_type = {'NAME': numpy.str_, 'TARGET_WEIGHT': numpy.float64, 'TICKER': numpy.str_, 'TRADE_DT': numpy.int32}
    columns_name = ["TRADE_DT", "TICKER", "NAME", "TARGET_WEIGHT"]
    df = pandas.read_excel(r'调仓权重样例.xlsx', dtype=d_type)
    if not df.columns.isin(d_type.keys()).all():
        raise TypeError("xlsx文件格式必须有{}四列".format(list(d_type.keys())))
    for date, weight_data in df.groupby("TRADE_DT"):
        if round(weight_data["TARGET_WEIGHT"].sum(), 6) > 1:
            raise ValueError("权重之和出错，请检查{}日的权重".format(date))
    # 转换为米筐order_book_id
    df['TICKER'] = df['TICKER'].apply(lambda x: rqdatac.id_convert(x) if ".OF" not in x else x)
    return df


def on_order_failure(context, event):
    # 拒单时，未成功下单的标的放入第二天下单队列中
    order_book_id = event.order.order_book_id
    context.next_target_queue.append(order_book_id)


# 在这个方法中编写任何的初始化逻辑。context对象将会在你的算法策略的任何方法之间做传递。
def init(context):
    import rqalpha
    import rqalpha_mod_fund
    df = read_tables_df()  # 调仓权重文件
    context.target_weight = df
    context.adjust_days = set(context.target_weight.TRADE_DT.to_list())  # 需要调仓的日期
    context.target_queue = []  # 当日需要调仓标的队列
    context.next_target_queue = []  # 次日需要调仓标的队列
    context.current_target_table = dict()  # 当前持仓权重比例
    subscribe_event(EVENT.ORDER_UNSOLICITED_UPDATE, on_order_failure)


# before_trading此函数会在每天策略交易开始前被调用，当天只会被调用一次
def before_trading(context):
    def dt_2_int_dt(dt):
        return dt.year * 10000 + dt.month * 100 + dt.day

    dt = dt_2_int_dt(context.now)
    if dt in context.adjust_days:
        today_df = context.target_weight[context.target_weight.TRADE_DT == dt].set_index("TICKER").sort_values(
            "TARGET_WEIGHT")
        context.target_queue = today_df.index.to_list()  # 更新需要调仓的队列
        context.current_target_table = today_df["TARGET_WEIGHT"].to_dict()
        context.next_target_queue.clear()
        # 非目标持仓 需要清空
        for i in context.portfolio.positions.keys():
            if i not in context.target_queue:
                # 非目标权重持仓 需要清空
                context.target_queue.insert(0, i)
            else:
                # 当前持仓权重大于目标持仓权重 需要优先卖出获得资金
                equity = context.portfolio.positions[i].long.equity + context.portfolio.positions[i].short.equity
                total_value = context.portfolio.accounts[instruments(i).account_type].total_value
                current_percent = equity / total_value
                if current_percent > context.current_target_table[i]:
                    context.target_queue.remove(i)
                    context.target_queue.insert(0, i)


# 你选择的证券的数据更新将会触发此段逻辑，例如日或分钟历史数据切片或者是实时数据切片更新
def handle_bar(context, bar_dict):
    if context.target_queue:
        for _ticker in context.target_queue:
            _target_weight = context.current_target_table.get(_ticker, 0)
            o = order_target_percent(_ticker, round(_target_weight, 6))
            if o is None:
                logger.info("[{}]下单失败，该标将于次日下单".format(_ticker))
                context.next_target_queue.append(_ticker)
            else:
                logger.info("[{}]下单成功，现下占比{}%".format(_ticker, round(_target_weight, 6) * 100))
        # 下单完成 下单失败的的在队列context.next_target_queue中
        context.target_queue.clear()


# after_trading函数会在每天交易结束后被调用，当天只会被调用一次
def after_trading(context):
    if context.next_target_queue:
        context.target_queue += context.next_target_queue
        context.next_target_queue.clear()
    if context.target_queue:
        logger.info("未完成调仓的标的:{}".format(context.target_queue))


if __name__ == '__main__':
    from rqalpha_plus import run_func

    run_func(init=init, before_trading=before_trading, after_trading=after_trading, handle_bar=handle_bar,
             config=__config__)
```
