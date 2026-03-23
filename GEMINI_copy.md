# Ricequant API 文档规则说明

1. 下面为Ricequant SDK 文档索引
2. 所有 Ricequant 相关开发，必须先查阅本地doc目录下的文档；
3. 不允许凭经验推断 API 行为，必须以文档内容为准；
4. 如果索引中缺失说明，需要先询问用户确认；
5. 输出代码必须遵循 Python 风格、错误处理和模块化结构，必须选用Python3.6+语法；
6. agent 可以在查看文档之后（需要时）直接在终端尝试调用 rqdatac 的API 以了解和确认使用方法，如 python -c "import rqdatac; rqdatac.init(); print(rqdatac.all_instruments())" 或 python -c "import rqdatac; rqdatac.init(); help(rqdatac.get_trading_dates)"。
7. 已配置好venv,使用`source venv/bin/active` 来运行代码,也可以使用 `uv pip install` 来安装额外的库

# 何时调用
1.当提到金融相关问题，需要获取金融数据时务必使用rqdata获取， 参考Ricequant SDK 文档索引（在 docs/ricequant/ 下）；
2.用户提及需要使用Ricequant SDK/rqsdk/rqdatac/rqalpha/rqfactor/rqoptimizer/rqpattr中任何一个组件编写数据获取函数或策略时；

# Ricequant Docs Index

## 文档目录

- # [参数配置](doc/rqalpha-plus_api_config.md) 各种类型的详尽的参数配置，用于传入 RQalphaPlus 的入口函数，或赋值给策略的 `__config__` 全局变量。
- # [入口函数](doc/rqalpha-plus_api_entrypoint.md) 用于运行回测的函数。
- # [约定函数](doc/rqalpha-plus_api_callback.md) 策略中可选实现的函数，这些函数会在特定的时间点被调用。
- # [交易接口](doc/rqalpha-plus_api_order-api.md) 策略中用于创建订单的函数。
- # [转账融资接口](doc/rqalpha-plus_api_transfer-financing-api.md) 策略中与转账融资相关的函数
- # [仓位查询接口](doc/rqalpha-plus_api_position-api.md) 策略中用于查询当前持仓的函数。
- # [数据查询接口](doc/rqalpha-plus_api_data-api.md) 策略中用于查询行情数据、财务数据等的函数。注：与 rqdata 有区别。
- # [其他接口](doc/rqalpha-plus_api_other-api.md) 合约订阅，指标计算，股票组合优化，以及画图等函数。
- # [类](doc/rqalpha-plus_api_types.md) 策略中会用到的类。
- # [枚举常量](doc/rqalpha-plus_api_enums.md) 策略中会用到的枚举常量。

## RQAlphaPlus 简介

- # [快速上手](doc/rqalpha-plus_doc_quick-start.md) 帮助您快速了解和使用回测
- # [进阶教程](doc/rqalpha-plus_doc_advance-tutorial.md) 账户和持仓配置、回测频率、支持的标的品种、事前风控、模拟撮合、自定义基准、出入金、管理费用、增量回测、定时器等功能
- # [常见问题](doc/rqalpha-plus_doc_question.md)
- # [示例策略](doc/rqalpha-plus_doc_example.md)
- # [更新履历](doc/rqalpha-plus_doc_changelogs.md)

## RQData HTTP API 手册

- # [数据获取](doc/rqdata_http_data-process.md) 通过 HTTP 接口的数据获取的流程和使用方法。
- # [请求示例](doc/rqdata_http_examples.md) Python、R、Matlab、Java 等多种编程语言的请求示例。
- # [接口方法](doc/rqdata_http_interface-method.md) 举例几种 Python API 不同返回类型的接口获取方式

## RQData Python API 手册

