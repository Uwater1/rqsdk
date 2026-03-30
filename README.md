# Ricequant SDK Development Workspace

## Directory Structure

- `doc/`: Comprehensive local API documentation and manuals.
- `data/`: Data that include options and stock price 
- `data-deep/`: Ticker-level options data, used to find arbitrage opportunity.


## Research & Strategy Status

### 1. Market Distribution (Alpha Finder)
- **HS300 Skewness**: Research in `data/walkthrough.md` confirms a significant downward skew in 30-day forward returns (Prob <-5pt is ~50% vs Prob >+5pt is ~40%).
- **`alpha_finder.py`**: A dedicated utility to calculate historical return distributions and dynamically determine optimal OTM strike offsets based on skewness.
- **`backtest_covered_call.py`**: Implementation and backtesting of the **Covered Call + Bull Put Spread** strategy on 50/300/500 ETFs. Optimized to prioritize Call-side income while maintaining strict disaster protection on the Put-side.

### 2. Execution & Simulation
- **Spread Model**: Implemented a LightGBM-based bid-ask spread simulation (`spread.py`) to ensure realistic backtesting.
- **Data Infrastructure**: All strategies leverage high-efficiency Parquet databases located in `data/`.

### 3. Option Alpha Research (OTM Levels)
- **`research_otm_levels.py`**: A research tool to analyze win rates and expected returns for OTM options across multiple strike levels (0-5). Supports Short Call and Long Put strategies with customizable entry filters.
- **`filter.txt`**: Comprehensive catalog of 20+ individual technical filters (SMA, RSI, MACD, etc.) detailing their specific impact on win rates and maximum drawdown.
- **`filter2.txt`**: Evaluation and ranking of top-performing *combined* filters. Identifies optimal logic (e.g., Rank 2: Bollinger Upper + ROC Momentum) for minimizing loss while maintaining trade frequency.

### 4. Box Spread Arbitrage (`boxx.py`, `live_boxx_*.py`)
- **Historical Scanner**: `boxx.py` and `boxx_etf.py` identify risk-free arbitrage opportunities in high-frequency historical data.
- **Live Scanners**: `live_boxx_short.py`, `live_boxx_near.py`, and `live_boxx_far.py` provide real-time arbitrage detection for CFFEX and ETF options.
- **Robustness Features**:
  - **Dynamic Staleness Filter**: Automatic quote rejection if data lags by more than 2 seconds.
  - **Expiry-Day Protection**: Filters out contracts expiring today to avoid settlement noise and extreme annualized return inflation.
  - **Defensive Parsing**: Robustly handles both flat and nested bid/ask data formats.
- **Usage**:
  ```bash
  # Historical High-Freq
  python boxx.py <data_dir/YYYY-MM-DD> [output_dir]
  # Historical Daily Snapshot
  python auto-boxx.py <folder_path>
  # Live
  python live_boxx_near.py
  ```

### 5. Winning Option Selection (`evaluate_combinations.py`)
- **Strategy Optimizer**: Backtests combinations of technical indicators (RSI, MACD, etc.) to identify high-probability entry points for OTM options.
- **Ranking System**: Ranks indicator sets by win rate and drawdown to isolate "winning" setups.
- **Usage**:
  ```bash
  python evaluate_combinations.py
  ```

### 6. Synthetic Options (`synthetic_option_pricing.py`)
- **Pricing Pipeline**: `synthetic_option_pricing.py` generates constant-maturity (28-35 days) synthetic option prices and implied volatilities for 50ETF, 300ETF, and 500ETF.
- **Methodology**:
  - Uses Put-Call Parity for robust forward price inference.
  - Numba-accelerated interpolation of total variance and implied yields.
  - Supports holiday-aware target expiry generation.
- **`research_synthetic_otm.py`**: A high-performance research tool using Numba-compiled kernels to analyze win rates, return profiles, and maximum drawdowns for synthetic OTM options.
- **Usage**:
  ```bash
  # Generate Pricing
  python synthetic_option_pricing.py --etf all
  # Run Research
  python research_synthetic_otm.py --etf 300 --years 3
  ```

## Getting Started

1. Activate the environment: `source venv/bin/activate`
2. Consult `doc/` for API specifications before implementation.
3. Use `examples/` as templates for new strategies.

*Note: All Ricequant API usage must adhere to the rules defined in `GEMINI.md`.*
