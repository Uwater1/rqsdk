# 使用示例

## 量价因子 范例 1

```python
from rqfactor import *
from rqfactor.extension import *
from rqfactor.engine_v2 import *
import rqdatac
rqdatac.init()

VWAP = Factor('total_turnover') / Factor('volume')
f = (RANK((VWAP - Factor('close'))) / RANK((VWAP + Factor('close'))))

```

## 量价因子 范例 2

```python
from rqfactor import *
from rqfactor.extension import *
from rqfactor.engine_v2 import *
import rqdatac
import numpy as np
import pandas as pd

rqdatac.init()

#定义自定义因子
def buy_volume(order_book_ids,start_date,end_date):
    return rqdatac.get_capital_flow(order_book_ids,start_date,end_date).buy_volume.unstack('order_book_id').reindex(columns=order_book_ids,index =pd.to_datetime(rqdatac.get_trading_dates(start_date,end_date)))

def sell_volume(order_book_ids,start_date,end_date):
    return rqdatac.get_capital_flow(order_book_ids,start_date,end_date).sell_volume.unstack('order_book_id').reindex(columns=order_book_ids,index =pd.to_datetime(rqdatac.get_trading_dates(start_date,end_date)))

BUY_VOLUME = UserDefinedLeafFactor('BUY_VOLUME',buy_volume)
SELL_VOLUME = UserDefinedLeafFactor('SELL_VOLUME',sell_volume)

f = DELTA(MA(BUY_VOLUME-SELL_VOLUME,13)/IF(MA(ABS(BUY_VOLUME-SELL_VOLUME),13) !=0,MA(ABS(BUY_VOLUME-SELL_VOLUME),13),np.nan),3)


d1='20190101'
d2='20200101'

df = execute_factor(f,rqdatac.index_components('000300.XSHG', d1),d1,d2)

#实例化引擎
engine=FactorAnalysisEngine()
#构建管道，对因子进行预处理
engine.append(('neutralization', Neutralization(industry='citics_2019', style_factors=['size','beta','earnings_yield','growth','liquidity','leverage','book_to_price','residual_volatility','non_linear_size'])))
#构建管道，添加因子分析器
engine.append(('rank_ic_analysis', ICAnalysis(rank_ic=True, industry_classification='sws',max_decay=20)))
engine.append(('quantile', QuantileReturnAnalysis(quantile=5, benchmark=None)))
engine.append(('return',FactorReturnAnalysis()))
#调仓周期为1，3，5
result = engine.analysis(df, 'daily', ascending=True, periods=[1,3,5], keep_preprocess_result=True)

```

- 查看因子 IC 分析结果

```python
In[]:
result['rank_ic_analysis'].summary()
Out[]:
                 P_1    	  P_3	        P_5
mean	        0.002531	  -0.005552	  -0.012799
std	          0.062977	  0.064005	  0.060862
positive	    117.000000	118.000000	107.000000
negative	    127.000000	126.000000	137.000000
significance	0.024590	  0.040984	  0.036885
sig_positive	0.012295	  0.004098	  0.008197
sig_negative	0.008197	  0.024590	  0.008197
t_stat	      0.627707	  -1.354970	  -3.284878
p_value	      0.530785	  0.176685	  0.001171
skew	        0.223259	  -0.401776	  -0.088231
kurtosis	    0.176964	  0.414680	  -0.099484
ir	          0.040185	  -0.086743	  -0.210293

```

- 绘制因子分组收益率结果

```python
result['quantile'].show()

```

![分组多空收益率结果](./img/f-2-quantile-1-plot.png)
![分组换手率结果-P_1](./img/f-2-quantile-2-plot.png)
![分组累积收益率结果-P_1](./img/f-2-quantile-3-plot.png)
![分组换手率结果-P_3](./img/f-2-quantile-4-plot.png)
![分组累积收益率结果-P_3](./img/f-2-quantile-5-plot.png)
![分组换手率结果-P_5](./img/f-2-quantile-6-plot.png)
![分组累积收益率结果-P_5](./img/f-2-quantile-7-plot.png)

