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

### 4. Box Spread Arbitrage (`boxx.py`, `boxx_etf.py`)
- **Box Spread Scanner**: Real-time scanners for CFFEX index and ETF options that identify risk-free arbitrage opportunities.
- **Profit Modeling**: Incorporates precise commission and exercise cost calculations for margin detection.
- **Usage**:
  ```bash
  python boxx.py <data_dir/YYYY-MM-DD> [output_dir]
  python boxx_etf.py <data_dir/YYYY-MM-DD> [output_dir]
  ```

### 5. Winning Option Selection (`evaluate_combinations.py`)
- **Strategy Optimizer**: Backtests combinations of technical indicators (RSI, MACD, etc.) to identify high-probability entry points for OTM options.
- **Ranking System**: Ranks indicator sets by win rate and drawdown to isolate "winning" setups.
- **Usage**:
  ```bash
  python evaluate_combinations.py
  ```

## Getting Started

1. Activate the environment: `source venv/bin/activate`
2. Consult `doc/` for API specifications before implementation.
3. Use `examples/` as templates for new strategies.

*Note: All Ricequant API usage must adhere to the rules defined in `GEMINI.md`.*
