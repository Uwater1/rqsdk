# 转账融资接口 {#rqalpha-plus-api-transfer-financing}

### deposit - 入金（增加账户资金） {#rqalpha-plus-api-transfer-deposit}

```python
rqalpha.api.deposit(account_type, amount, receiving_days=0)
```

入金（增加账户资金）

#### 参数 {#rqalpha-plus-api-transfer-deposit-params}

| 参数名         | 类型    | 说明                                                           |
| -------------- | ------- | -------------------------------------------------------------- |
| account_type   | _str_   | 账户类型                                                       |
| amount         | _float_ | 入金金额                                                       |
| receiving_days | _int_   | 入金到账天数，0 表示立刻到账，1 表示资金在下一个交易日盘前到账 |

#### 返回 {#rqalpha-plus-api-transfer-deposit-return}

_None_

### withdraw - 出金（减少账户资金） {#rqalpha-plus-api-transfer-withdraw}

```python
rqalpha.api.withdraw(account_type, amount)
```

出金（减少账户资金）

#### 参数 {#rqalpha-plus-api-transfer-withdraw-params}

| 参数名       | 类型    | 说明     |
| ------------ | ------- | -------- |
| account_type | _str_   | 账户类型 |
| amount       | _float_ | 减少金额 |

#### 返回 {#rqalpha-plus-api-transfer-withdraw-return}

_None_

### finance - 融资（增加账户资金，增加负债） {#rqalpha-plus-api-transfer-finance}

```python
rqalpha.api.finance(amount, account_type=DEFAULT_ACCOUNT_TYPE.STOCK)
```

融资

#### 参数 {#rqalpha-plus-api-transfer-finance-params}

| 参数名       | 类型    | 说明     |
| ------------ | ------- | -------- |
| amount       | _float_ | 融资金额 |
| account_type | _str_   | 融资账户 |

#### 返回 {#rqalpha-plus-api-transfer-finance-return}

_None_

### repay - 还款（减少账户资金，减少负债） {#rqalpha-plus-api-transfer-repay}

```python
rqalpha.api.repay(amount, account_type=DEFAULT_ACCOUNT_TYPE.STOCK)
```

进行还款操作，减少账户资金同时减少负债。

#### 参数 {#rqalpha-plus-api-transfer-repay-params}

| 参数名       | 类型    | 说明     |
| ------------ | ------- | -------- |
| amount       | _float_ | 还款金额 |
| account_type | _str_   | 还款账户 |

#### 返回 {#rqalpha-plus-api-transfer-repay-return}

_None_