- # [RQData 使用说明](doc/rqdata_python_manual.md)
- [基础知识](doc/rqdata_python_manual.md#rqdata-basics) 关于 RQData 的架构、版本号、流量配额等信息将在这里阐述。
- [上手指引](doc/rqdata_python_manual.md#rqdata-get-started) 如果您是初次使用 RQData，这里提供了一些信息使您能快速熟悉 RQData 的整体使用方式。
- # API 参考
- [跨品种通用 API](doc/rqdata_python_generic-api.md) 介绍了 RQData 中对于所有金融标的都通用的 API，是整个 RQData 的基础 API 集合，也是使用最频繁的几个 API。主要包括了查询合约信息、查询历史行情、查询实时行情、检索交易日历等功能。
- [A 股](doc/rqdata_python_stock-mod.md) 查询财务数据、分红派息、拆股并股、流通股、板块及行业分类、融资融券、南北向资金、公告相关等及其他股票市场特有信息的 API。
- [港股（公测版本）](doc/rqdata_python_stock-hk.md) 查询行情、复权因子、财务数据、行业分类等
- [金融、商品期货](doc/rqdata_python_futures-mod.md) 主力合约、仓单数据、升贴水、交易参数等期货市场特有信息的 API。
- [金融、商品期权](doc/rqdata_python_options-mod.md) 期权合约、希腊字母、主力月份、PCR/skew 衍生指标等。
- [指数、场内基金](doc/rqdata_python_indices-mod.md) 获取指数值、成分及权重。
- [基金](doc/rqdata_python_fund-mod.md) 公募基金、ETF 的信息及估值、成分、持仓变动、份额变动、基金经理、分红等信息。
- [可转债](doc/rqdata_python_convertible-mod.md) 可转债信息、转债所对应的股票标的信息、强赎、回售、现金流、衍生指标、评级数据等信息。
- [风险因子](doc/rqdata_python_risk-factors-mod.md) 获得米筐自研 A 股风险因子模型、包含因子协方差、特异收益率及风险、个股暴露度等数据。
- [现货](doc/rqdata_python_spot-goods.md) 获取上海黄金现货交易所上市的现货
- [货币市场](doc/rqdata_python_repo.md) 获取国债回购行情、上海银行间同业拆放利率
- [宏观经济数据](doc/rqdata_python_macro-economy.md) 获取存款准备金率、货币供应量、宏观因子
- [另类数据](doc/rqdata_python_alternative-data.md) 获取一致预期、新闻舆情、ESG 评价数据
- [米筐特色指数](doc/rqdata_python_ricequant-index.md) 米筐特色指数行情、成分及指数编制规则等信息
- # [更新履历](doc/rqdata_python_changelogs.md)

## RQFactor API 手册

- # [内置因子](doc/rqfactor_api_biult-in-factor.md) 解释 RQFactor 内置的行情、财务、和技术类因子的名称、数据来源及调用方式。
- # [内置算子](doc/rqfactor_api_built-in-operators.md) 详解数学运算、时间序列、横截面等预设算子的参数含义、格式要求与配置逻辑。
- # [自定义算子](doc/rqfactor_api_custom-operators.md) 说明基于`CombinedFactor`/`RollingWindowFactor`等抽象类开发算子时，运算函数参数、输入因子参数、返回格式的配置规范。
- # [因子计算](doc/rqfactor_api_factor-calculation.md) 解释`execute_factor`函数中参数的配置要求，及数据预处理（复权、停牌填充）的参数规则。
- # [因子检验](doc/rqfactor_api_factor-test.md) 详解因子检验中“预处理”、“因子分析器”、“管道构建”和“执行计算”不同步骤的的配置方式，及结果输出参数的设置逻辑。

## RQFactor用户指南

- # [快速上手](doc/rqfactor_manual_quick-start.md) 帮助您快速了解因子开发流程
- # [进阶理解](doc/rqfactor_manual_advance-tutorial.md) 帮助您快速掌握自定义算子与因子
- # [使用示例](doc/rqfactor_manual_example.md)

## RQOptimizer API 手册

- # [选股API](doc/rqoptimize_api_select-stock.md) 介绍选股API的使用及参数详细说明
- # [优化器API](doc/rqoptimize_api_optimizer.md) 介绍优化器API的使用及参数详细说明

## RQOptimizer 用户指南

- # [快速上手](doc/rqoptimize_doc_quick-start.md)
- 帮助您快速了解优化器使用流程
- # [代码示例](doc/rqoptimize_doc_example.md)

## RQPAttr API文档目录

- # [归因API](doc/rqpattr_api_pattr-api.md) 介绍RQPAttr API

## 简介

- # [归因模型详解](doc/rqpattr_doc_model-introduction.md)
- 介绍权益类 Brinson 行业归因和因子归因的原理
- # [代码示例](doc/rqpattr_doc_example.md)

## Ricequant SDK-米筐本地量化开发工具套件文档

- # [操作手册](doc/rqsdk_manual-rqsdk.md)
- ## [快速上手](doc/rqsdk_manual-rqsdk.md#rqsdk-get-started) RQSDK 的快速上手指南。
- ## [RQSDK组件文档路径](doc/rqsdk_manual-rqsdk.md#rqsdk-doc-index) RQData、RQAlpha-Plus、RQFactor、RQOptimizer 四个组件的文档路径。
- ## [Anaconda安装](doc/rqsdk_manual-rqsdk.md#rqsdk-conda-isntall) Anaconda 的安装说明和环境管理（推荐使用）
- ## [VS Code 和PyCharm配置](doc/rqsdk_manual-rqsdk.md#rqsdk-doc-index-config) VS Code 和 PyCharm 的配置说明。
- ## [AI 编程工具配置指南](doc/rqsdk_manual-rqsdk.md#rqsdk-ai-tools) Claude Code、Cursor 和 VS Code Copilot 的配置说明。
- # [常见问题](doc/rqsdk_rqsdk-faq.md) RQSDK 常见问题解答。例如：如何解决安装过程中遇到的问题、如何解决使用过程中遇到的问题等。
- # [更新履历](doc/rqsdk_changelogs.md)

