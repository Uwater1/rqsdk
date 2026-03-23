# 快速上手 {#rqalpha-plus-quick-start}

在编写策略之前，建议您参考[RQSDK 准备一次回测](../../rqsdk/manual-rqsdk#rqsdk-prep-backtest)的介绍先体验如何准备样例数据、生成样例策略和运行策略的功能，方便您快速了解和使用回测。如果您之前已经按照 RQSDK 文档进行了相关操作，可忽略此提示。接下来会对策略编写、运行策略和获取回测结果等模块进行详细介绍。

## 第一个策略 {#rqalpha-plus-first-strategy}

如下展示的是一个简单的策略，该策略的基本逻辑是在策略运行的第一天半仓买入平安银行（000001.XSHE）并持有至策略运行结束。

```python
def init(context):
    context.fired = False

def handle_bar(context, bar_dict):
    if not context.fired:
        order_target_percent("000001.XSHE", 0.5)
        context.fired = True
```

将上述策略运行于 2019 年全年，运行结束后 RQAlphaPlus 会展示出策略运行期间的收益曲线及部分收益和风险指标。

![运行结果](./img/buy-and-hold-000001.png)

如下展示的是一个稍稍复杂一些的策略，该策略关注个股每日 MACD（指数平滑移动平均线）的情况，捕捉 MACD 和 SIGNAL（信号线）的交叉点作为买卖点：

```python
import talib


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

上述 MACD 策略在 2019 年全年的运行情况如下：

![运行结果](./img/macd-000001.png)

本章后文将以编写该 MACD 策略为目标引导读者了解和熟悉 RQAlphaPlus 的基本用法。

## 基本概念 {#rqalpha-plus-basic-concepts}

为了使用 RQAlphaPlus ，您需要了解几个常用名词，后文中将直接使用这些名词代指相应的概念。

#### 策略 {#rqalpha-plus-basic-concepts-strategy}

用户编写的代码逻辑的集合，这些代码的呈现方式可以是 .py 文件，可以是几个函数，亦可以是 python 中的字符串。策略内通常包含 init、handle_bar、before_trading 等[约定函数](#rqalpha-plus-basic-concepts-callbacks)，策略会被 RQAlphaPlus 执行。

#### 约定函数 {#rqalpha-plus-basic-concepts-callbacks}

策略中实现的有固定名字及参数的函数，如 `init(context)`、`before_trading(context)`和`handle_bar(context, bar_dict)` 等，这些函数会被 RQAlphaPlus 在诸如策略初始化、每日盘前、k 线行情发生更新等时机调用。用户可以在策略中根据需要选择性地实现约定函数，并在这些函数中实现计算、发单等逻辑。

下文中会统称 `init`、`before_trading` 和 `after_trading` 三个约定函数为“盘外约定函数”，统称 `handle_bar` 和 `handle_tick` 为“盘中约定函数”。

完整的约定函数列表可查阅[约定函数 API 手册](../api/callback.md)

#### 数据包 {#rqalpha-plus-basic-concepts-bundle}

为了加速策略运行，RQAlphaPlus 需要将部分策略运行所必须的数据存储于用户计算机本地，这些数据以文件形式存储，包括标的基础数据、交易日历数据和行情数据等，上述数据文件统称为"数据包"。数据包不完整可能导致策略运行出现报错或行为异常，数据包的更新方法详见[下载数据包](#rqalpha-plus-download-data)。

#### 接口（API） {#rqalpha-plus-basic-concepts-api}

RQAlphaPlus 提供了很多可以在策略中调用的函数，其功能包括数据查询、账户和仓位查询和下撤单等等，这些函数及其返回的数据类型统称为 RQAlphaPlus 的接口或 API。如果您也在使用 RQDatac，您可能会注意到部分 RQAlphaPlus 提供的接口与 RQDatac 提供的接口功能和名称形似，但使用方法略有差异，请务必注意区分使用，上述差异形成的原因详见[常见问题](question.md#rqalpha-plus-faq)。

## 下载数据包 {#rqalpha-plus-download-data}

如上文介绍，为了加速策略运行，RQAlphaPlus 需要将部分策略运行所必须的数据存储于用户计算机本地，所以在编写和运行策略前，您需要先下载或生成数据包至本地磁盘。安装 RQSDK 后，您便可以在命令行（Windows）或终端（macOS/Linux）中执行命令以下载或更新数据包。

#### 下载样例数据 {#rqalpha-plus-download-data-sample}

首次使用 RQAlphaPlus 时，您可以通过执行如下命令下载样例数据以快速体验回测功能。

```shell
rqsdk download-data --sample
```

样例数据包含完整的日线和基础数据，可供运行（RQAlphaPlus 支持的）任意合约几乎全时间段的日级别回测。样例数据另外包含有限的分钟和 tick 数据，可供运行所提供的标的的分钟和 tick 回测，数据目录如下：

| order_book_id | 品种   | 时间段                 | 频率      |
|-----|-----|-----|-----|
| 000001.XSHE   | 股票   | 2018 年全年            | 分钟/tick |
| 002891.XSHE   | 股票   | 2018 年全年            | 分钟/tick |
| 600185.XSHG   | 股票   | 2018 年全年            | 分钟/tick |
| 600000.XSHG   | 股票   | 2018 年全年            | 分钟/tick |
| 000300.XSHG   | 股票   | 2018 年全年            | 分钟/tick |
| IF1606        | 期货   | 该期货上市交易时间段内 | 分钟/tick |
| IF2002        | 期货   | 该期货上市交易时间段内 | 分钟/tick |
| NR2003        | 期货   | 该期货上市交易时间段内 | 分钟/tick |
| AG1612        | 期货   | 该期货上市交易时间段内 | 分钟      |
| AU1612        | 期货   | 该期货上市交易时间段内 | 分钟      |
| IO2002C3900   | 期权   | 该期权上市交易时间段内 | 分钟/tick |
| IO2002P3900   | 期权   | 该期权上市交易时间段内 | 分钟/tick |
| 113010.XSHG   | 可转债 | 2018 年全年            | 分钟/tick |
| 113011.XSHG   | 可转债 | 2018 年全年            | 分钟/tick |

#### 更新数据 {#rqalpha-plus-download-data-update}

您可以通过如下命令增量更新数据包。增量更新时数据来自于 RQDatac，更新数据包会占用您 RQDatac 许可中的连接数和流量。

```shell
rqsdk update-data
```

上述命令可以通过传入参数以控制更新的数据品种，不传入参数时默认更新日线数据，详细的参数说明可通过运行 `rqsdk update-data --help` 查看。

示例，运行如下命令以更新日线、平安银行的分钟线数据、所有螺纹钢期货的分钟线数据和 IO2002C3900 的 tick 数据：

```shell
rqsdk update-data --minbar 000001.XSHE --minbar RB --tick IO2002C3900
```

#### 自定义数据包存储目录 {#rqalpha-plus-download-data-custom}

默认情况下，数据包存储于用户目录下的 .rqalpha-plus/bundle 目录下，您在下载样例数据包和更新数据包时可通过 -d 参数指定自定义的数据包目录。需要注意，若您指定了非默认的数据包目录，需要在运行回测时指定同样的数据包目录。

例如，更新位于 D 盘下的 `user_bundle_path` 文件夹下的数据包

```shell
rqsdk update-data -d D:\\user_bundle_path --minbar 000001.XSHE --minbar RB --tick IO2002C3900
```

## 编写策略 {#rqalpha-plus-write-strategy}

完成数据包的更新后，就可以开始策略的编写了，本节以文档开头出现的 MACD 策略为例演示简单的策略如何设计和编写。

首先需要确定策略主要逻辑，单股票 MACD 策略逻辑如下：

- 明确要交易的目标证券，并在每个交易日计算 [MACD 线](https://zh.wikipedia.org/wiki/指数平滑移动平均线) 和 SIGNAL 线（MACD 线的均线），若 MACD 线突破 SIGNAL 线，则全仓买入目标证券，若 MACD 线跌穿 SIGNAL 线，则清仓。

上文提到，RQAlphaPlus 将交易的整个过程抽象为几段不同的“市场时机”，策略开发者则需要将策略逻辑拆分为对不同“市场时机”的响应，这些时机包括：

- 初始化：一般用于进行策略全局的初始化工作，该阶段不能执行交易逻辑
- 盘前：一般用于执行每日交易前的准备工作，该阶段不能执行交易逻辑
- 行情更新：一般用于执行行情发生变动时的判断及交易逻辑，不同频率级别的策略触发的“时机”有所差异：
  - 日 k 线更新：在日级别的策略中触发，每个交易日触发一次，该阶段可以获取到所有标的当日及之前的日 k 线
  - 分钟 k 线更新：在分钟级别的策略中触发，每分钟触发一次，该阶段可以获取到当前分钟及之前的分钟 k 线
  - tick 更新：tick 级别的策略中触发，需预先“订阅”标的，当订阅的标的 tick 发生更新时触发，若订阅了多个标的则每个合约会分别触发
- 盘后：用于执行每日交易后的逻辑，如清理、计算、记录等，该阶段不能执行交易逻辑

将上文确定的 MACD 策略逻辑进行拆分如下：

- 初始化：明确要交易的目标证券，本例使用平安银行（000001.XSHE）
- 日 k 线更新：
  - 获取过去一段时间日 k 线中的收盘价数据
  - 计算 MACD 和 SIGNAL 线
  - 判断两条均线是否发生了突破或跌穿
  - 若发生了突破或跌穿则执行开仓或清仓逻辑

逻辑已经明确，接下来开始正式编码。

首先是初始化阶段。初始化阶段的逻辑需要写在名为 `init` 的函数中，函数需要接受唯一的参数 `context`：

```python
def init(context):
    pass
```

`context` 变量顾名思义存储的是策略的上下文信息，策略需要在各个“时机”之间传递的变量都可以存储在 `context` 中，另外 `context` 中也提供一些内置的上下文相关的属性，如访问 `context.now` 可以获取到当前“时机”运行的时间。具体到本例，我们将目标证券的代码定义成变量存储在 `context` 中：

```python
def init(context):
    context.stock = "000001.XSHE"
```

接下来是日 k 线更新阶段。该阶段的逻辑需要写在名为 `handle_bar` 的函数中，函数除了接受 `context` 参数外还接受第二个参数 `bar_dict`：

```python
def handle_bar(context, bar_dict):
    pass
```

`bar_dict` 顾名思义就是"dict of bar"，存储 k 线对象的字典。例如访问平安银行当前 k 线的“收盘价”：

```python
bar_dict["000001.XSHE"].close
```

在本例中，单个收盘价是不够的，为了计算均线，我们需要获取近一段时间以来的收盘价序列。最常用的获取历史行情序列的接口是 `history_bars`，该函数接受标的代码、序列长度、k 线频率和价格字段四个参数，例如获取本例中标的证券过去 100 天日 k 线的收盘价序列：

```python
# 四个参数分别为标的代码 context.stock, 100 天, 日线 '1d', 收盘价 'close'
prices = history_bars(context.stock, 100, '1d', 'close')
```

接下来使用获取到的收盘价序列计算均线，MACD 作为常用的技术指标，其计算逻辑不需要我们自己实现，可以直接使用第三方库 [TA-Lib](https://github.com/mrjbq7/ta-lib)。TA-Lib 中的 [MACD 函数](https://hexdocs.pm/talib/0.3.0/TAlib.Indicators.MACD.html) 接受四个参数，分别为价格序列、短周期均线天数、长周期均线天数、SIGNAL 均线天数，返回值有三个，分别为 MACD 线、SIGNAL 线、MACD 和 SIGNAL 线的差值，类型均为 [numpy.array](https://numpy.org/doc/stable/reference/arrays.html)。本例中需要 MACD 和 SIGNAL 线就够了：

```python
import talib

macd, macd_signal, _ = talib.MACD(prices, 12, 26, 9)
```

接下来判断两条均线间的突破和跌穿。所谓 MACD 突破 SIGNAL，即 MACD 的最后一个值大于 SIGNAL 的最后一个值，且 MACD 的倒数第二个值小于 SIGNAL 的倒数第二个值；相反，所谓 MACD 跌穿 SIGNAL，即 MACD 的最后一个值小于 SIGNAL 的最后一个值，且 MACD 的倒数第二个值大于 SIGNAL 的倒数第二个值：

```python
if macd[-1] > macd_signal[-1] and macd[-2] < macd_signal[-2]:
    # MACD 突破 SIGNAL，此时应开仓
    pass

if macd[-1] < macd_signal[-1] and macd[-2] > macd_signal[-2]:
    # MACD 跌穿 SIGNAL，此时应平仓
    pass
```

最后，还剩下开仓和平仓逻辑，对于股票，RQAlphaPlus 提供了六个下单接口，均可以用于开仓或平仓：

- order_shares: 用于按股数下单
- order_lots: 用于按手数下单
- order_value: 用于按价值下单
- order_percent: 用于按价值占当前账户总权益的比例下单
- order_target_value: 用于按目标仓位价值下单
- order_target_percent: 用于按目标仓位价值占账户总权益的比例下单

本例中全仓买入和清仓使用 `order_target_percent` 最为方便，该接口接受两个两个参数，分别为标的代码和目标仓位比例；另有第三个可选参数，为现价单价格，该参数不传表示市价下单。全仓买入和清仓即目标仓位比例为 1 或 0:

```python
# 全仓买入
order_target_percent(context.stock, 1)

# 清仓
order_target_percent(context.stock, 0)
```

另外，为了提升效率及减少因下单失败而出现的 WARNING 日志，可以在清仓前进行判断，仅在当前有仓位时执行清仓。获取当前持仓的接口是 `get_position`，该函数接受标的代码为参数（对于期货等具有空头仓位的标的品种，该函数还接受第二个参数——持仓方向，用于控制查询哪个方向的持仓），返回对应标的品种的持仓对象，持仓对象具有 `.quantity` 属性，其值为持仓股数；

```python
if get_position(context.stock).quantity > 0;
    # 仅当持仓股数大于零时执行清仓操作
    order_target_percent(context.stock, 0)
```

将以上代码集成到一起：

```python
import talib


def init(context):
    context.stock = "000001.XSHE"


def handle_bar(context, bar_dict):
    prices = history_bars(context.stock, 100, '1d', 'close')
    macd, macd_signal, _ = talib.MACD(prices, 12, 26, 9)

    if macd[-1] > macd_signal[-1] and macd[-2] < macd_signal[-2]:
        order_target_percent(context.stock, 1)

    if macd[-1] < macd_signal[-1] and macd[-2] > macd_signal[-2]:
        if get_position(context.stock).quantity > 0:
            order_target_percent(context.stock, 0)
```

注意，将代码中使用到的一些常量定义为全局变量或 `context` 的属性而不是埋没于代码中是一个好习惯，如上述代码中 `talib.MACD` 的后三个参数。可以将上述代码稍作修改：

```python
import talib


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

## 运行策略 {#rqalpha-plus-run-strategy}

RQAlphaPlus 提供了多种入口以供运行策略，本节介绍其中最常用的两种。

#### 使用终端命令运行策略 {#rqalpha-plus-run-strategy-cli}

将上一节编写好的策略写入扩展名为 .py 的文件中，例如 `macd_000001.py`，并在命令行执行如下命令：

```bash
rqalpha-plus run -f macd_000001.py -a stock 100000 -s 20190101 -e 20191231 -bm 000300.XSHG -p
```

敲击 Enter 键之后，RQAlphaPlus 便开始执行，完成后会弹出类似下图的窗口，窗口内包括一些收益风险指标及收益率曲线图：

![运行后弹出的窗口](./img/macd-000001-result.png)

上边的运行命令由几部分组成:

- `rqalpha-plus`：RQAlphaPlus 所有命令行工具的总入口，执行 `rqalpha-plus --help` 以查看所有可用的功能
- `run`: 用于运行策略的子命令，
- 参数：策略运行的各种选项，顺序不限，部分参数需要传入参数值
  - `-f macd_000001.py`：指定运行的策略文件，支持绝对路径或相对路径
  - `-a stock 100000`：指定股票账户的初始资金为十万元，RQAlphaPlus 支持股票（`stock`）、期货（`future`）两种账户，策略交易不同品种的标的需要配置对应账户的初始资金
  - `-s 20190101`：回测运行的初始时间为 2019 年 1 月 1 日，回测实际上会从不早于该日期的第一个交易日开始运行
  - `-e 20191231`：回测运行的终止时间为 2019 年 12 月 31 日，回测实际上会运行至不晚于改日期的最后一个交易日
  - `-bm 000300.XSHG` 使用沪深三百指数（000300.XSHG）作为回测运行的基准，该基准用于计算 Alpha、Beta 等基于超额收益的指标，基准也会和策略收益一起展示在收益曲线图上
  - `-p`：策略运行结束后展示收益曲线图

除这些参数外，您还可以执行 `rqalpha-plus run --help` 以查看运行策略支持传入的更多参数。

#### 使用函数入口运行策略 {#rqalpha-plus-run-strategy-func}

除命令行入口外，RQAlphaPlus 也提供了函数入口以供在其他脚本中调用运行。最常用的是 `run_func` 函数，该函数接受几个关键字参数，分别为存储设置项的字典以及策略实现的约定函数：

```python
config = {
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

if __name__ == "__main__":

    from rqalpha_plus import run_func

    run_func(config=config, init=init, handle_bar=handle_bar)
```

这里传入的 config 与上文中命令行运行所传入的参数功能是相同的。完整的配置列表可查阅 [API 手册](../api/config.md)。

除了上述三个参数外，run_func 还可以接受其他约定函数作为参数，RQAlphaPlus 也另外提供了具有不同功能的其他函数入口，详细信息可查阅 API 手册中 [入口函数](../api/entrypoint.md) 部分。

## 获取结果 {#rqalpha-plus-get-result}

使用 `run_func` 运行策略时，该函数会返回一个字典，这个字典包含了众多策略运行时产生的数据，您可以查看这些数据以了解策略的运行情况，或对策略运行的结果加以分析。

```python
result = run_func(config=config, init=init, handle_bar=handle_bar)
```

如获取策略的指标汇总

```python
result['sys_analyser']["summary"]

# Out:
# {'strategy_name': 'strategy',
#  'start_date': '2019-01-02',
#  'end_date': '2019-12-31',
#  'strategy_file': 'strategy.py',
#  'run_type': 'BACKTEST',
#  'STOCK': 100000.0,
#  'alpha': 0.22,
#  'beta': 0.605,
#  'sharpe': 1.813,
#  'information_ratio': 0.468,
#  'downside_risk': 0.135,
#  'tracking_error': 0.206,
#  'sortino': 0.191,
#  'volatility': 0.226,
#  'max_drawdown': 0.148,
#  'total_value': 148613.493,
#  'cash': 563.493,
#  'total_returns': 0.486,
#  'annualized_returns': 0.506,
#  'unit_net_value': 1.486,
#  'units': 100000.0,
#  'benchmark_total_returns': 0.361,
#  'benchmark_annualized_returns': 0.375}
```

`result['sys_analyser']` 字典中另外有交易流水、每日的账户、持仓等信息：

| key             | value 格式 | 说明                                       |
|-----|-----|-----|
| summary         | dict       | 回测的收益和风险指标汇总                   |
| trades          | DataFrame  | 交易流水                                   |
| portfolio       | DataFrame  | 投资组合中每日现金、权益、市值、净值等数据 |
| stock_account   | DataFrame  | 股票账户每日现金、权益、市值等数据         |
| stock_positions | DataFrame  | 股票账户下的每日持仓情况                   |

使用命令行运行策略的情况下，因为无法直接获取到上述返回值，您可以通过传入参数的方式要求 RQAlphaPlus 将回测结果写入文件。

## 保存回测结果 {#quick-start-save-result}

在 RQAlphaPlus 回测中，加入以下参数至启动命令中，可以将回测结果写入文件。

- `-o result.pkl`：用于将回测结果以 pickle 形式存储至 pickle 文件，该 pickle 文件与 `run_func` 返回的字典内容相同
- `--report report`： 用于将回测结果以 csv 报告的形式输出至 report 目录，这些文件内容与 `run_func` 返回的结果相同，只是使用了更便于直接查看和分析的格式呈现：

| 文件名              | 说明                                       |
|-----|-----|
| report.xlsx         | 所有以下文件的汇总 excel 表                |
| summary.csv         | 回测的收益和风险指标                       |
| portfolio.csv       | 投资组合中每日现金、权益、市值、净值等数据 |
| stock_account.csv   | 股票账户每日现金、权益、市值等数据         |
| stock_positions.csv | 股票账户下的每日持仓情况                   |
| trades.csv          | 交易流水                                   |

```python
rqalpha-plus run -f macd_000001.py -a stock 100000 -s 20190101 -e 20191231 -p  -bm 000300.XSHG -o result.pkl --report report
```

使用 pandas 读取回测报告为 DataFrame 对象的示例：

```python
import pandas as pd
import os

portfolio_df = pd.read_csv(os.path.join("report", "portfolio.csv"), encoding="GBK")
stock_account_df = pd.read_csv(os.path.join("report", "stock_account.csv"), encoding="GBK")
stock_positions_df = pd.read_csv(os.path.join("report", "stock_positions.csv"), encoding="GBK")
summary_df = pd.read_csv(os.path.join("report", "summary.csv"), encoding="GBK")
trades_df = pd.read_csv(os.path.join("report", "trades.csv"), encoding="GBK")
print(trades_df)

#               datetime  commission  ...     trading_datetime  transaction_cost
# 0  2018-01-02 09:31:00    798.5184  ...  2018-01-02 09:31:00          798.5184
```

使用 pickle，读取回测结果文件 result.pkl 的示例：

```python
import pickle
with open("result.pkl", "rb") as f:
        result = pickle.load(f)

result.keys()
# Out[ ]: dict_keys(['trades', 'summary', 'benchmark_portfolio', 'portfolio', 'stock_positions', 'stock_account'])

result['trades']
# Out[ ]:
#                      commission  ...  transaction_cost
# datetime                         ...
# 2019-01-02 15:00:00     79.4016  ...           79.4016

```
