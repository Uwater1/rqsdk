## 使用范例

该范例所使用的组合数据来自于通过 rqalpha-plus 回测框架回测后所保存的回测结果。

```python
import os
import pandas as pd
import numpy as np
import rqdatac
import pickle
from rqalpha.mod.rqalpha_mod_sys_analyser.plot import *
from rqdatac import *
import rqpattr
from rqpattr.api import performance_attribute

import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings("ignore")

rqdatac.init()

#读取回测后保存的回测结果
path = os.getcwd()+'\\bts\\bts'
files = '000906.XSHG_factor1_liquidity_v2_asfc.pkl'
result = pd.read_pickle(os.path.join(path, files))
print('result')

#out:
# {'sys_analyser': {'summary': {'strategy_name': 'strategy',
#    'start_date': '2020-06-10',
#    'end_date': '2022-06-30',
#    'strategy_file': 'strategy.py',
#    'run_type': 'BACKTEST',
#    'starting_cash': 'STOCK:1000000000.0',
#    'STOCK': 1000000000.0,
#    'benchmark': '000906.XSHG',
#    'benchmark_symbol': '中证800',
#    'alpha': 0.04161847252000668,
#    'beta': 0.9689441949400958,
#    'sharpe': 0.42678333868827145,
#    'excess_sharpe': 0.3582160902725003,
#    'information_ratio': 0.3453132024893898,
#    'downside_risk': 0.1655438441069776,
#    'tracking_error': 0.12271422135189096,
#    'sortino': 0.5852185528297059,
#    'volatility': 0.22699885420999039,
#    'excess_volatility': 0.007730269334000854,
#    'excess_annual_volatility': 0.12271422135189096,
#    'max_drawdown': 0.3449066882507446,
#    'excess_max_drawdown': 0.16459229054214705,
#    'excess_returns': 0.07486020583373909,
#    'excess_annual_returns': 0.03712968826159724,
#    'var': 0.023450724628239612,
#    'total_value': 1203328714.4768782,
#    'cash': 8210.926878128295,
#    'total_returns': 0.20332871447687806,
#    'annualized_returns': 0.09798110622545697,
#    'unit_net_value': 1.203328714476878,
#    'units': 1000000000.0,
#    'benchmark_total_returns': 0.11694720785066992,
#    'benchmark_annualized_returns': 0.05744300314969153,
#    'excess_cum_returns': 0.08638150662620814,
#    'max_drawdown_duration': IndexRange(start=305, end=498, start_date=datetime.date(2021, 9, 7), end_date=datetime.date(2022, 6, 30)),
#    'max_drawdown_duration_start_date': '2021-09-07',
#    'max_drawdown_duration_end_date': '2022-06-30',
#    'max_drawdown_duration_days': 296,
#    'turnover': 19.746910020902284,
#    'avg_daily_turnover': 0.03878575014506964,
#    'excess_max_drawdown_duration': IndexRange(start=69, end=277, start_date=datetime.date(2020, 9, 17), end_date=datetime.date(2021, 7, 29)),
#    'excess_max_drawdown_duration_start_date': '2020-09-17',
#    'excess_max_drawdown_duration_end_date': '2021-07-29',
#    'excess_max_drawdown_duration_days': 315,
#    'weekly_alpha': 0.0407174667550259,
#    'weekly_beta': 0.9442199165766891,
#    'weekly_sharpe': 0.4328984550718106,
#    'weekly_sortino': 0.6233499038107769,
#    'weekly_information_ratio': 0.38383642721331795,
#    'weekly_tracking_error': 0.015232196824837712,
#    'weekly_max_drawdown': 0.2874243182734171},
#   'trades':                                 datetime     trading_datetime order_book_id  \
#   datetime
#   2020-06-10 15:00:00  2020-06-10 15:00:00  2020-06-10 15:00:00   000671.XSHE
#   2020-06-10 15:00:00  2020-06-10 15:00:00  2020-06-10 15:00:00   603806.XSHG
#   2020-06-10 15:00:00  2020-06-10 15:00:00  2020-06-10 15:00:00   002773.XSHE
#   2020-06-10 15:00:00  2020-06-10 15:00:00  2020-06-10 15:00:00   000988.XSHE
#   2020-06-10 15:00:00  2020-06-10 15:00:00  2020-06-10 15:00:00   601811.XSHG
#   ...                                  ...                  ...           ...
#   2022-06-13 15:00:00  2022-06-13 15:00:00  2022-06-13 15:00:00   511220.XSHG
#   2022-06-16 15:00:00  2022-06-16 15:00:00  2022-06-16 15:00:00   511220.XSHG
#   2022-06-23 15:00:00  2022-06-23 15:00:00  2022-06-23 15:00:00   511220.XSHG
#   2022-06-29 15:00:00  2022-06-29 15:00:00  2022-06-29 15:00:00   511220.XSHG
#   2022-06-30 15:00:00  2022-06-30 15:00:00  2022-06-30 15:00:00   511220.XSHG

#                          symbol side position_effect         exec_id  tax  \
#   datetime
#   2020-06-10 15:00:00       阳光城  BUY            OPEN  16710930284727  0.0
#   2020-06-10 15:00:00       福斯特  BUY            OPEN  16710930284728  0.0
#   2020-06-10 15:00:00      康弘药业  BUY            OPEN  16710930284729  0.0
#   2020-06-10 15:00:00      华工科技  BUY            OPEN  16710930284730  0.0
#   2020-06-10 15:00:00      新华文轩  BUY            OPEN  16710930284731  0.0
#   ...                       ...  ...             ...             ...  ...
#   2022-06-13 15:00:00  海富通城投ETF  BUY            OPEN  16710930286411  0.0
#   2022-06-16 15:00:00  海富通城投ETF  BUY            OPEN  16710930286412  0.0
#   2022-06-23 15:00:00  海富通城投ETF  BUY            OPEN  16710930286413  0.0
#   2022-06-29 15:00:00  海富通城投ETF  BUY            OPEN  16710930286414  0.0
#   2022-06-30 15:00:00  海富通城投ETF  BUY            OPEN  16710930286415  0.0

#                         commission  last_quantity  last_price        order_id  \
#   datetime
#   2020-06-10 15:00:00  54331.39440       26711600       6.780  16710930364951
#   2020-06-10 15:00:00  38711.06820        3062100      42.140  16710930364963
#   2020-06-10 15:00:00  28030.80870        2358900      39.610  16710930364972
#   2020-06-10 15:00:00  24600.08340        3723900      22.020  16710930364985
#   2020-06-10 15:00:00  22208.87760        7243600      10.220  16710930365008
#   ...                          ...            ...         ...             ...
#   2022-06-13 15:00:00     11.89320            400      99.110  16710930376692
#   2022-06-16 15:00:00    178.43040           6000      99.128  16710930376694
#   2022-06-23 15:00:00      5.00000            100      99.259  16710930376696
#   2022-06-29 15:00:00   1844.92842          62600      98.239  16710930376698
#   2022-06-30 15:00:00      8.84205            300      98.245  16710930376700

#                        transaction_cost
#   datetime
#   2020-06-10 15:00:00       54331.39440
#   2020-06-10 15:00:00       38711.06820
#   2020-06-10 15:00:00       28030.80870
#   2020-06-10 15:00:00       24600.08340
#   2020-06-10 15:00:00       22208.87760
#   ...                               ...
#   2022-06-13 15:00:00          11.89320
#   2022-06-16 15:00:00         178.43040
#   2022-06-23 15:00:00           5.00000
#   2022-06-29 15:00:00        1844.92842
#   2022-06-30 15:00:00           8.84205

#   [1689 rows x 13 columns],
#   'portfolio':                  cash   total_value  market_value  unit_net_value  \
#   date
#   2020-06-10   153.0189  9.997001e+08  9.996999e+08        0.999700
#   2020-06-11   153.0189  9.918064e+08  9.918062e+08        0.991806
#   2020-06-12  1984.0438  9.998441e+08  9.998421e+08        0.999844
#   2020-06-15  1984.0438  9.891545e+08  9.891525e+08        0.989154
#   2020-06-16  1984.0438  1.006052e+09  1.006050e+09        1.006052
#   ...               ...           ...           ...             ...
#   2022-06-24   161.1973  1.187876e+09  1.187876e+09        1.187876
#   2022-06-27   161.1973  1.196714e+09  1.196679e+09        1.196714
#   2022-06-28   161.1973  1.205983e+09  1.205948e+09        1.205983
#   2022-06-29  2893.2689  1.168880e+09  1.168843e+09        1.168880
#   2022-06-30  8210.9269  1.203329e+09  1.203321e+09        1.203329

#                      units  static_unit_net_value
#   date
#   2020-06-10  1.000000e+09                 1.0000
#   2020-06-11  1.000000e+09                 0.9997
#   2020-06-12  1.000000e+09                 0.9918
#   2020-06-15  1.000000e+09                 0.9998
#   2020-06-16  1.000000e+09                 0.9892
#   ...                  ...                    ...
#   2022-06-24  1.000000e+09                 1.1671
#   2022-06-27  1.000000e+09                 1.1879
#   2022-06-28  1.000000e+09                 1.1967
#   2022-06-29  1.000000e+09                 1.2060
#   2022-06-30  1.000000e+09                 1.1689

#   [499 rows x 6 columns],
#   'benchmark_portfolio':             unit_net_value
#   date
#   2020-06-10        0.998862
#   2020-06-11        0.989584
#   2020-06-12        0.991023
#   2020-06-15        0.982023
#   2020-06-16        0.997713
#   ...                    ...
#   2022-06-24        1.096298
#   2022-06-27        1.107309
#   2022-06-28        1.119947
#   2022-06-29        1.101584
#   2022-06-30        1.116947

#   [499 rows x 1 columns],
#   'stock_account':                  cash  transaction_cost  market_value   total_value
#   date
#   2020-06-10   153.0189       299909.9811  9.996999e+08  9.997001e+08
#   2020-06-11   153.0189            0.0000  9.918062e+08  9.918064e+08
#   2020-06-12  1984.0438         1853.5725  9.998421e+08  9.998441e+08
#   2020-06-15  1984.0438            0.0000  9.891525e+08  9.891545e+08
#   2020-06-16  1984.0438            0.0000  1.006050e+09  1.006052e+09
#   ...               ...               ...           ...           ...
#   2022-06-24   161.1973            0.0000  1.187876e+09  1.187876e+09
#   2022-06-27   161.1973            0.0000  1.196679e+09  1.196714e+09
#   2022-06-28   161.1973            0.0000  1.205948e+09  1.205983e+09
#   2022-06-29  2893.2689         1844.9284  1.168843e+09  1.168880e+09
#   2022-06-30  8210.9269            8.8421  1.203321e+09  1.203329e+09

#   [499 rows x 4 columns],
#   'stock_positions':            order_book_id symbol    quantity  last_price  avg_price  \
#   date
#   2020-06-10   000671.XSHE    阳光城  26711600.0        6.78      6.780
#   2020-06-10   603806.XSHG    福斯特   3062100.0       42.14     42.140
#   2020-06-10   002773.XSHE   康弘药业   2358900.0       39.61     39.610
#   2020-06-10   000988.XSHE   华工科技   3723900.0       22.02     22.020
#   2020-06-10   601811.XSHG   新华文轩   7243600.0       10.22     10.220
#   ...                  ...    ...         ...         ...        ...
#   2022-06-30   002460.XSHE   赣锋锂业     38100.0      148.70    141.450
#   2022-06-30   600316.XSHG   洪都航空    101100.0       30.24     31.603
#   2022-06-30   601117.XSHG   中国化学    300600.0        9.41      9.644
#   2022-06-30   600079.XSHG   人福医药    149200.0       16.00     18.070
#   2022-06-30   600588.XSHG   用友网络     42500.0       21.71     29.880

#               market_value
#   date
#   2020-06-10   181104648.0
#   2020-06-10   129036894.0
#   2020-06-10    93436029.0
#   2020-06-10    82000278.0
#   2020-06-10    74029592.0
#   ...                  ...
#   2022-06-30     5665470.0
#   2022-06-30     3057264.0
#   2022-06-30     2828646.0
#   2022-06-30     2387200.0
#   2022-06-30      922675.0

#   [19797 rows x 6 columns],
#   'yearly_risk_free_rates': {2020: 0.020009000000000002, 2021: 0, 2022: 0}}}

```