- 绘制因子收益率结果

```python
result['return'].show()

```

![因子收益率结果](./img/f-2-return-plot.png)

## 月度因子（自然月）范例

财务因子比较偏向价值投资，一般持有期会相对较长，这里采用以自然月为收益区间验证财务因子

```python
from rqfactor import *
from rqdatac import *
import pandas as pd
init()


#因子定义
f = RANK((Factor('net_profit_parent_company_ttm_0')/Factor('equity_parent_company_ttm_0')) /(Factor('net_profit_parent_company_ttm_1')/Factor('equity_parent_company_ttm_1')), 'first', True)

d1 = '20210101'
d2 = '20211201'
ids= index_components('000300.XSHG',d1)

#因子数据
df = execute_factor(f,ids,d1,d2)
df = df.resample('BM').last()


#合成每个自然月的收益率数据
returns=get_price_change_rate(ids, start_date=d1, end_date=d2, expect_df=True)+1
#为了使用resample能更便捷聚合收益率数据，这里直接将收益率数据index平移一个交易日
returns.index=get_trading_dates(get_previous_trading_date(returns.index[0]), get_previous_trading_date(returns.index[-1]), market='cn')
returns.columns.name=''
returns.index=pd.DatetimeIndex(returns.index)
#returns.index平移后，聚合的为当月第二个交易日到下一个月第一个交易日的收益率数据
returns=returns.resample('BM').prod()-1
returns.index=pd.DatetimeIndex(returns.index.date)
returns.columns.name=''

# 构建管道，并将因子值和收益率传入分析器中进行计算
engine = FactorAnalysisEngine()
# engine.append(('winzorization-mad', Winzorization(method='mad')))
engine.append(('rank_ic_analysis', ICAnalysis(rank_ic=True, industry_classification='sws',max_decay=10)))
engine.append(('QuantileReturnAnalysis', QuantileReturnAnalysis(quantile=10, benchmark='000300.XSHG')))
result = engine.analysis(df, returns, ascending=True, periods=1, keep_preprocess_result=True)

```

- 查看 IC 分析结果及分组情况

