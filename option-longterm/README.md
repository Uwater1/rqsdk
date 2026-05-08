# Option Longterm Investment - Project JEPI-CN

This directory contains scripts and research for long-term option investment strategies, specifically focusing on **Covered Call** and **Bull Put Spread** strategies on Chinese ETFs (50ETF, 300ETF, 500ETF).

## Core Strategy
The primary strategy is a "Covered Call + Bull Put Spread" combination, inspired by income-generating funds like JEPI, but adapted for the Chinese market (Project JEPI-CN).

- **Covered Call**: Selling OTM calls against held ETF shares to generate premium income.
- **Bull Put Spread**: Selling OTM put spreads to capture additional premium while limiting downside risk.
- **Strike Selection**: Driven by historical probability distributions (Alpha Finder) and ATM Implied Volatility (IV).

## File Structure

### Backtesting
- `backtest_covered_call.py`: The main backtesting engine. Supports multiple ETFs and dynamic strike selection based on IV regimes.
- `backtest_covered_call*.png`: Visualizations of backtest results (Equity curve, drawdown, etc.).
- `backtest_covered_call*.log`: Detailed logs of executed trades and performance metrics.

### Research & Analysis
- `alpha_finder.py`: Calculates historical 30-day calendar forward return distributions for indices to identify high-probability "alpha" zones for strike selection.
- `research_otm_levels.py`: Research script to evaluate the performance of different OTM strike offsets under various market conditions.
- `research_otm_no_filter.py`: Baseline OTM performance research without technical filters.
- `research_synthetic_otm.py`: Evaluates OTM strategies using synthetic option pricing data.
- `evaluate_combinations.py`: Analyzes the impact of different indicators (SMA, RSI, MACD) on the performance of OTM strategies.

### Documentation
- `STRATEGY.md`: Detailed strategy execution report (in Chinese), including capital structure, position configuration, and risk management rules.

### Utilities
- `numba_utils.py`: Performance-optimized functions for option pricing and metric calculations.

## Getting Started

### 1. Run Alpha Analysis
Identify the historical probabilities for index moves:
```bash
python alpha_finder.py
```

### 2. Run Backtest
Run a backtest for the 300ETF covered call strategy:
```bash
python backtest_covered_call.py --etf 300
```

### 3. Analyze OTM Levels
Research the optimal OTM offsets:
```bash
python research_otm_levels.py --etf 300
```

## Data Dependencies
The scripts expect data to be located in the `../data/` directory (relative to this folder).
