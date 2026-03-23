## 快速上手 {#rqsdk-get-started}

### 如何安装 Ricequant SDK {#rqsdk-installation}

#### 准备

- Ricequant SDK 需要 64-bit，Python3.6+运行环境。如果您目前没有 Python 环境，或者已有的环境版本过低，请参考下面的说明来准备 Python 环境。
- Ricequant SDK 需要商业授权才能使用。请在安装前准备好米筐发放的许可证文件（通常会以邮件的形式发放），或联系销售获取授权。如果您想先试用本产品，可以点击[这里](https://www.ricequant.com/welcome/trial/rqsdk-cloud)申请试用 RQSDK 产品。

#### 安装 Python 环境

Ricequant SDK 支持的 python 版本及系统环境如下表：

|             |  Linux  | Windows |            Mac(Apple Silicon)            |                Mac(Intel)                |
| ----------- | :-----: | :-----: | :--------------------------------------: | :--------------------------------------: |
| python 3.7  | &check; | &check; | <span style="color: red;">&cross;</span> |                 &check;                  |
| python 3.8  | &check; | &check; |                 &check;                  |                 &check;                  |
| python 3.9  | &check; | &check; |                 &check;                  |                 &check;                  |
| python 3.10 | &check; | &check; |                 &check;                  |                 &check;                  |
| python 3.11 | &check; | &check; |                 &check;                  |                 &check;                  |
| python 3.12 | &check; | &check; |                 &check;                  |                 &check;                  |
| python 3.13 | &check; | &check; |                 &check;                  | <span style="color: red;">&cross;</span> |

由于 Python 原生的安装和配置相对比较复杂，我们建议使用[Anaconda](https://www.anaconda.com/)进行安装及配置，安装使用教程可参考[安装 Anaconda 虚拟环境（强烈建议）](#rqsdk-conda-isntall)。

#### 安装 Ricequant SDK {#install-rqsdk}

**_有关如何在 Mac M1 平台上安装 RQSDK，请点击[常见问题](#install-rqsdk-on-m1)_**

在开始之前我们假设您已经自行或按照上述步骤装好了 Python，并激活了您希望进行量化策略开发的虚拟环境。

Ricequant SDK 的安装非常简单，您只需在激活了虚拟环境的命令行终端内输入下面的命令即可安装（或复制下面的命令再黏贴进命令行——Windows 的 cmd 终端用鼠标右键点击黑色区域任意位置来黏贴）：

```
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple rqsdk
```

整个安装过程持续约 5 分钟（取决于机器配置和网络状况）。如果您在 Windows 下的 cmd 窗口运行上述命令，请在安装程序运行的时候不要用鼠标点击 cmd 窗口内，这样会导致程序运行暂停。如果不慎点击了，可以按一次`回车键`来继续运行程序。

安装完毕后直接在窗口中输入`rqsdk`命令，如果安装成功会输出下列内容：

![image-20200521143547497](./img/rqsdk-install-done.png)

#### 配置代理 {#rqsdk-proxy}

如果您所在的环境需要通过代理访问外网（如不需要可跳过此步骤，进行下一步骤配置许可证信息），rqsdk 可通过如下命令配置或更新代理：

```
rqsdk proxy
```

该命令是交互式的，您只需要根据命令提示填入所需信息即可。配置完毕后可以调用`rqsdk proxy info`来查看刚配置的许可证信息。

#### 配置许可证信息 {#rqsdk-license}

在您申请试用或者正式采购 Ricequant SDK 之后，米筐会将含有许可证信息的邮件发送到您提供的邮箱中。许可证信息是一串看起来像“乱码”的文字：

```
5tyGjIiAWfs6azz40Ad9TOc1E8SFjwmp0zoHD0Leg4ZfzHsDJEsYmBgoOAyQxfmMDILeSyMPA2yoO1xN99PsLLhlHATh/5nupsahbzK4MO8wwL/PmZwhOF;fkOUGrPWQFkuguZUv3wid37Gf3hm1T9WRPS61BhFBPbcLOq4pCQw=IViSI2J51NV3IhUcHJ4f9l7YtSP6o6ziClTRgiGxoM]kI2IvlqBCh1AZKuqi7wafRoa0ZHzmNZ05SOx+a6sS8x/ihvOT+iYnvokDx7/6Zaz9VePmdIa35OB3v3+Hl+N4q8UmbQrgv/sG3mUPfFRaWP0jDuSUanuU5mPWfmwfkX4=
```

如果您曾经安装过 Ricequant SDK，可以通过`rqsdk license info`命令来查看许可证信息。

无论您是否已经配置过许可证，都可以通过下列命令来更新到最新的许可证：

```
rqsdk license
```

该命令是交互式的，您只需要根据命令提示填入所需信息即可。配置完毕后可以调用`rqsdk license info`来查看刚配置的许可证信息。

#### 安装产品

在安装完`rqsdk`及配置许可证之后，您需要根据自己的需要选择安装 Ricequant SDK 中包含的产品。如果您只需要 RQData——金融数据 API 的功能，那么您已经完成了所有的安装和配置步骤，请参考 RQData 的文档来进行下一步工作。

如果您的许可证信息在使用过程中有所变化（例如原本仅有 RQData 的权限，后来添加了回测功能）或希望使用其他功能，则需要通过下面的方法来安装其他产品组件。

目前 Ricequant SDK 中可选的产品如下表：

| 安装代码     | 产品名       | 组件用途及依赖                                   |
| ------------ | ------------ | ------------------------------------------------ |
| rqdatac      | RQData       | 金融数据 API，所有组件的基础依赖，**默认已安装** |
| rqoptimizer  | RQOptimizer  | 股票优化器，依赖 rqdatac                         |
| rqfactor     | RQFactor     | 因子投研工具，依赖 rqdatac                       |
| rqalpha_plus | RQAlpha Plus | 回测引擎，依赖 rqoptimizer 及 rqfactor           |

Ricequant SDK 支持通过下列命令安装特定产品：

```
rqsdk install <安装代码>
```

例如安装 RQAlpha Plus，命令为`rqsdk install rqalpha_plus`。

_注意：在安装某个产品时，如果上表中已说明组件依赖关系，则其所依赖的组建都会被同时安装上。例如运行了上述的命令安装了 RQAlpha Plus，那么 RQFactor 和 RQOptimizer 也会同时被装上。_

#### 更新 Ricequant SDK 的版本 {#rqsdk-update}

米筐会不定期更新 Ricequant SDK 的版本以修复问题和增加功能，每次版本升级后会通过邮件告知更新的内容列表。当您决定要更新的时候，只需要在安装了 RQSDK 的虚拟环境中运行下列命令即可更新到最新版：

```
rqsdk update
```

以上`rqsdk update`命令会更新 rqsdk 及本地安装的各产品的版本，如有更新特定产品需求，可通过`rqsdk update --help` 获取该命令的完整用法。

**_特别注意：在执行该命令时请确保所有运行中的 Python 程序都已停止，例如 IPython Notebook、您自己写的 Python 应用等，否则很可能会报“无写权限”而升级失败。_**

### 准备进行一次回测 {#rqsdk-prep-backtest}

Ricequant SDK 的回测功能由**RQAlpha Plus**提供，而回测所需的数据——除了您自己的数据之外——则由**RQData**提供。

RQAlpha Plus 回测依赖于历史行情数据，而这些数据需要预先被缓存到本地（股票、期货回测及各类品种的 tick 回测）。因此在进行回测之前，首先需要准备好历史行情数据。

取决于您期望进行研究的标的数量和回测频次，历史行情数据量可能会非常庞大。如果直接通过网络下载可能会耗时非常久，并且很可能会突破您账号的每日流量限制。如果您已经正式采购 Ricequant SDK，可以联系米筐销售为您提供线下的行情数据拷贝服务。

我们先用一个简单的例子（大约会消耗 500MB 的流量）来演示一下使用 Ricequant SDK 做回测的简便性。

#### 准备回测所需数据

**_尊敬的试用客户：我们为您准备了每日 1G 的流量配额，--base如果全部下载流量消耗将近1G（建议先用[不消耗计费流量](#rqsdk-doc-trial)下载一部分数据，再运行--base增量更新），按照前文描述的 1G 流量消耗是可以满足日度数据日常增量更新的。同时，我们专门为试用账户准备了[不消耗计费流量](#rqsdk-doc-trial)的初始化方式_**。

在开始之前，请确保已通过`conda activate 环境名`命令切换到已经装好 Ricequant SDK 的虚拟环境。

通过网络的方式初始化数据缓存只需要运行如下命令：

```
rqsdk update-data --base --minbar 000001.XSHE
```

该命令在运行中将产生如下图所示的动态输出：

![image-20200426095701719](./img/get-started-update-data-1.png)

命令运行完毕后如下，注意会有两行进度条：

![image-20200426102332653](./img/get-started-update-data-2.png)

该命令的目的是更新所有日线及基础数据，并且更新代号为`000001.XSHE（平安银行）`的分钟线行情数据。这样您就可以针对所有的股票和期货做日线回测，而仅对`平安银行`做分钟线回测。
_注意_：

- _如果您对需要做分钟线、tick 回测的合约有更复杂的需求，请运行`rqsdk update-data`获得该命令的完整用法。_
- _更新数据过程中，请不要运行回测，避免出现同时读写数据的情况._

##### 试用客户初始化缓存的方式 {#rqsdk-doc-trial}

我们为试用客户专门准备了不消耗计费流量的数据初始化方式，避免因为要下载 500MB 的数据而耗尽每日流量配额。在完成前面的安装过程后，您只需要运行下列命令：

```
rqsdk download-data --sample
```

该命令将下载米筐准备的样例数据，不消耗 rqdatac 的每日流量配额，它会为您准备好真实的日级别历史行情数据、合约列表数据、分红拆分数据等回测所需的基础数据。之后如果您再运行`rqsdk update-data`或该命令的其他参数形式（如前文提到的`rqsdk update-data --minbar 000001.XSHE --base`，则对于已下载的部分只会进行增量更新，并不会消耗大量流量。

_注意：在调取本节所描述的数据相关命令时，因为只有 RQAlpha Plus 的回测功能依赖本地数据包，因此系统会自动检查是否已经安装了该产品，如无安装则会提示安装。_

#### 准备回测所需策略代码

在上述命令执行完毕后，将会在`<用户目录>\.rqalpha-plus\bundle`目录下创建历史行情数据的缓存文件。

_这是 Ricequant SDK 管理缓存文件的默认目录，您可以通过参数`-d <完整路径>`进行定制化。在回测时同样可以指定`-d`参数来更改 RQAlpha Plus 读取回测历史文件的位置。_

接下来您需要准备一个策略来进行回测。策略是交易决策逻辑的载体，用 Python 代码来体现。您只需要在策略中实现由 RQAlpha Plus 指定的回调函数即可 (详细用法请参考[策略引擎 API 文档](/quant/))。

但是现在并不需要急着去研究策略引擎的细节，我们已经为您准备好了几个直接能运行的策略。请您用`cd`命令切换到您希望放置样例策略的目录，然后运行下面的命令：

```
rqalpha-plus examples
```

该命令会在当前目录下创建一个名为 exmaples 的目录，其内容如下图所示：

![image-20200427152039598](./img/get-started-bt-example-1.png)

您可以用惯用的 IDE 或者编辑器打开这些 Python 源码文件来查看代码，这里列举了一些常用的策略写法，以便您快速上手策略编写的 API。

我们现在以`buy_and_hold.py`策略为例，简单讲解一下策略的几个构成部分。当然您也完全可以跳过下面的代码讲解，直接到下一个环节，先看一下回测引擎能对策略做哪些分析，输出了哪些数据。

```python
# 顾名思义，这是一个“买入并持有”的简单策略。在这个策略里，我们将在策略开始时买入平安银行，并持有到策略结束。

# 首先策略引入了RQAlpha的框架依赖，这是所有策略必须具备的。
from rqalpha.api import *

# 在这个方法中编写任何的初始化逻辑。context对象是由引擎构建并传入的，这个对象内涵了关于整个策略的信息，
# 这个对象也会出现在其他回调中，使用同一个实例。
def init(context):
    # 在这里定义了一个类似“全局变量”的变量。因为这个context对象实例会出现在别的回调中，因此在别的函数中
    # 也可以引用context.s1这个变量
    context.s1 = "000001.XSHE"

    # 告诉引擎该策略的股票池包含了什么股票，在这里股票池只有“平安银行”一个，您还可以传入一个列表或一个
    # 指数代码
    update_universe(context.s1)

    # 创建一个变量，用来判断是否已经执行过买入操作。因为行情会不断触发回调，因此需要策略自行判断是否
    # 已经买入过，而不是在每一次行情触发时都执行买入
    context.fired = False

    # 日志会直接打印在命令行（标准输出）中，您可以通过将输出流转发到文件的方式将日志保存下来。
    logger.info("RunInfo: {}".format(context.run_info))


# 这个回调模拟的是每个交易日开盘前希望执行的一些操作，例如对昨天收盘后的情况做一些处理来指导今天的交易，
# 但是在我们这个很简单的策略中并不需要这一回调，可以略过。
def before_trading(context):
    pass


# 这是前面提到的行情处理回调，也是整个策略的核心部分。行情是以K线的方式传入的，每当策略收到一个新的行情
# （在回测的情况下，就是下一个时间单位的K线准备好）时，这个函数就会被触发一次。
# 除了context变量之外，bar_dict就是含有行情信息的一个字典结构，它的key是合约代码，值是引擎内定义的
# Bar结构，包含了常见的开盘价、收盘价、最高最低价等信息，具体含义可以参考下面的链接：
# https://www.ricequant.com/doc/api/python/chn#object-bar
def handle_bar(context, bar_dict):

    # 这里就是策略逻辑的主体了。
    # 我们先判断买入的逻辑是否已经触发过，如果没有触发过，说明是第一次收到行情，那么就进行买入
    # 如果已经触发过，则什么也不做。
    if not context.fired:
        # order_percent并且传入1代表买入该股票并且使其占有投资组合的100%
        logger.info("order_percent:{}".format(order_percent(context.s1, 1)))

        # 注意将代表是否买入过的变量设为True，确保只执行一次买入操作
        context.fired = True


# 类似前面的before_trading，这个回调函数模拟了每个交易日收盘后需要进行的一些处理。
# 在这个策略中并不需要做任何处理，因此直接略过了。
def after_trading(context):
    pass

```

#### 运行回测！

到这里，您已经准备好了运行回测所需的所有条件，可以准备运行回测了。我们仍然以前面提到的`buy_and_hold.py`——一个简单的买入并持有策略为例。

运行回测之前，您需要想好几个参数：

- 策略从那一天开始：起始时间
- 策略运行到那一天为止：结束时间
- 策略所使用的最大资金量是多少：账户资金
- 策略以什么频率进行回测：日线、分钟线或 tick

现在我们假设以**分钟线**频率，从**2018 年 1 月 1 日**开始到**2018 年 12 月 31 日**为止（引擎会自动按各个交易所公示的交易日期针对不同交易品种跳过非交易日，您只需要按您所想的日期指定即可，不必考虑节假日或周末的情况），账户资金**10 万元**。那么执行下列命令即可：

```
rqalpha-plus run -f examples/buy_and_hold.py -s 2018-01-01 -e 2018-12-31 -fq 1m --plot --account stock 100000
```

由于在上述策略运行命令中输入了`--plot`命令，因此在策略执行完毕后会弹出策略执行结果的图片，展示策略运行情况。如果您希望获得更多的策略运行结果以备分析，可以使用`--report`和`-o`命令来分别输出`csv`格式的报告和`pickle`格式的 Python 内存序列化文件。更多的配置参数可以通过下列命令查看：

```
rqalpha-plus run --help
```

您将会看到非常多的可配置项。随着使用的逐渐深入，这些配置项都会成为您的得力工具。

### 上手总结 {#rqsdk-get-started-summary}

至此您已经完成了所有 RQSDK 的配置流程，并运行了一个策略。这里总结一下几个关键的命令，假设您已经配置了满足条件的 Python 环境，其实安装 Ricequant SDK 是非常简单的。

从网络安装 Ricequant SDK：

```
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple rqsdk
```

下载试用数据：

```
rqsdk download-data --sample
```

下载生产数据：

```
rqsdk update-data --minbar 000001.XSHE
```

生成回测样例：

```
rqalpha-plus examples
```

以分钟线频率运行回测样例：

```
rqalpha-plus run -f examples/buy_and_hold.py -s 2018-01-01 -e 2018-12-31 -fq 1m --plot --account stock 100000
```

接下来我们会更详细地带您了解 Ricequant SDK 的每一个细节。我们建议您按照前面的内容先行配置好环境，后面的讲解将不再赘述环境的配置、数据的更新等内容。

## Ricequant SDK 文档路径 {#rqsdk-doc-index}

Ricequant SDK 由四个主要部件组成，分别为：

- 负责提供和管理金融数据的 RQData；
- 作为回测引擎的 RQAlpha Plus；
- 承担了因子投研的 RQFactor；
- 可进行股票组合优化的优化器 RQOptimizer。

四个组件既各司其职又紧密配合，共同提供了流畅、完整的本地量化开发体验。

| 产品                           | 资源                                                                    |
| ------------------------------ | ----------------------------------------------------------------------- |
| RQData - 金融数据 API          | [使用说明](../rqdata/python/index-rqdatac)                              |
| RQAlpha Plus - 策略回测引擎    | [使用教程](../rqalpha-plus/doc/index-rqalphaplus#rqalpha-plus-guide) \| |
| RQFactor - 因子编写及检验      | [使用教程](../rqfactor/manual/index-rqfactor) \|                        |
| RQOptimizer - 股票多因子优化器 | [使用说明](../rqoptimize/doc/index-rqoptimize) \|                       |

## 安装 Anaconda 虚拟环境（强烈建议） {#rqsdk-conda-isntall}

完整版的 Anaconda 对于大多数人来说都是没有必要的，因此 Anaconda 官方提供了精简版的 Miniconda，只安装最核心的工具包。本文档将以 Miniconda 的安装为例。如果您希望安装 Anaconda 本体，请移步至[Anaconda 官网](https://www.anaconda.com/distribution)获得安装指引。下面简要列出 Miniconda 的安装步骤（**注意：本章所述的功能只适用于大多数用户。如果您已对 Anaconda 非常熟悉，或者已有惯用的环境，完全可以不按本章节所述方法配置环境**）：

#### 下载 Miniconda

- 如果您身处国内，请在[清华大学的 Miniconda 镜像仓库](https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/)中寻找适用于您系统的安装包，或直接
  - Windows 系统：[点击下载](https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-latest-Windows-x86_64.exe)
  - MacOS 系统
    - X86 版：[点击下载](https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-latest-MacOSX-x86_64.pkg)
    - ARM 版：[点击下载](https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-latest-MacOSX-arm64.sh)
  - Linux 系统：[点击下载](https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-latest-Linux-x86_64.sh)
- 如果您身处海外，可以直接去[官方网站](https://docs.conda.io/en/latest/miniconda.html)下载对应您系统的安装包

#### 安装 Miniconda

在各个系统中安装 Miniconda 的体验与安装其他软件无异，但是在安装过程中有一个需要留意的配置点：

**添加命令到环境变量**

![img](./img/miniconda-install-add-env.png)

**如果在安装过程中错过了环境变量的选项，可以按如下步骤手工添加**

假设您的 Miniconda 安装位置为`D:\ProgramData\Miniconda3`（默认安装位置是`C:\Users\<用户目录>\miniconda3`，或`C:\ProgramData\Miniconda3`，可在安装过程中手工更改）。

将下列值逐个添加到`Path`环境变量中（注意在实际操作的时候依据您的实际安装情况来更改目录）：

```
D:\ProgramData\Miniconda3\Scripts
D:\ProgramData\Miniconda3\Library\bin
D:\ProgramData\Miniconda3\Library\usr\bin
D:\ProgramData\Miniconda3\Library\mingw-w64\bin
D:\ProgramData\Miniconda3
```

添加方法如下：

- 在 Windows 搜索框中搜索`环境变量`或`env`，系统会给出最佳匹配项
  ![image-20200422101051261](./img/miniconda-install-edit-env.png)
- 打开配置面板后点击`环境变量`按钮
  ![image-20200422101303208](./img/miniconda-install-edit-env-1.png)
- 在打开的对话框中找到`Path`列，双击或选中后点击`编辑`按钮
  ![image-20200422101619641](./img/miniconda-install-edit-env-2.png)
- 在打开的对话框中点击`新建`按钮，依次将本节开头的五个路径添加进去，**_注意根据自己实际安装的配置改变路径，不要直接复制黏贴_**。配置完成后将会看到如下图所示状态：
  ![image-20200422101941085](./img/miniconda-install-edit-env-3.png)

* 配置完成后打开一个命令行窗口，输入`conda`回车，如果您看到类似下图的结果，说明配置生效。后续的使用中如果碰到类似`No such file or directory`之类关于文件、路径未找到的错误时，可以再次检查一下是否本节描述的五个值都设置正确。
  ![image-20200422102747374](./img/miniconda-install-edit-env-4.png)

#### 创建及切换 Python 虚拟环境 {#create-virtual-env}

安装好 Miniconda 并配置好环境变量之后，您就可以使用`conda`命令方便地进行虚拟环境的配置和管理了。

> Python 虚拟环境是 Python 提供的一种依赖管理方式，它允许您在同一台电脑上使用不同版本的 Python、不同版本的依赖来开发不同的程序。环境之间互相独立，互不干涉，还可以随意切换。

用下列命令创建一个名为`rqsdk`的 Python 3.9 环境：

```
conda create -n rqsdk python=3.9
```

创建完毕后还需要用`conda activate rqsdk`来激活刚才创建的环境，这样之后的操作（例如调用`pip install`等）就都只会影响这个虚拟环境了。

如果要退出虚拟环境，可以直接在环境激活的状态下运行`conda deactivate`命令。

本节仅以 Windows 10 系统为例，更多关于如何使用 conda 命令管理虚拟环境的内容可以参考[conda 官方文档——环境管理](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)章节。

#### 升级 Python 环境

如果您已有的环境是低于 Python 3.6 的，请根据您的实际情况升级到 Python 3.6 或以上（推荐升级到最新的 Python 3.9）。我们要求 64-bit 的 Python 环境，如果您的环境是 32-bit 的，请重新安装 64-bit 的环境。

如果您已有环境是 Anaconda 或 Miniconda，可以先用`conda update conda`命令更新 conda 工具本身，然后再通过`conda activate <env name>`激活您的 Python 虚拟环境，然后运行`conda install python=3.9`来安装最新的 Python 到该虚拟环境。

#### 中国境内安装加速方案

pip 默认下载源服务器在国外，从中国境内访问速度会比较慢。推荐在全局范围内更改默认 pip 下载源到国内的清华镜像，将会对安装配置速度有非常明显的提升，**感谢清华为中国的 Python 发展做出的贡献**。

在命令行中运行如下命令可以轻松配置：

```
conda activate base
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

#### conda 基本操作

- 查看版本信息 `conda --version`
- 更新 conda `conda update conda`
- 创建一个虚拟环境 `conda create -n rqsdk python=3.9`
- 激活新的虚拟环境 `conda activate rqsdk`
- 列出环境信息 `conda env list`
- 退出当前环境 `conda deactivate`
- 删除虚拟环境`conda remove --name rqsdk --all`

#### 在 Powershell 中使用 conda 命令

如果您习惯于 Windows 的 Powershell 环境，则在默认的安装状态下，conda 并不能支持，还需要进行以下步骤。

**查看您的 conda 版本**

通过`conda --version`查看您当前的 conda 版本，分两种情况：

- 版本号大于等于 4.6
  - 用管理员权限运行 Powershell
  - 执行命令`conda init powershell`
- 版本号小于 4.6
  - 用管理员权限运行 Powershell
  - 输入命令`conda install -n root -c pscondaenvs pscondaenvs`安装[PSCondaEnvs](https://github.com/BCSharp/PSCondaEnvs)包。**这里注意正确的命令中确实包含了两个`pscondaenvs`，并不是文档写错了**。
  - 输入命令`Set-ExecutionPolicy RemoteSigned`，随后输入`Y`并回车，以更改 Powershell 安全策略
  - 在 Powershell 中激活和退出环境的命令分别为`activate rqsdk`和`deactivate`，而不是`conda activate rqsdk`和`conda deactivate`。

_如果对 Conda 环境没有特殊要求的话，建议直接通过`conda update conda`命令升级到最新版本_

## PyCharm 及 vsCode 快速配置 {#rqsdk-doc-index-config}

### PyCharm {#rqsdk-pycharm}

#### 为什么要用 PyCharm？

- PyCharm 作为 IDE（集成开发环境），自带 python 解释器和虚拟环境管理功能，开箱即用。
- PyCharm 默认的内置功能极为丰富（Git、数据库支持、框架支持等），无需手动配置插件便可直接使用。
- PyCharm 内置了在业界无出其右的静态代码审查（code inspect）功能。

#### PyCharm 下载

[PyCharm 官网](https://www.jetbrains.com/pycharm/)提供了专业版和社区版下载。

- 专业版用于科学计算和 Web 开发。同时具有 HTML、JS 和 SQL 等支持。专业版 PyCharm 支持试用 30 天。
- 社区版用于通常的 Python 开发。免费且开源。

#### 创建 PyCharm 工程（Project）

下载且安装完成 PyCharm 后，便可打开 Pycharm 后建立一个项目（Project）。
建立项目时，可以设置项目使用的 Python 解释器/虚拟环境。_后续开发中的代码提示、调试等功能都依赖项目配置的虚拟环境_

1. 点击 Create New Project 按钮
2. 展开 Project interpreter
3. 选择虚拟环境（若没有已存在环境，则 PyCharm 会自动创建）
4. 点击 Create 按钮，创建项目

![建立一个项目](./img/rqsdk-create-project-1.png)

_如果没有 python 环境 ，编辑器右下角会有进度条提示 python 的安装进度。_

> 工程创建完成后，亦可在设置中修改当前工程使用的虚拟环境：
>
> 1. 点击左上角菜单栏 FIle -> Settings（macOS 中为 PyCharm -> Preference）
> 2. 点击 Project: \*\*\*\* -> Project Interpreter
> 3. 点击右边小齿轮 -> Show All
> 4. 点击加号（+） -> 选择虚拟环境（Virtualenv Environment) 或者 Conda 环境（Conda Environment) `

![配置python环境](./img/rqsdk-create-project-2.png)

#### 在 PyCharm 中安装 RQSDK

若当前工程配置的虚拟环境中还未安装 RQSDK，可以直接在 PyCharm 中调用终端（terminal）安装，PyCharm 会自动在改终端激活先前配置好的虚拟环境。
若点击左下角 Terminal 以激活终端，输入以下代码以安装 RQSDK

    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple rqsdk

#### 使用 PyCharm 编写代码

- 创建 Python 模块（module）`鼠标右键项目文件夹 -> New -> Python File -> 输入文件名`
  ![](./img/rqsdk-create-project-3.png)

- 若当前工程正确配置了虚拟环境，且虚拟环境中安装了 RQSDK，在 py 文件中输入“import rq”时便可以看到 PyCharm 给出的代码提示
  ![image.png](./img/rqsdk-create-project-4.png)

- 在 py 文件中输入下列代码，使用 RQDatac 调取日线数据：

  ```python
  import rqdatac

  rqdatac.init()
  print(rqdatac.get_price("000001.XSHE"))
  ```

- 在编辑区域点击右键执行 Run... 便可以运行当前代码。
  注意，上述代码的运行要求事先使用 [`rqsdk license`](#rqsdk-license)命令配置好 license。

![](./img/rqsdk-pycahrm-run-1.png)

> 当运行 `rqsdk install rqalpha_plus` 命令后，当前 python 环境也会有 rqoptimizer 和 rqfactor

#### 使用 PyCharm 运行回测

回测在终端中需要通过 rqalpha-plus 命令而非 python 命令运行，故在 PyCharm 中运行回测需要进行一些额外的配置，以简单的 buy-and-hold 回测策略为例。

1. 创建名为 buy_and_hold.py 的 python 文件并键入以下代码：

   ```python
   # buy_and_hold.py

   def init(context):
       context.s = "000001.XSHE"
       context.fired = False

   def handle_bar(context, bar_dict):
       if not context.fired:
           order_shares(context.s, 1000)
           context.fired = True
   ```

2. 点击右上角的 `Add Configuration`

![打开配置启动参数窗口](./img/rqsdk-pycahrm-run-2.png)

3. 在打开的窗口中将第一项左侧默认的运行方式由 `Script path` 修改为 `Module name`
4. 设置 `Module name` 为 `rqalpha_plus`，设置 `Parameters` 为回测运行的子命令 `run` 及其参数，如：

   ```shell
   run -f buy_and_hold.py -s 20190101 -e 20191231 -a stock 20000 --plot
   ```

![配置启动命令](./img/rqsdk-pycahrm-run-3.png)

5. 点击 OK 按钮以完成配置
6. 点击右上角的三角形按钮以运行回测，或点击虫子按钮以调试（debug）代码

![运行策略](./img/rqsdk-pycahrm-run-4.png)

### Visual Studio Code (VS Code) {#rqsdk-vs-code}

#### 为什么要用 VS Code？

1. 轻量化，下载安装更快；资源占用低，对配置相对不足的计算机更友好。
2. 启动快速，首次创建工程时没有漫长等待创建索引的过程。
3. 生态健全，有着丰富的第三方主题和插件。

在[Visual Studio Code](https://code.visualstudio.com/)官网可以下载标准版。

#### 安装 Python 插件（Extensions）

VScode 不是 python 专用的编辑器，故使用其开发 python 需要安装专门的插件支持才能获得代码提示、审查、调试等功能：

- 在左侧栏点击 Extensions 后，搜索 python，选择搜索到的第一项并点击 `install` 按钮安装。

![image.png](./img/rqsdk-vs-code-1.png)

#### 设置虚拟环境/Python 解释器

- 使用 Ctrl+Shift+P 快捷键（macOS 为 Command+Shift+P）打开 command palette 窗口
- 输入关键字 `python select` 并找到 `Python: Select Interpreter` 一项， 点击该项并在随后弹出的 Python 解释器列表中选择目标虚拟环境中的解释器（若目标虚拟环境未列出，则需要手工输入解释器的路径）

#### 使用 VS Code 编写代码

- 在 VS Code 中点击打开一个系统文件夹，使用 vs code 会在此文件夹中生成配置文件。
- 在打开的文件夹中创建新的 python 文件，文件名`demo_rqdatac.py`

![打开文件夹](./img/rqsdk-vs-code-2.png)

![创建py文件](./img/rqsdk-vs-code-3.png))

![VS code 代码补全功能](./img/rqsdk-vs-code-4.png)

- 使用 rqdatac 查看平安银行日线数据

文件中输入以下代码：

```
import rqdatac

rqdatac.init()
print(rqdatac.get_price("000001.XSHE"))
```

![vs code demo](./img/rqsdk-vs-code-5.png)

#### 用 debug 方式运行回测

首先需配置 pyhton 解释器。

![选择python解释器 1](./img/rqsdk-vs-code-6.png)

![选择python解释器 2](./img/rqsdk-vs-code-7.png)

启动 rqalpha debug 模式 需要在 vs code 的配置文件中配置 debug 参数。
debug 配置文件在 .vscode 文件夹下 launch.json 文件中。
需要加入如下代码:

```json
{
  // 使用 IntelliSense 了解相关属性。
  // 悬停以查看现有属性的描述。
  // 欲了解更多信息，请访问: https://go.microsoft.com/fwlink/?linkid=830387
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: 模块",
      "type": "python",
      "request": "launch",
      "module": "rqalpha-plus",
      "args": [
        "run",
        "-f",
        "examples\\buy_and_hold.py",
        "-s",
        "2018-01-01",
        "-e",
        "2018-05-31",
        "-fq",
        "1m",
        "--plot",
        "--account",
        "stock",
        "1000000"
      ]
    }
  ]
}
```

配置完成后，即可在需要的文件上打上断点，然后 debug 运行。

![debug 运行buy_and_hold.py 1](./img/rqsdk-vs-code-8.png)

![debug 运行buy_and_hold.py 2](./img/rqsdk-vs-code-9.png)

## AI 编程工具配置指南 {#rqsdk-ai-tools}

Ricequant SDK 提供了完整的文档索引文件[Document-index](https://www.ricequant.com/doc/document-index.txt)，您可以使用现代 AI 编程工具来更好地利用这个索引文件，提升开发效率。

### 工具选择指南

| 工具                  | 特点                                              | 适用场景                         |
| --------------------- | ------------------------------------------------- | -------------------------------- |
| **Claude Code**       | 命令行 AI 助手，深度集成开发环境                  | 快速查询文档、生成配置、调试问题 |
| **Cursor**            | AI 驱动的代码编辑器，智能代码补全                 | 策略开发、代码重构、API 探索     |
| **VS Code + Copilot** | 成熟的编辑器 + AI 助手，生态丰富                  | 团队协作、大型项目、多语言开发   |
| **Cline**             | 开源插件，支持多模型切换及自定义MCP工具创建       | 高度集成、脚本生成、自动化任务   |
| **Trae**              | 免费AI IDE，支持MCP，覆盖浏览器自动化、数据库管理 | 代码生成、性能优化、上手快速     |

### Claude Code 配置

#### 1. 创建自定义命令

在项目根目录创建 `.claude\commands\ricequant-doc-index.md` 文件,将[Document-index](https://www.ricequant.com/doc/document-index.txt) 的内容复制进去（这里目录名也可以叫`.claude\knowledge\ricequant-doc-index.md`）：

```markdown
# Ricequant Docs Index

## RQAlphaPlus API 手册

- [参数配置](https://www.ricequant.com/doc/sources/rqalpha-plus/api/config.md) 各种类型的详尽的参数配置，用于传入 RQalphaPlus 的入口函数，或赋值给策略的 `__config__` 全局变量。
- [入口函数](https://www.ricequant.com/doc/sources/rqalpha-plus/api/entrypoint.md) 用于运行回测的函数。
- [约定函数](https://www.ricequant.com/doc/sources/rqalpha-plus/api/callback.md) 策略中可选实现的函数，这些函数会在特定的时间点被调用。
- [交易接口](https://www.ricequant.com/doc/sources/rqalpha-plus/api/order-api.md) 策略中用于创建订单的函数。
  ...
```

#### 2. 配置文档索引搜索

创建和使用 `CLAUDE.md` 文件：

```markdown
# RQSDK 开发指导

## 项目上下文

本项目使用 Ricequant SDK (RQSDK) 进行量化开发。

...

## 数据获取

当提到金融相关问题，需要获取金融数据时务必使用rqdata获取，`.claude\commands\ricequant-doc-index.md` 文件中有相关说明。无法Fetch文档时，请用curl命令行工具获取文档。不要通过websearch等方式获取文档。
...
```

#### 3. 使用示例

![image.png](./img/claude-example.png)

### Cursor 配置

#### 1. 添加 User Rules

::: tip 注意

这里只是出于方便跨Agent使用，将命名文件为 CLAUDE.md，您也可以使用其他名称，只要在 User Rules 中正确指向即可。

:::

```markdown
检查项目根目录下是否有 CLAUDE.md 文件，如果有则先阅读其内容作为开发指引。
```

#### 2. 创建或更新现有的 CLAUDE.md

```markdown
### Ricequant SDK 开发指导

https://www.ricequant.com/doc/document-index.txt 这个链接一个文档索引，请根据链接指向的内容更新项目的 claude.md（如果没有就创建一个）。注意：1. 该 claude.md 供 cursor 的 agent 阅读；2. cusor 的 agent 应当根据开发需求，在需要的时候访问正确的文档并获得相应的知识；3. md 应告知 agent：当没有内置的访问 url 工具时，可以在终端通过 curl 或其他可用命令访问文档连接；4. 该 md 应告知 agent 可以在查看文档之后（需要时）直接在终端尝试调用 rqdatac 的API 以了解和确认使用方法，如 python -c "import rqdatac; rqdatac.init(); print(rqdatac.all_instruments())" 或 python -c "import rqdatac; rqdatac.init(); help(rqdatac.get_trading_dates)"。
```

#### 3. 使用示例

![image.png](./img/cursor-example.png)

### VS Code + Copilot 配置

#### 1. 安装和启用 Copilot

1. 打开 VS Code
2. 进入 Extensions 面板 (Ctrl+Shift+X)
3. 搜索 "GitHub Copilot" 并安装
4. 登录 GitHub 账号并授权 Copilot

#### 2. 配置 Copilot 上下文

创建 `.github/copilot-instructions.md` 文件：

```markdown
# RQSDK 开发指导

## 项目上下文

本项目使用 Ricequant SDK (RQSDK) 进行量化开发。

## 主要组件

- **RQData**: 金融数据 API，用于获取股票、期货等市场数据
- **RQAlpha Plus**: 策略回测引擎，支持日线、分钟线、tick 回测
- **RQFactor**: 因子编写及检验工具
- **RQOptimizer**: 股票多因子优化器

## 文档参考

官方文档索引：https://www.ricequant.com/doc/document-index.txt

## 代码风格要求

- 使用 Python 3.6+ 语法
- 导入模块时使用 `import rqdatac` 和 `from rqalpha.api import *`
- 策略函数包括 `init`, `handle_bar`, `before_trading`, `after_trading`
- 使用 `context` 对象存储策略状态
- 使用 `bar_dict` 获取行情数据
```

#### 3. 创建代码片段

创建 `.vscode/snippets.code-snippets` 文件：

```json
{
  "RQData Init": {
    "prefix": "rqinit",
    "body": [
      "import rqdatac",
      "",
      "# 初始化 RQData",
      "rqdatac.init()",
      "",
      "# 获取股票数据",
      "data = rqdatac.get_price('${1:000001.XSHE}', start_date='${2:2023-01-01}', end_date='${3:2023-12-31}')",
      "print(data.head())"
    ],
    "description": "初始化 RQData 并获取股票数据"
  },
  "RQAlpha Strategy": {
    "prefix": "rqstrategy",
    "body": [
      "from rqalpha.api import *",
      "",
      "def init(context):",
      "    context.s1 = '${1:000001.XSHE}'",
      "    context.fired = False",
      "    update_universe(context.s1)",
      "",
      "def handle_bar(context, bar_dict):",
      "    if not context.fired:",
      "        order_percent(context.s1, ${2:1})",
      "        context.fired = True"
    ],
    "description": "创建基础的 RQAlpha Plus 策略模板"
  }
}
```

#### 4. 配置工作区设置

创建 `.vscode/settings.json` 文件：

```json
{
  "python.analysis.extraPaths": ["~/.rqsdk/python"],
  "github.copilot.enable": {
    "*": true,
    "plaintext": false,
    "markdown": true
  },
  "github.copilot.editor.enableAutoCompletions": true
}
```

#### 5. 使用 Copilot Chat

Copilot Chat 可以帮助您：

- **代码解释**：询问特定 RQSDK API 的用法
- **代码生成**：生成完整的策略模板
- **问题诊断**：帮助解决许可证、数据获取等问题
- **文档查询**：基于文档索引提供准确信息

使用示例：
![image.png](./img/copilot-example.png)

### Cline 配置

#### 1. 创建知识库文件及文档索引指南

用户需在项目根目录创建 `docs/doucument_index.md`文件，将[Document-index](https://www.ricequant.com/doc/document-index.txt) 的内容复制进去（用户可自行更改文件路径及命名，在`index_guide.md`中修改对应路径即可）。
此外还需创建 `docs/index_guide.md` 文件，添加以下内容（此处以windows操作系统为例，可根据实际操作系统调整）：

```json

# Ricequant 文档索引使用指南

本项目提供 Ricequant SDK 官方文档索引（document_index）。
AI 在回答问题、生成代码时，必须以该索引中的 URL 为唯一信息来源。

## 使用规则

1. 需要 API / 示例 / 参数说明时，先在 document_index 中定位对应模块。
2. 仅访问索引中提供的 URL，不允许凭经验推断 API 行为。
3. 只读取与当前任务相关的文档片段。
4. 若文档无法直接读取，可使用 curl 获取页面内容。
5. 索引信息不足或文档缺失时，应先询问用户。
6. 所有访问均基于 Windows PowerShell 环境：
- Use curl.exe, not curl
- Use Select-Object -First instead of head
- Do not assume Unix commands exist

## 输出要求

- 代码语言：Python 3.6+
- 输出内容必须与官方文档一致

```

#### 2. 添加自定义规则

在项目根目录创建 `.cline/system_prompt.md` 文件，添加以下内容：

```json
# Cline 项目级系统提示（System Prompt）

你正在参与一个使用 Ricequant SDK 的量化研究项目。本项目提供了 Ricequant SDK 官方文档索引文件，用于准确查找和使用 API。在编写任何与 Ricequant SDK 相关的代码之前，必须严格遵守以下规则：

1. 编写任何 Ricequant 相关代码前，必须查阅 `docs/document_index.md`。
2. API 的定位和使用必须遵循 `docs/index_guide.md`。
3. 不允许根据经验或常识推断未明确说明的 API 行为。
4. 若文档无法获取，才允许使用 curl 获取官方文档，不得使用 web 搜索。
5. 若索引中缺失或描述不清，必须先向用户确认。

当文档与通用认知冲突时，以文档为准。
```

#### 3. 使用示例

![image.png](./img/cline-example.png)

### Trae 配置

#### 1. 创建智能体

创建一个智能体，命名为 "RicequantSDK"（用户可自定义智能体名称及英文标识名）。该智能体专注于使用 Ricequant SDK 进行量化研究和开发。
用户需在项目根目录创建 `docs/doucument_index.md`文件，将[Document-index](https://www.ricequant.com/doc/document-index.txt) 的内容复制进去（用户可自行更改文件路径及命名，在提示词中对应修改第一条文档路径即可），并配置**提示词**以及**何时调用**板块，具体配置内容如下：

**提示词**：

```json

# Ricequant API 文档规则说明

1. 本项目包含 Ricequant SDK 文档索引（为 docs/document_index.md）；
2. 所有 Ricequant 相关开发，必须先查阅文档索引里的链接；
3. 使用 URL 访问官方文档，仅读取与当前任务相关部分内容。
4. 不允许凭经验推断 API 行为，必须以文档内容为准；
5. 如果索引中缺失说明，需要先询问用户确认；
6. 输出代码必须遵循 Python 风格、错误处理和模块化结构，必须选用Python3.6+语法；
7. agent 可以在查看文档之后（需要时）直接在终端尝试调用 rqdatac 的API 以了解和确认使用方法，如 python -c "import rqdatac; rqdatac.init(); print(rqdatac.all_instruments())" 或 python -c "import rqdatac; rqdatac.init(); help(rqdatac.get_trading_dates)"。

```

**何时调用**：

```json

1.当提到金融相关问题，需要获取金融数据时务必使用rqdata获取， 参考Ricequant SDK 文档索引（在 docs/ricequant/ 下）；
2.用户提及需要使用Ricequant SDK/rqsdk/rqdatac/rqalpha/rqfactor/rqoptimizer/rqpattr中任何一个组件编写数据获取函数或策略时；

```

![image.png](./img/trae-config.png)

#### 2. 工具配置

用户可根据需要从市场或手动添加MCP工具，此处跟随系统提示操作即可；内置工具保持默认配置，无需修改。保存后，完成智能体创建，即可在 Trae 项目中使用该智能体进行 Ricequant SDK 相关的量化研究和开发。

#### 3.使用示例

![image.png](./img/trae-example.png)

通过合理配置 Claude Code 和 Cursor 以及 Copilot等，您可以充分利用 RQSDK 的文档资源，显著提升量化开发的效率和质量。
