# 内置因子

在使用 RQFactor 需先导入相关模块：

``` python
from rqfactor import *
```

后续可在因子表达式中直接引用系统预设中常见的`行情因子`、`财务因子`、`Alpha101 因子`、`技术指标因子`。

除特殊标注外，所有内置因子均通过 `Factor('factor_name')` 语法引用，其中 `factor_name` 为具体因子名称。各类因子的引用方式与具体说明如下：

### 行情因子 

引用方式： 
```python
Factor('factor')
```

**可用因子清单：**

| 因子           | 类型  | 说明     |
| -------------- | ----- | -------- |
| open           | float | 开盘价   |
| close          | float | 收盘价   |
| high           | float | 最高价   |
| low            | float | 最低价   |
| total_turnover | float | 总成交额 |
| volume         | float | 总成交量 |
| num_trades     | float | 成交笔数 |

### 财务因子

引用方式： 
```python
Factor('factor')
```

  可引用的财务因子可见[基础财务因子](../../rqdata/python/stock-mod.md#stock-API-financials)、 [财务衍生指标因子](../../rqdata/python/stock-mod.md#financial_indicators)
  

### alpha101 因子

引用方式： 
```python
Factor('factor')
```

可引用因子详情可见 [alpha101 因子](../../rqdata/python/stock-mod.md#alpha101)

### 技术指标

引用方式： 
```python
Factor('factor')
```
    
具体因子详情可见 [技术指标因子](../../rqdata/python/stock-mod.md#technicals)

### 举例

  - 自定义因子中引用行情相关的因子

    ```python
    from rqfactor import *
    def compute():
        return Factor('open') + Factor('close')
    ```

  - 自定义因子中引用财务类的因子。

    ```python
    from rqfactor import *
    def compute():
        return Factor('pe_ratio')
    ```

  - 自定义因子中引用技术类因子。
    ```python
    from rqfactor import *
    def compute():
        return KDJ_K
    ```
  - 自定义财务因子。

    ```python
    from rqfactor import *
    def compute():
        return 1/Factor('pe_ratio') + 1/Factor('pb_ratio') + Factor('return_on_equity')
    ```