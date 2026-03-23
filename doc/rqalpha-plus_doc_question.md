# 常见问题 {#rqalpha-plus-faq}

#### 为什么部分 API 与 RQDatac 中的 API 同名但用法不同？ {#rqalpha-plus-faq-api-diff}

RQDatac 的 API 与 RQAlphaPlus 提供的 API 使用场景不同。RQAlphaPlus 提供的 API 通常在策略内调用，故更多考虑的是如何更方便地调取到“当前时间“的数据以及如何避免策略无意间调用到未来数据。

如果希望在策略中调用 rqdatac 的 API，需要显示地引入 rqdatac 包，如：

```python
import rqdatac

rqdatac.get_price("000001.XSHE")
```

#### RQAlphaPlus 中的接口是线程安全的吗？ {#rqalpha-plus-faq-thread-safe}

不是。请勿在多线程环境中运行 RQAlphaPlus 或在策略中开启子线程。任何情况下每个进程中同一时间应只有一个策略实例在运行，否则可能会导致 RQAlphaPlus 出现不可预测的行为。

#### 为什么我已经在终端配置了 RQSDK 的 License，但在 IDE/编辑器中依然会遇到 License 不生效的情况？ {#rqalpha-plus-faq-license}

该问题通常会发生在 Linux/macOS 中。

RQSDK 通过环境变量存储 License 等配置信息。在 Linux 和 macOS 中，环境变量是通过在 bash 启动文件（`.bash_profile`、 `.bashrc`、 `.zshrc`）中添加命令的方式设置的。若您使用的 IDE 或编辑器因为某些原因未能读取到环境变量，则会出现执行策略或脚本时报出无权限的错误、或 RQDatac 无法正确初始化的情况。

您需要了解：

- `rqsdk license` 命令会设置 `RQSDK_LICENSE` 和 `RQDATAC_CONF` 两个环境变量

- `rqsdk config --rqdatac` 命令会设置 `RQDATAC2_CONF` 环境变量

解决问题的方法：

1. 首先确认您的终端内能够正确读取到上述环境变量
2. 尝试在上述终端内启动 IDE
3. 在 IDE 内执行代码以确认能否读取上述环境变量

若问题依旧，您可以：

1. 尝试升级 IDE 版本，并联系 IDE 提供方寻求帮助
2. 在 IDE 的设置中或您的脚本中手动配置上述环境变量