获取回测结果中持仓及权益数据

```python

positions = result['sys_analyser']['stock_positions']
portfolio = result['sys_analyser']['portfolio']

positions = positions.join(portfolio['total_value'])
positions['asset_type'] = 'stock'
positions = positions.reset_index()
positions = positions.set_index(['date','order_book_id','asset_type'])
daily_return  = portfolio['unit_net_value'].pct_change().dropna()
weights = positions['market_value']/positions['total_value']
print('daily_return')

#   out:
#   date
#   2020-06-11   -0.007896
#   2020-06-12    0.008104
#   2020-06-15   -0.010692
#   2020-06-16    0.017083
#   2020-06-17    0.005524
#                   ...
#   2022-06-24    0.017760
#   2022-06-27    0.007440
#   2022-06-28    0.007745
#   2022-06-29   -0.030766
#   2022-06-30    0.029472
#   Name: unit_net_value, Length: 498, dtype: float64

print('weights')

# out:
# date        order_book_id  asset_type
# 2020-06-10  000671.XSHE    stock         0.181159
#             603806.XSHG    stock         0.129076
#             002773.XSHE    stock         0.093464
#             000988.XSHE    stock         0.082025
#             601811.XSHG    stock         0.074052
#                                            ...
# 2022-06-30  002460.XSHE    stock         0.004708
#             600316.XSHG    stock         0.002541
#             601117.XSHG    stock         0.002351
#             600079.XSHG    stock         0.001984
#             600588.XSHG    stock         0.000767
# Length: 19797, dtype: float64
```

