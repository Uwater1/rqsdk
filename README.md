# Ricequant SDK Development Workspace

## Directory Structure

- `doc/`: Comprehensive local API documentation and manuals.
- `data/`: Data that include options and stock price 

## Research & Strategy Status

### 1. Market Distribution (Alpha Finder)
- **HS300 Skewness**: Research in `data/walkthrough.md` confirms a significant downward skew in 30-day forward returns (Prob <-50pt is ~50% vs Prob >+50pt is ~40%).
- **Strategy Impact**: The Covered Call + Bull Put Spread strategy has been optimized to prioritize Call-side income while maintaining strict disaster protection on the Put-side.

### 2. Execution & Simulation
- **Spread Model**: Implemented a LightGBM-based bid-ask spread simulation (`spread.py`) to ensure realistic backtesting.
- **Data Infrastructure**: All strategies leverage high-efficiency Parquet databases located in `data/`.

### 3. Option Alpha Research (OTM Levels)
- **`research_otm_levels.py`**: A research tool to analyze win rates and expected returns for OTM options across multiple strike levels (0-5). Supports Short Call and Long Put strategies with customizable entry filters.
- **`filter.txt`**: Comprehensive catalog of 20+ individual technical filters (SMA, RSI, MACD, etc.) detailing their specific impact on win rates and maximum drawdown.
- **`filter2.txt`**: Evaluation and ranking of top-performing *combined* filters. Identifies optimal logic (e.g., Rank 2: Bollinger Upper + ROC Momentum) for minimizing loss while maintaining trade frequency.

## Getting Started

1. Activate the environment: `source venv/bin/activate`
2. Consult `doc/` for API specifications before implementation.
3. Use `examples/` as templates for new strategies.

*Note: All Ricequant API usage must adhere to the rules defined in `GEMINI.md`.*
