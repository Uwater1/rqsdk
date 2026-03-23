## 常见问题

#### 1.磁盘空间不足

```python
(rqb) C:\Users\jinjuan\python\examples>rqsdk update-data --tick M1905C2350
开始更新 2 只标的的tick数据：{'M1905', 'M1905C2350'}
  [##################------------------]   50%
concurrent.futures.process._RemoteTraceback:
"""
Traceback (most recent call last):
  File "c:\users\jinjuan\miniconda3\miniconda\envs\rqb\lib\site-packages\rqalpha\utils\concurrent.py", line 26, in _process_worker
    r = call_item.fn(*call_item.args, **call_item.kwargs)
  File "rqalpha_plus\bundle.py", line 166, in rqalpha_plus.bundle._append_h5_tick
  File "rqalpha_plus\bundle.py", line 186, in rqalpha_plus.bundle._append_h5_tick
  File "h5py\_objects.pyx", line 54, in h5py._objects.with_phil.wrapper
  File "h5py\_objects.pyx", line 55, in h5py._objects.with_phil.wrapper
  File "c:\users\jinjuan\miniconda3\miniconda\envs\rqb\lib\site-packages\h5py\_hl\group.py", line 399, in __delitem__
    self.id.unlink(self._e(name))
  File "h5py\_objects.pyx", line 54, in h5py._objects.with_phil.wrapper
  File "h5py\_objects.pyx", line 55, in h5py._objects.with_phil.wrapper
  File "h5py\h5g.pyx", line 304, in h5py.h5g.GroupID.unlink
KeyError: "Couldn't delete link (link count would be negative)"
"""

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "c:\users\jinjuan\miniconda3\miniconda\envs\rqb\lib\runpy.py", line 192, in _run_module_as_main
    return _run_code(code, main_globals, None,
  File "c:\users\jinjuan\miniconda3\miniconda\envs\rqb\lib\runpy.py", line 85, in _run_code
    exec(code, run_globals)
  File "C:\Users\jinjuan\Miniconda3\miniconda\envs\rqb\Scripts\rqsdk.exe\__main__.py", line 7, in <module>
  File "c:\users\jinjuan\miniconda3\miniconda\envs\rqb\lib\site-packages\rqsdk\__init__.py", line 26, in entry_point
    cli()
  File "c:\users\jinjuan\miniconda3\miniconda\envs\rqb\lib\site-packages\click\core.py", line 764, in __call__
    return self.main(*args, **kwargs)
  File "c:\users\jinjuan\miniconda3\miniconda\envs\rqb\lib\site-packages\click\core.py", line 717, in main
    rv = self.invoke(ctx)
  File "c:\users\jinjuan\miniconda3\miniconda\envs\rqb\lib\site-packages\click\core.py", line 1137, in invoke
    return _process_result(sub_ctx.command.invoke(sub_ctx))
  File "c:\users\jinjuan\miniconda3\miniconda\envs\rqb\lib\site-packages\click\core.py", line 956, in invoke
    return ctx.invoke(self.callback, **ctx.params)
  File "c:\users\jinjuan\miniconda3\miniconda\envs\rqb\lib\site-packages\click\core.py", line 555, in invoke
    return callback(*args, **kwargs)
  File "c:\users\jinjuan\miniconda3\miniconda\envs\rqb\lib\site-packages\rqalpha_plus\cmds.py", line 66, in update_bundle
    update_tick(os.path.join(path, "h5", "ticks"), tick, with_derivatives, concurrency)
  File "rqalpha_plus\bundle.py", line 217, in rqalpha_plus.bundle.update_tick
  File "c:\users\jinjuan\miniconda3\miniconda\envs\rqb\lib\concurrent\futures\_base.py", line 636, in __exit__
    self.shutdown(wait=True)
  File "c:\users\jinjuan\miniconda3\miniconda\envs\rqb\lib\site-packages\rqalpha\utils\concurrent.py", line 94, in shutdown
    raise fut.exception()
KeyError: "Couldn't delete link (link count would be negative)"
```

请查看您存储数据的磁盘是否有足够的可用空间，若可用空间不足，请清理一些空间后再次更新数据，如无法解决该问题，请联系我们协助您解决。

#### 2.本地 bundle 数据被损坏

![数据损坏](./img/rqsdk-data-corruption.png)
一般报上述错误原因是本地数据被损坏，请找到该指定文件进行删除，然后重新执行一次更新即可。

#### 3.同时对本地 bundle 进行读写操作

