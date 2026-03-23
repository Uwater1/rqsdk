# Download Stock-Linked Options Task

## Objective
Download all stock-linked options data (including index ETF options and CFFEX index options) and save them in parquet format using clean, English/alphanumeric names.

## Checklist
- [x] Identify all ETF options and CFFEX index options underlying symbols.
- [x] Map underlying symbols to clean names (e.g., `510050.XSHG` -> `50ETF`, `510300.XSHG` -> `300ETF`, `IO` -> `IO`).
- [x] Write a python script to query instruments and download historical prices for each option category.
- [x] Save the results into `.parquet` files with `_instruments.parquet` and `_historical_prices.parquet` suffixes.
- [x] Execute the python script and verify `.parquet` files are generated.
- [x] Update `requirements.txt` to include `pyarrow`.
- [x] Move all `.parquet` files to the `data/` directory.

