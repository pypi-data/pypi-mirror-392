# ncBacktester

A simple backtesting engine for trading strategies, built for learning purposes.

## Overview

ncBacktester is a lightweight Python package for backtesting trading strategies based on hold signals and OHLCV data. Unlike complex backtesting libraries, ncBacktester focuses on simplicity and educational value.

## Features

- **Simple Strategy Execution**: Execute trades based on hold signal changes (0→1 for buy, 1→0 for sell)
- **Performance Metrics**: Calculate Sharpe Ratio, Sortino Ratio, Annualized Returns, Alpha, Beta, and Max Drawdown
- **Stop Loss Support**: Fixed and trailing stop loss functionality
- **Static Visualization**: Simple static plots of equity curves, trades, and drawdowns
- **Easy to Use**: Clean API similar to backtesting.py but simpler

## Installation

```bash
pip install ncBacktester
```

## Quick Start

```python
from ncBacktester import Backtest
import pandas as pd

# Your data should have OHLCV columns + Hold_Signal column
data = pd.DataFrame({
    'Open': [...],
    'High': [...],
    'Low': [...],
    'Close': [...],
    'Volume': [...],
    'Hold_Signal': [0, 0, 1, 1, 0, ...]  # 1 = hold, 0 = don't hold
})

# Create and run backtest
bt = Backtest(
    data=data,
    initial_capital=10000,
    stop_loss_pct=0.05,  # 5% stop loss
    commission=0.001  # 0.1% commission
)

results = bt.run()

# View results
print(results['metrics'])

# Plot results
bt.plot()
```

## Requirements

- Python >= 3.8
- pandas >= 1.3.0
- numpy >= 1.20.0
- matplotlib >= 3.3.0

## Project Structure

```
ncBacktester/
├── ncBacktester/
│   ├── __init__.py
│   ├── backtest.py          # Main Backtest class
│   ├── strategy_executor.py # Strategy execution (Coder A)
│   ├── metrics.py           # Performance metrics (Coder B)
│   ├── stop_loss.py         # Stop loss logic (Coder C)
│   └── plotter.py           # Plotting (Coder C)
├── tests/
│   ├── test_strategy_executor.py  # Tests for Coder A
│   ├── test_metrics.py            # Tests for Coder B
│   ├── test_stop_loss.py          # Tests for Coder C (Part 1)
│   ├── test_plotter.py            # Tests for Coder C (Part 2)
│   └── test_integration.py        # Integration tests
├── setup.py
├── pyproject.toml
└── README.md
```

## How It Works

1. **Signal Processing**: The engine detects when `Hold_Signal` changes:
   - `0 → 1`: Buy signal (go long)
   - `1 → 0`: Sell signal (close position)

2. **Trade Execution**: 
   - On buy: Uses available capital to buy as many shares as possible
   - On sell: Sells entire position
   - Prices executed at Close price of the signal bar

3. **Stop Loss**: 
   - Fixed stop loss: Exits if price drops X% below entry
   - Trailing stop loss: Exits if price drops X% below highest price since entry

4. **Metrics Calculation**: Calculates various performance metrics from the equity curve and trades.

## Testing

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run tests for specific component
pytest tests/test_strategy_executor.py -v  # Coder A
pytest tests/test_metrics.py -v           # Coder B
pytest tests/test_stop_loss.py -v          # Coder C
```

## Development

This project is organized for collaborative development:

- **Coder A**: Strategy execution and trade management (`strategy_executor.py`)
- **Coder B**: Performance metrics calculation (`metrics.py`)
- **Coder C**: Stop loss logic (`stop_loss.py`) and plotting (`plotter.py`)

Each component has detailed docstrings explaining what needs to be implemented.

## Publishing to PyPI

1. Update version in `setup.py` and `ncBacktester/__init__.py`
2. Build the package:
   ```bash
   python setup.py sdist bdist_wheel
   ```
3. Upload to PyPI:
   ```bash
   twine upload dist/*
   ```

## License

MIT License

## Contributing

This is a learning project. Contributions welcome!

## Acknowledgments

Inspired by [backtesting.py](https://github.com/kernc/backtesting.py) but simplified for educational purposes.