```python
In[]:
result['rank_ic_analysis'].summary()

Out[]:
                   P_1
mean         -0.006272
std           0.106604
positive      7.000000
negative      5.000000
significance  0.333333
sig_positive  0.083333
sig_negative  0.083333
t_stat       -0.203807
p_value       0.842226
skew          0.281141
kurtosis      0.418097
ir           -0.058834

In[]:
result['QuantileReturnAnalysis'].quantile_detail

Out[]:
order_book_id 600183.XSHG 603658.XSHG 601319.XSHG 600637.XSHG 002179.XSHE  \
datetime
2021-01-29            NaN         NaN         NaN         NaN         NaN
2021-02-26             q5          q3          q4          q6          q7
2021-03-31             q5          q3          q4          q6          q7
2021-04-30             q3          q3          q4          q6          q6
2021-05-31             q7          q2          q8          q4          q9
2021-06-30             q7          q2          q8          q4          q9
2021-07-30             q7          q2          q8          q4          q9
2021-08-31             q7          q2          q8          q4          q9
2021-09-30             q9          q2          q7          q2          q3
2021-10-29             q9          q2          q7          q2          q3
2021-11-30             q9          q3          q2          q3          q6
2021-12-31             q9          q3          q2          q3          q6

order_book_id 002050.XSHE 600660.XSHG 600176.XSHG 601877.XSHG 000157.XSHE  \
datetime
2021-01-29            NaN         NaN         NaN         NaN         NaN
2021-02-26             q6          q3          q4          q5          q7
2021-03-31             q6          q3          q4          q5          q7
2021-04-30             q4          q8          q9          q5          q7
2021-05-31             q7          q9         q10          q2          q8
2021-06-30             q7          q9         q10          q2          q8
2021-07-30             q7          q9         q10          q2          q8
2021-08-31             q7          q9         q10          q2          q8
2021-09-30             q5          q8         q10          q5          q2
2021-10-29             q5          q8         q10          q5          q2
2021-11-30             q5          q5         q10          q3          q2
2021-12-31             q5          q5         q10          q3          q2

order_book_id  ... 002311.XSHE 601398.XSHG 601111.XSHG 002384.XSHE  \
datetime       ...
2021-01-29     ...         NaN         NaN         NaN         NaN
2021-02-26     ...          q6          q4         q10          q1
2021-03-31     ...          q6          q4         q10          q1
2021-04-30     ...          q6          q7         q10          q1
2021-05-31     ...          q7          q4          q9          q2
2021-06-30     ...          q7          q4          q9          q2
2021-07-30     ...          q7          q4          q9          q2
2021-08-31     ...          q2          q4          q9          q2
2021-09-30     ...          q3          q6          q1          q3
2021-10-29     ...          q3          q6          q1          q3
2021-11-30     ...          q1          q6         q10          q8
2021-12-31     ...          q1          q6         q10          q8

order_book_id 002594.XSHE 600690.XSHG 002600.XSHE 000661.XSHE 600019.XSHG  \
datetime
2021-01-29            NaN         NaN         NaN         NaN         NaN
2021-02-26            q10          q8          q1          q7          q8
2021-03-31            q10          q8          q1          q7          q8
2021-04-30             q9          q9         q10          q5          q8
2021-05-31             q2          q7          q8          q6         q10
2021-06-30             q2          q7          q8          q6         q10
2021-07-30             q2          q7          q8          q6         q10
2021-08-31             q2          q7          q8          q6         q10
2021-09-30             q1          q8          q1          q5         q10
2021-10-29             q1          q8          q1          q5         q10
2021-11-30             q1          q2          q6          q5          q9
2021-12-31             q1          q2          q6          q5          q9

order_book_id 002008.XSHE
datetime
2021-01-29            NaN
2021-02-26             q9
2021-03-31             q9
2021-04-30             q2
2021-05-31             q9
2021-06-30             q9
2021-07-30             q9
2021-08-31             q9
2021-09-30             q6
2021-10-29             q6
2021-11-30             q9
2021-12-31             q9

[12 rows x 300 columns]

```

- 绘制 IC 分析结果

```python
result['rank_ic_analysis'].show()

```

![因子IC分析结果](./img/f-bm-ic-plot.png)

## F-Score 因子范例

F-Score 因子出自 Piotroski 的论文《Value Investing: The Use of Historical Financial Statement Information to Separate Winners from Losers》，主要从三个维度(profitability、financial leverage/liquidity、operating efficiency)来衡量公司的基本面状况。作者选用了九个好实施的指标，并且每个指标使用“好”或“坏”评判该公司在该指标上的表现。F-Score 因子是这九个指标的加总。
| 指标 | 打分方式 |
|-----|-----|
| 资产收益率 | 大于零为 1，否则为 0 |
| 资产收益率变化率 | 大于零为 1，否则为 0 |
| 经营活动产生的现金流比总资产 | 大于零为 1，否则为 0 |
| 应计收益率 | 大于零为 0，否则为 1 |
| 长期负债率变化 | 大于零为 0，否则为 1 |
| 流动比率变化 | 大于零为 0，否则为 1 |
| 股票是否增发 | 是为 0，否则为 1 |
| 毛利率变化 | 大于零为 1，否则为 0 |
| 资产周转率 | 大于零为 1，否则为 0 |

