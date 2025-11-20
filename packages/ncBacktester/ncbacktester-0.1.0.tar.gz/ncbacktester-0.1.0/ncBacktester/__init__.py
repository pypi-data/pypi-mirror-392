"""
ncBacktester - A Simple Backtesting Engine

A lightweight backtesting engine for evaluating trading strategies
based on hold signals and OHLCV data.
"""

__version__ = "0.1.0"
__author__ = "ncBacktester Team"

from ncBacktester.backtest import Backtest
from ncBacktester.strategy_executor import StrategyExecutor

__all__ = ['Backtest', 'StrategyExecutor']

