# PyBeli

PyBeli is a CLI tool that analyzes stock and crypto tickers using technical analysis indicators to provide insights and predictions about market trends.

## Features

- **Technical Analysis** — SMA, EMA, RSI, MACD and more
- **Multi-Asset Support** — analyze both stocks and cryptocurrencies
- **Backtesting / Paper Trading** — evaluate strategies against historical data

## Usage

```bash
pybeli
```

## Development Setup

**Prerequisites:** [uv](https://docs.astral.sh/uv/getting-started/installation/)

```bash
# Clone and enter the repo
git clone https://github.com/ernman37/pibeli.git
cd pibeli

# Install all dependencies (creates .venv automatically)
uv sync --dev

# Activate the virtual environment
source .venv/bin/activate

# Install pre-commit hooks
pre-commit install
```

## Common Commands

```bash
# Run the CLI
uv run pybeli

# Run tests with coverage
uv run pytest

# Type check
uv run mypy

# Lint + format
uv run ruff check .
uv run ruff format .
```