更新数据时报错：unable to create file 'resource temporaily unavailable'
![同时读写](./img/data-read-and-write.png)
通常是由于其他程序在占用 bundle 文件导致的,更新数据过程中，请不要运行回测，避免出现同时读写数据的情况。

#### 4.简单举例说明如何更新数据

- 更新基础日线

```python
rqsdk update-data --base
```

- 更新分钟线

```python
## 更新某几个合约的分钟线
rqsdk update-data --minbar 000001.XSHE --minbar 000002.XSHE --minbar IF2006
## 更新某个期货品种的分钟线
rqsdk update-data --minbar RB
## 更新某个资产的分钟线,耗时较长，可能会突破流量限制，不建议这样更新
rqsdk update-data --minbar futures
## 更新某个合约分钟线的同时也更新日线
rqsdk update-data --base --minbar 000001.XSHE
## 更新某个合约的分钟数据的同时也更新该合约的相关衍生品数据
rqsdk update-data --minbar M1905 --with-derivatives
```

- 更新 tick

```python
## 更新合约tick数据使用方式和更新分钟线类似
rqsdk update-data --tick M1905
```

**更新数据的完整参数说明可通过运行 `rqsdk update-data --help` 查看**

#### 5.将 bundle 数据下载到指定位置

```python
## 用 -d 指定下载数据的保存位置，如将 000001.XSHE的最新分钟数据下载到D:\bundle
rqsdk update-data --minbar 000001.XSHE -d D:\bundle
```

#### 6.查询下载到本地的 bundle 数据

首先找到对应的 bundle 文件，默认会下载到 C 盘用户目录下的的.rqalpha-plus 文件夹下，以股票日线为例就是 C:\Users\用户\.rqalpha-plus\bundle\stocks.h5，然后在 python 中使用下列代码进行查询

```python
import h5py

import pandas

import numpy as np

file_path = r"C:\Users\rice\.rqalpha-plus\bundle\stocks.h5"

#r只读，r+读写，不创建

h5 = h5py.File(file_path,"r")

order_book_id = "000401.XSHE"

#print(h5[order_book_id][()])

#print(h5.keys())

#print(order_book_id in h5.keys())

#print(h5[order_book_id].value)

#df = pandas.DataFrame(h5[order_book_id].value)

df = pandas.DataFrame(h5[order_book_id][()])

# 具体查询某个日期

df[df['datetime']==np.int64('20051130000000')]
```

#### 7.运行回测报错找不到指定模块

报错类似下图
![缺失包](./img/rqsdk-lacking-module.png)
一般是需要重新安装所缺的包

```python
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple h5py --force-reinstall
```

#### 8.如何查看某次回测的交易流水

参见 RQAlpha Plus 使用教程保存[回测结果](../rqalpha-plus/doc/quick-start#quick-start-save-result)

#### 9.运行回测日志报订单创建失败: 下单量为 0 的 WARN

一般是用 order_target_percent 或者 order_target_value 的时候容易出现，原因是调仓的股票下单数量小于 100 股导致的。举例说明：已有 300268 的持仓 57500 股，用 Order_target_pecent 下单的目标仓位是 57511，也就是要再买 57511-57500=11 股，11 股不满足 100 的整数倍的交易规则，所以出现这个 WARN。

#### 10. linux 系统上运行样例策略报错

报错提示：tkinter.TclError: couldn't connect to display "localhost:10.0"
![linux运行回测报错](./img/linux-bactest-error.png)
原因是 Linux 系统没有 GUI，图片无法展示，把运行回测命令里面的 --plot 去掉

#### 11. 如何在 Apple Silicon（M1）平台的 Mac 上安装 RQSDK？ {#install-rqsdk-on-m1}

从 1.4.1 开始，RQSDK 开始提供为 M1 平台原生编译的版本（**该版本暂不包含 RQOptimizer**），但在现阶段——因为众多第三方包的支持问题——x86 版本仍然是兼容性更好的选择。

如您希望安装 x86 版本的 rqsdk，您需要首先安装 [x86 版本的 conda](https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-latest-MacOSX-x86_64.pkg)，并在该 conda 创建的虚拟环境中按照[一般的安装流程](#install-rqsdk)安装 RQSDK 。

如您暂不需要用到 RQOptimizer，且希望拥有更好的执行性能，您可以选择安装 ARM 版本。您只需要安装 [ARM 版本的 conda](https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-latest-MacOSX-arm64.sh)，并在该 conda 创建的虚拟环境中安装 RQSDK 即可。
