I want to upgrade the current boxx_near.py from a prove of concept to a production ready thing

Here's some additional constrain I faced:

1. The short boxx have to charge 2*spread margin
2. The long boxx margin spike at 2 days before the strike date (as Shanghai Exchange 's rules)

In order to solve that, here's my solution:

1. For long box and short box, we should actually keep our order book in the ram. If the close position now return > hold to maturity return, (after commission cost) we should close the position immediately. 
2. We shop opening new position 5 days away from maturity. (5 is a Global constant (int) for now, we will adjust it later)
3. If 4 days away from maturity, return > buying cost (after commission cost) , we should close the position immediately. (4 is a Global constant (int) for now, we will adjust it later)

So for backtest ready:

Step 1: Download ETF data using download_etf_options.py (actually, we stop trading )

Step 2: 