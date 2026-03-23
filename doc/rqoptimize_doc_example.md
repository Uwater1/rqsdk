## 代码示例

### 净利润增长率指数增强策略

```python
import rqdatac
from rqoptimizer import *
from rqdatac import *
rqdatac.init()
### 净利润增长率指数增强策略
def generate_stock_pool(date, indicator_series, stock_number):

    industry_classification = rqdatac.zx_instrument_industry(indicator_series.index.tolist(), date)['first_industry_name']
    index_weight = rqdatac.index_weights('000300.XSHG', date)

    # 优先选入沪深300成分股中权重大于3%的股票
    prioritized_stock_pool = index_weight[index_weight >= 0.03].index.tolist()
    prioritized_stock_industry = industry_classification.loc[prioritized_stock_pool]

    remaining_indicator_series = indicator_series.drop(prioritized_stock_pool)
    selected_stock = prioritized_stock_pool

    for i in list(industry_classification.unique()):
    # 除优先选入股票外，在每个行业选取指标得分最高的股票，使得每一个行业股票总数量为5
        industry_prioritized_stock = prioritized_stock_industry[prioritized_stock_industry == i].index.tolist()
        industry_stocks = industry_classification[industry_classification==i].drop(industry_prioritized_stock)
        industry_selected_stock = remaining_indicator_series.loc[industry_stocks.index].sort_values()[-(stock_number-len(industry_prioritized_stock)):].index.tolist()
        selected_stock = selected_stock + industry_selected_stock

    return selected_stock

bounds = {'*': (0, 0.05)}
date = '2014-07-16' # 优化日期
# Wildcard的exclude列表为空，即对所有风格/行业设置相同的约束，其中使用中信行业分类
cons = [
    WildcardIndustryConstraint(lower_limit=-0.01, upper_limit=0.01, relative=True, hard=False),
    WildcardStyleConstraint(lower_limit=-0.3, upper_limit=0.3, relative=True, hard=False)
]

# 获取前一交易日中证800成分股的净利润增长率（TTM）
previous_date = rqdatac.get_previous_trading_date(date)
index_component = rqdatac.index_components('000906.XSHG', previous_date)
indicator_series = rqdatac.get_factor(index_component, 'net_profit_growth_ratio_ttm', previous_date,previous_date,expect_df=False).dropna()

selected_stock = generate_stock_pool(previous_date, indicator_series, stock_number=5)

# 个股指标得分范围调整至0.1-1.1，避免权重过分集中于部分指标得分较大的个股
adjusted_series = ((indicator_series.loc[selected_stock] - indicator_series.loc[selected_stock].min()) / (
        indicator_series.loc[selected_stock].max() - indicator_series.loc[selected_stock].min())) + 0.1

portfolio_weight = portfolio_optimize(selected_stock, date, bnds=bounds, cons=cons, benchmark='000300.XSHG', objective=MaxIndicator(indicator_series=adjusted_series))
```

### 贝塔风格增强策略

```python
from rqoptimizer import *
from rqoptimizer.utils import *
import rqdatac
from rqdatac import *
import pandas as pd
rqdatac.init()
def update_stock_pool(date):
    index_weight = rqdatac.index_weights('000300.XSHG', date)

    # 沪深300中权重大于3%的股票设定为第一优先级股票
    first_priority_stock_pool = index_weight[index_weight >= 0.03].index.tolist()
    first_priority_stock_pool = pd.Series(index=first_priority_stock_pool,data=0)

    # 去除第一优先级股票后，其它股票中选取beta暴露度最高的前50只作为第二优先级股票
    index_component_800 = rqdatac.index_components('000906.XSHG', date)
    beta_exposure = rqdatac.get_factor_exposure(index_component_800,date,date,factors='beta')
    beta_exposure.index = beta_exposure.index.droplevel('date')
    second_priority_stock_pool = beta_exposure['beta'].drop(first_priority_stock_pool.index).sort_values()[-50:]
    second_priority_stock_pool = pd.Series(index=second_priority_stock_pool.index, data=1)

    # 中证800中去除前两个优先级后，剩余股票作为优先级最低的股票
    last_priority_stock_pool = list(set(index_component_800).difference(set(first_priority_stock_pool.index)).difference(set(second_priority_stock_pool.index)))
    last_priority_stock_pool = pd.Series(index=last_priority_stock_pool, data=2)
    stock_pool = pd.concat([first_priority_stock_pool, second_priority_stock_pool, last_priority_stock_pool])

    return stock_pool

# 生成行业选股约束
def generate_industry_selected_stock(stock_number):
    industry_factors = ['农林牧渔', '采掘', '化工', '钢铁', '有色金属', '电子', '家用电器', '食品饮料', '纺织服装', '轻工制造', '医药生物', '公用事业', '交通运输', '房地产', '商业贸易', '休闲服务','综合', '建筑材料',  '建筑装饰', '电气设备', '国防军工', '计算机', '传媒', '通信', '银行', '证券','保险','多元金融', '汽车', '机械设备']

    industry_selected_stock = []
    for i in industry_factors:
        industry_stock = IndustryStockCountTarget(i, IndustryClassification.SWS_1, stock_number)
        industry_selected_stock.append(industry_stock)

    return industry_selected_stock


date = '2019-02-28' # 优化日期
stock_pool = update_stock_pool(date)

# 设定每个行业中选择5只股票
industry_selected_stock = generate_industry_selected_stock(stock_number=5)
target_style = pd.Series({'size': 0, 'beta': 1, 'book_to_price': 0, 'earnings_yield': 0, 'growth': 0, 'leverage': 0,
                          'liquidity': 0, 'momentum': 0, 'non_linear_size': 0, 'residual_volatility': 0})

stock_list = stock_select(stock_pool, industry_selected_stock, date, TargetStyleScore(target_style=target_style, relative=True),benchmark='000300.XSHG')
bounds = {'*': (0, 0.05)}

# 添加行业约束
cons = [WildcardIndustryConstraint(lower_limit=-0.01, upper_limit=0.01, relative=True, hard=False)]
objective = MinStyleDeviation({'size': 0, 'beta': 1, 'book_to_price': 0, 'earnings_yield': 0, 'growth': 0, 'leverage': 0, 'liquidity': 0, 'momentum': 0, 'non_linear_size': 0, 'residual_volatility': 0}, relative=True, priority=target_style)
portfolio_weight = portfolio_optimize(stock_list, date, bnds=bounds, cons=cons, benchmark='000300.XSHG', objective=objective)

```