```python
from rqfactor import *
from rqfactor.extension import *
from rqfactor.engine_v2 import *
import rqdatac as rq
import pandas as pd
rq.init()

import numpy as np
from rqfactor.engine_v2 import execute_factor

#自定义算子，使得因子值大于0时返回1，否则返回0
def fillter(df):
    df[df>0]=1
    df[df<=0]=0
    df=df.fillna(0)
    return df
def Fillter(f):
    return UnaryCrossSectionalFactor(fillter, f)

#自定义算子，使得因子值大于0时返回0，否则返回1
def fillter_1(df):
    df[df<0]=1
    df[df>=0]=0
    df=df.fillna(0)
    return df
def Fillter_1(f):
    return UnaryCrossSectionalFactor(fillter_1, f)



##构建因子

#1.ROA因子，大于0得1分，否则0分
f1 = Fillter(Factor('return_on_asset_ttm'))

#2.Δroa因子，大于0得1分，否则0分
f2 = Fillter(Factor('net_profit_mrq_0')/Factor('total_assets_mrq_0')-Factor('net_profit_mrq_3')/Factor('total_assets_mrq_3'))

#3.cfoa因子，大于0得1分，否则0分
f3 = Fillter(Factor('cash_flow_from_operating_activities_ttm_0')/Factor('total_assets_ttm_0'))

#4.应计利润,小于0得1分，否则0分
f4 = Fillter_1((Factor('profit_from_operation_ttm_0')-Factor('cash_flow_from_operating_activities_ttm_0'))/Factor('total_assets_ttm_0'))

#5.ΔLEVER,小于0得1分，否则0分,需对银行类别进行处理
def lever(order_book_ids, start_date, end_date):
    trading_dates=rq.get_trading_dates(start_date, end_date, market='cn')
    a=rq.get_factor(order_book_ids,'non_current_liabilities_mrq_0',start_date, end_date)['non_current_liabilities_mrq_0']
    b=rq.get_factor(order_book_ids,'total_assets_mrq_0',start_date, end_date)['total_assets_mrq_0']
    lever=a/b
    lever=lever.unstack('order_book_id')
    lever.columns.name=''
    lever.index.name=''
    lever=lever.reset_index(drop = False)
    lever.index=lever[''].tolist()
    lever.index=trading_dates
    lever=lever.drop(columns='')
    for key,value in lever.iteritems():
        if key in rq.get_industry('银行', source='citics', date=end_date):
            lever[key]=rq.get_factor(key,'deposits',start_date, end_date).unstack('order_book_id')['deposits']\
                       +rq.get_factor(key,'bond_payable',start_date, end_date).unstack('order_book_id')['bond_payable']\
                       +rq.get_factor(key,'borrowings_from_central_banks', start_date, end_date).unstack('order_book_id')['borrowings_from_central_banks']
    lever.index = pd.DatetimeIndex(lever.index)
    return lever
LEVER=UserDefinedLeafFactor('LEVER', lever)
f5=Fillter_1(LEVER-REF(LEVER, 252))

#6.ΔLIQUID,大于0得1分，否则0分
def liquid(order_book_ids, start_date, end_date):
    trading_dates=rq.get_trading_dates(start_date, end_date, market='cn')
    a=rq.get_factor(order_book_ids,'current_assets',start_date, end_date).fillna(method='pad')
    b=rq.get_factor(order_book_ids,'current_liabilities',start_date, end_date).fillna(method='pad')
    liquid=a['current_assets']/b['current_liabilities']
    liquid=liquid.unstack('order_book_id')
    liquid.columns.name=''
    liquid.index.name=''
    liquid=liquid.reset_index(drop = False)
    liquid.index=liquid[''].tolist()
    liquid.index=trading_dates
    liquid=liquid.drop(columns='')
    for key,value in liquid.iteritems():
        bf_obi=rq.get_industry('银行', source='citics', date=end_date)+rq.get_industry('非银行金融', source='citics', date=end_date)
        a=['cash_equivalent','deposits_of_interbank','precious_metals','lend_capital',
           'financial_asset_held_for_trading','derivative_financial_assets','resale_financial_assets',
            'interest_receivable','loans_advances_to_customers','financial_asset_available_for_sale'
              'financial_asset_hold_to_maturity','loan_account_receivables']
        b=['borrowings_from_central_banks','deposits_of_interbank','borrowings_capital','financial_liabilities',
              'derivative_financial_liabilities','buy_back_security_proceeds','deposits','payroll_payable',
                'tax_payable','dividend_payable']
        if key in bf_obi:
            liquid[key]=(rq.get_factor(key,a,start_date,end_date).sum(axis=1)/rq.get_factor(key,b,start_date,end_date).sum(axis=1)).unstack('order_book_id')
    liquid.index=pd.DatetimeIndex(liquid.index)
    return liquid
LIQUID=UserDefinedLeafFactor('LIQUID', liquid)
f6 = Fillter(LIQUID-REF(LIQUID,252))

#7.EQ_OFFER,过去一年是否增发或配售新股,没有增发得1分，否则为0
def eq_offer(order_book_ids, start_date, end_date):
    trading_dates=rq.get_trading_dates(start_date, end_date, market='cn')
    c=pd.DataFrame(columns=order_book_ids,index=trading_dates)
    for i in trading_dates:
        pp=rq.get_private_placement(order_book_ids, start_date=rq.get_previous_trading_date(i,252,market='cn'),
                                 end_date=i, progress='complete',issue_type='private', market='cn')
        for b in pp.index.get_level_values('order_book_id').values:
            c.loc[i, b] = 0
    for i in trading_dates:
        pp=rq.get_private_placement(order_book_ids, start_date=rq.get_previous_trading_date(i,252,market='cn'),
                                 end_date=i, progress='complete',issue_type='private', market='cn')
        for b in pp.index.get_level_values('order_book_id').values:
            c.loc[i, b] = 0
    c=c.fillna(1)
    c.index = pd.DatetimeIndex(c.index)
    return c
f7 = UserDefinedLeafFactor('EQ_OFFER', eq_offer) #自定义因子

#8.ΔMARGIN因子，大于0得1分，否则0分
f8 = Fillter((Factor('operating_revenue_mrq_0')-Factor('total_expense_mrq_0'))/Factor('operating_revenue_mrq_0')\
     -(Factor('operating_revenue_mrq_3')-Factor('total_expense_mrq_3'))/Factor('operating_revenue_mrq_3'))

#9.ΔTURN：最新报告期资产周转率-上年同期资产周转率,大于0得1分，否则0分
f9 =Fillter(Factor('operating_revenue_mrq_0') / Factor('total_assets_mrq_0')-Factor('operating_revenue_mrq_3') / Factor('total_assets_mrq_3'))


f=f1+f2+f3+f4+f5+f6+f7+f8+f9



#检验因子
#print(execute_factor(f, rq.index_components('000300.XSHG', '20180201'), '20180101', '20180201'))
df=execute_factor(f, rq.index_components('000300.XSHG','20150101'), '20150101', '20200101')

engine = FactorAnalysisEngine()
engine.append(('neutralization',Neutralization(industry='sws',style_factors=['size','beta','momentum','growth','book_to_price','residual_volatility','non_linear_size'])))
engine.append(('rank_ic_analysis', ICAnalysis(rank_ic=False, industry_classification='sws')))
engine.append(('QuantileReturnAnalysis', QuantileReturnAnalysis(quantile=3, benchmark='000300.XSHG')))
result = engine.analysis(df, 'daily', ascending=False, periods=22, keep_preprocess_result=True)
# 绘制 IC 结果图
result['rank_ic_analysis'].show()

result['QuantileReturnAnalysis'].show()


```

![IC分析结果](./img/f-score-ic-plot.png)
![因子分组收益率结果-P-1](./img/f-score-quantile-1-plot.png)
![因子分组收益率结果-P-2](./img/f-score-quantile-2-plot.png)
![因子分组收益率结果-P-3](./img/f-score-quantile-3-plot.png)

