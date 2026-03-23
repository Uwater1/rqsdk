# 数据获取

## 相关参数说明 {#related-parameter-description}

| 参数      | 含义             | 示例                                                                                                                                                                                           |
| :-------- | :--------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| url       | api 地址         | _<https://rqdata.ricequant.com/><指令>_， 其中<指令>需要替换成/auth 或者 /api                                                                                                                  |
| user_name | 用户名           | ricequant 注册帐号，获取 token 需要                                                                                                                                                            |
| password  | 密码             | 以上用户名登录密码，获取 token 需要                                                                                                                                                            |
| headers   | 头文件           | 用于获取数据请求时存放 token，例如 `{“token": "7dsf9ad6sDAsd889da"}`                                                                                                                           |
| data      | 请求时的主要数据 | 字典格式，必须包含 `{"method"： "<\*api name>"}`，具体内容依据使用的 [Python API](../python/index-rqdatac.md) 而定，如 `{"method": "instruments", "order_book_ids": ["10001941", "10001943"]}` |

## 数据获取流程 {#Data-acquisition-process}

> 1. 使用 post 方式以及帐号密码获取用户凭证(token)，指定传入的 data 参数为 json
> 2. 使用上述流程得到返回值并获取 token，在请求数据中加入 token，同样使用 post 方式获取数据

## 接口请求说明 {#interface-description}

> 获取 token 的接口： _<https://rqdata.ricequant.com/auth>_<br/>
> 获取数据的接口： _<https://rqdata.ricequant.com/api>_

## 使用方法 {#instructions}

#### 1、获取用户凭证(token) {#get-token}

获取数据之前，必须先获取 token, 即用户凭证，以作为用户获取数据的认证。该认证当天有效。token 过期或者更改用户权限后可重新获取。重新获取 token 后，旧的 token 随即失效。获取 token 所需要的参数示例如下

```
{
    "user_name" : "your_username",
    "password" : "your_password"
}
```

#### 2、请求数据 {#request-data}

获取 token 后，请设置 http 请求的数据以及头文件，请求的数据包含 API 名称以及相关参数。

- HTTP 接口请求体为 `json` 格式，需要设置请求的 `Content-Type` 为 `application/json`，与 [Python API](../python/index-rqdatac.md) 一样，请求中需要包含必需的参数，请求格式如下：

```json
{
  "method": "get_price",
  "order_book_ids": ["000001.XSHE", "600000.XSHG"],
  "start_date": 20190601,
  "end_date": 20191001,
  "fields": ["open", "close", "high", "low"],
  "adjust_type": "none"
}
```

- HTTP 请求头文件必须包含 token，示例如下：

```
{
    "token": "7dsf9ad6sDAsd889da"
}
```

## 返回格式 {#response-format}

csv 格式文本数据，示例

```
order_book_id,date,open,close,high,low
000001.XSHE,2019-06-03,12.22,11.9,12.33,11.82
000001.XSHE,2019-06-04,11.89,11.85,11.94,11.6
000001.XSHE,2019-06-05,11.97,11.97,12.14,11.92
000001.XSHE,2019-06-06,11.97,11.92,12.07,11.89
000001.XSHE,2019-06-10,12.01,12.34,12.47,11.98
000001.XSHE,2019-06-11,12.34,12.65,12.72,12.3
```

## 特殊请求注意事项 {#special-request-notes}

::: tip 注意事项
1、如果 Python API 定义的参数本身包含 method，需要将原本的 method 修改为 m，避免关键字冲突。<br/>
2、在 HTTP 接口中，所有 expect_df 参数会被忽略。<br/>
3、过大的get_factor 请求会直接拒绝，大致上会限制到每个请求可以取1个因子全市场八年左右（导出为 csv 之后大概250M ）
:::

#### 举例{#special-request-notes-example}

- Python API

```python
get_factor_return(start_date, end_date, factors=None, universe='whole_market', method='implicit', industry_mapping='sws_2021', model='v1', market='cn')
```

那么请求需改变为

```
{
    "m": "get_factor_return",
    "start_date": 20240104,
    "end_date": 20240115,
    "method": "implicit"
}
```
