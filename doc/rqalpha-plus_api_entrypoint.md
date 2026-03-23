# 入口函数 {#rqalpha-plus-api-entrypoint}

### run_func - 传入约定函数运行回测 {#rqalpha-plus-api-entrypoint-run-func}

```python
rqalpha.run_func(**kwargs)
```

传入约定函数和策略配置运行回测。约定函数详见[约定函数]部分，可用的配置项详见[参数配置]部分。

#### 参数 {#rqalpha-plus-api-entrypoint-run-func-params}

| 参数名         | 类型                                                                                                                                           | 说明                                                               |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| config         | _dict_                                                                                                                                         | 策略配置字典                                                       |
| init           | _Callable_[[[StrategyContext](./types#rqalpha-plus-api-types-context)], _Any_]                                                                 | 策略初始化函数，会在策略开始运行时被调用，仅会执行一次             |
| before_trading | _Callable_[[[StrategyContext](./types#rqalpha-plus-api-types-context)], _Any_]                                                                 | 盘前函数，会在每日盘前被调用一次                                   |
| open_auction   | _Callable_[[[StrategyContext](./types#rqalpha-plus-api-types-context), _dict_[_str_, [BarObject](./types#rqalpha-plus-api-types-bar)]], _Any_] | 集合竞价函数，会在每日盘前集合竞价阶段被调用一次                   |
| handle_bar     | _Callable_[[[StrategyContext](./types#rqalpha-plus-api-types-context), _dict_[_str_,[BarObject](./types#rqalpha-plus-api-types-bar)]], _Any_]  | k 线处理函数，会在盘中 k 线发生更新时被调用，适用于日/分钟级别回测 |
| handle_tick    | _Callable_[[[StrategyContext](./types#rqalpha-plus-api-types-context), [TickObject](./types#rqalpha-plus-api-types-tick)], _Any_]              | 快照数据处理函数，会在每个 tick 到达时被调用，适用于 tick 回测     |
| after_trading  | _Callable_[[[StrategyContext](./types#rqalpha-plus-api-types-context)], _Any_]                                                                 | 盘后函数，会在每日交易结束后被调用一次                             |

#### 返回 {#rqalpha-plus-api-entrypoint-run-func-return}

_dict_

#### 范例 {#rqalpha-plus-api-entrypoint-run-func-example}

```python
config = {
    "base": {
        ...
    }
}

def init(context):
    ...

def handle_bar(context, bar_dict):
    ...

run_func(config=config, init=init, handle_bar=handle_bar)
```

### run_file - 传入代码文件运行回测

```python
rqalpha.run_file(strategy_file_path, config=None)
```

通过传入策略代码文件来运行回测。

#### 参数 {#rqalpha-plus-api-entrypoint-run-file-params}

| 参数名             | 类型               | 说明                                                                             |
| ------------------ | ------------------ | -------------------------------------------------------------------------------- |
| strategy_file_path | _str_              | 策略文件路径                                                                     |
| config             | _Optional_[_dict_] | 策略配置项字典，默认为空，此处传入的配置项优先级高于策略内 **config** 中的配置项 |

#### 返回 {#rqalpha-plus-api-entrypoint-run-file-return}

_dict_

#### 范例 {#rqalpha-plus-api-entrypoint-run-file-example}

```python
config = {
    "base": {
        ...
    }
}

run_file("strategy.py", config=config)
```

### run_code - 传入代码字符串运行回测

```python
 rqalpha.run_code(code, config=None)
```

通过传入策略代码字符串来运行回测。

#### 参数 {#rqalpha-plus-api-entrypoint-run-code-params}

| 参数名 | 类型             | 说明                                                                             |
| ------ | ---------------- | -------------------------------------------------------------------------------- |
| code   | _str_            | 策略代码字符串                                                                   |
| config | _Optional[dict]_ | 策略配置项字典，默认为空，此处传入的配置项优先级高于策略内 **config** 中的配置项 |

#### 返回 {#rqalpha-plus-api-entrypoint-run-code-return}

_dict_

#### 范例 {#rqalpha-plus-api-entrypoint-run-code-example}

```python
config = {
    "base": {
        ...
    }
}

CODE = """
def init(context):
    ...

def handle_bar(context, bar_dict):
    ...
"""

run_code(CODE, config=config)
```
