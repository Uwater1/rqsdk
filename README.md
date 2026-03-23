# Ricequant SDK Development Workspace

A specialized development and research environment for Ricequant's quantitative finance toolkits.

## Overview

This project facilitates quantitative research, strategy backtesting, and factor analysis using the Ricequant SDK ecosystem.

## Key Components

- **RQData**: Financial data retrieval (stocks, futures, options, etc.).
- **RQAlpha-Plus**: Strategy backtesting and simulation engine.
- **RQFactor**: Quantitative factor development and calculation.
- **RQOptimizer**: Portfolio optimization and stock selection.
- **RQPAttr**: Performance and risk attribution.

## Directory Structure

- `doc/`: Comprehensive local API documentation and manuals.
- `examples/`: Reference implementations for various strategy types.
- `data/`: Local cache for historical prices and instrument metadata.
- `venv/`: Pre-configured Python 3.6+ virtual environment.

## Getting Started

1. Activate the environment: `source venv/bin/activate`
2. Consult `doc/` for API specifications before implementation.
3. Use `examples/` as templates for new strategies.

*Note: All Ricequant API usage must adhere to the rules defined in `GEMINI.md`.*