传入 rqpattr 计算引擎，对策略进行归因

```python
result = rqpattr.performance_attribute(model="equity/factor_v2", daily_weights=weights, daily_return=daily_return,
                               benchmark_info={'type': 'index',  'name': '中证800', 'detail': '000906.XSHG'})


```

混合资产 Brinson 归因

```python

result['returns_decomposition']

#out:
# [{'factor': '总收益',
#   'value': 0.20369010703210916,
#   'children': [{'factor': '交易收益',
#     'value': -0.025843778212483993,
#     'children': None},
#    {'factor': '杠杆收益', 'value': 0.0, 'children': None},
#    {'factor': '持仓收益',
#     'value': 0.2295338852445934,
#     'children': [{'factor': '主动收益',
#       'value': 0.06632185697753212,
#       'children': [{'factor': '可转债收益',
#         'value': 0.0,
#         'children': [{'factor': '可转债配置收益', 'value': 0.0, 'children': None},
#          {'factor': '可转债选择收益', 'value': 0.0, 'children': None}]},
#        {'factor': '基金收益',
#         'value': 0.0,
#         'children': [{'factor': '基金配置收益', 'value': 0.0, 'children': None},
#          {'factor': '基金选择收益', 'value': 0.0, 'children': None}]},
#        {'factor': '指数收益',
#         'value': 0.0,
#         'children': [{'factor': '指数配置收益', 'value': 0.0, 'children': None},
#          {'factor': '指数选择收益', 'value': 0.0, 'children': None}]},
#        {'factor': '期权收益',
#         'value': 0.0,
#         'children': [{'factor': '期权配置收益', 'value': 0.0, 'children': None},
#          {'factor': '期权选择收益', 'value': 0.0, 'children': None}]},
#        {'factor': '期货收益',
#         'value': 0.0,
#         'children': [{'factor': '期货配置收益', 'value': 0.0, 'children': None},
#          {'factor': '期货选择收益', 'value': 0.0, 'children': None}]},
#        {'factor': '港股收益',
#         'value': 0.0,
#         'children': [{'factor': '港股配置收益', 'value': 0.0, 'children': None},
#          {'factor': '港股选择收益', 'value': 0.0, 'children': None}]},
#        {'factor': '现金收益',
#         'value': 0.0,
#         'children': [{'factor': '现金配置收益', 'value': 0.0, 'children': None},
#          {'factor': '现金选择收益', 'value': 0.0, 'children': None}]},
#        {'factor': '股票收益',
#         'value': 0.06632185697753212,
#         'children': [{'factor': '股票配置收益',
#           'value': 3.054056964001931e-06,
#           'children': None},
#          {'factor': '股票选择收益',
#           'value': 0.06631880292056812,
#           'children': None}]},
#        {'factor': '非标资产收益',
#         'value': 0.0,
#         'children': [{'factor': '非标资产配置收益', 'value': 0.0, 'children': None},
#          {'factor': '非标资产选择收益', 'value': 0.0, 'children': None}]}]},
#      {'factor': '基准持仓收益',
#       'value': 0.1632120282670611,
#       'children': [{'factor': '基准收益',
#         'value': 0.1182192041711989,
#         'children': None},
#        {'factor': '穿透效应',
#         'value': 0.04499282409586221,
#         'children': None}]}]}]}]

```

展示组合风格因子主动暴露及主动收益

```python

style_factor_attr = pd.DataFrame(
    result['attribution']['factor_attribution'][0]['factors'])

plt.figure()
style_factor_attr.set_index('factor')['active_exposure'].plot(kind='bar',figsize=(15,7),legend='active_exposure',fontsize=15)
plt.figure()
(style_factor_attr.set_index('factor')['active_return']*100).plot(kind='bar', figsize=(15, 7),legend='active_return',fontsize=15)


```

![组合主动暴露](../img/3.png)
![组合主动风险](../img/4.png)
