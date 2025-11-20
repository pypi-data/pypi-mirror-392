"""
Main Backtest class that orchestrates the backtesting process.

This is the main entry point for users of the package.
Combines StrategyExecutor, MetricsCalculator, and Plotter.
"""

from typing import Optional, Dict, Any
import pandas as pd

from ncBacktester.strategy_executor import StrategyExecutor
from ncBacktester.metrics import MetricsCalculator
from ncBacktester.stop_loss import StopLossManager
from ncBacktester.plotter import Plotter


class Backtest:
    """
    Main Backtest class that orchestrates the entire backtesting process.
    
    This class coordinates between:
    - StrategyExecutor (Coder A): Executes trades based on signals
    - MetricsCalculator (Coder B): Calculates performance metrics
    - StopLossManager (Coder C): Manages stop loss logic
    - Plotter (Coder C): Creates static visualizations
    
    Usage:
        >>> from ncBacktester import Backtest
        >>> bt = Backtest(
        ...     data=df,  # DataFrame with OHLCV + Hold Signal
        ...     initial_capital=10000
        ... )
        >>> results = bt.run()
        >>> bt.plot()
    
    Attributes:
        data (pd.DataFrame): DataFrame containing OHLCV data and hold signals
        initial_capital (float): Starting capital for backtesting
        stop_loss_pct (float): Stop loss percentage (0.05 = 5%)
        trailing_stop_pct (float): Trailing stop loss percentage
        commission (float): Commission per trade (default 0.0)
        
    Note:
        The data DataFrame must contain columns:
        - Open, Low, High, Close, Volume (OHLCV)
        - Hold_Signal (0 or 1, where 1 = hold, 0 = don't hold)
    """
    
    def __init__(
        self,
        data: pd.DataFrame,
        initial_capital: float = 10000.0,
        stop_loss_pct: Optional[float] = None,
        trailing_stop_pct: Optional[float] = None,
        commission: float = 0.0
    ):
        """
        Initialize the Backtest engine.
        
        Args:
            data: DataFrame with OHLCV columns and Hold_Signal column
            initial_capital: Starting capital amount
            stop_loss_pct: Stop loss percentage (e.g., 0.05 for 5%)
            trailing_stop_pct: Trailing stop loss percentage
            commission: Commission per trade (as decimal, e.g., 0.001 for 0.1%)
        """
        self.data = data.copy()
        self.initial_capital = initial_capital
        self.stop_loss_pct = stop_loss_pct
        self.trailing_stop_pct = trailing_stop_pct
        self.commission = commission
        
        # Initialize components
        self.strategy_executor = None
        self.stop_loss_manager = None
        self.metrics_calculator = None
        self.plotter = None
        
        # Results storage
        self.trades_df = None
        self.equity_curve = None
        self.metrics = None
        
    def run(self) -> Dict[str, Any]:
        """
        Run the backtest.
        
        This method:
        1. Validates the input data
        2. Initializes the StrategyExecutor and StopLossManager
        3. Executes trades through StrategyExecutor
        4. Applies stop loss logic through StopLossManager
        5. Calculates metrics through MetricsCalculator
        6. Prepares results for plotting
        
        Returns:
            Dictionary containing:
            - 'trades': DataFrame of all executed trades
            - 'equity_curve': DataFrame with portfolio value over time
            - 'metrics': Dictionary of calculated metrics
            - 'final_value': Final portfolio value
        """
        # Validate data
        self._validate_data()
        
        # Initialize components
        self.stop_loss_manager = StopLossManager(
            stop_loss_pct=self.stop_loss_pct,
            trailing_stop_pct=self.trailing_stop_pct
        )
        
        self.strategy_executor = StrategyExecutor(
            data=self.data,
            initial_capital=self.initial_capital,
            commission=self.commission,
            stop_loss_manager=self.stop_loss_manager
        )
        
        # Execute strategy
        self.trades_df, self.equity_curve = self.strategy_executor.execute()
        
        # Calculate metrics
        self.metrics_calculator = MetricsCalculator(
            trades_df=self.trades_df,
            equity_curve=self.equity_curve,
            initial_capital=self.initial_capital
        )
        self.metrics = self.metrics_calculator.calculate_all_metrics()
        
        # Initialize plotter
        self.plotter = Plotter(
            data=self.data,
            trades_df=self.trades_df,
            equity_curve=self.equity_curve,
            metrics=self.metrics
        )
        
        return {
            'trades': self.trades_df,
            'equity_curve': self.equity_curve,
            'metrics': self.metrics,
            'final_value': self.equity_curve['Portfolio_Value'].iloc[-1] if len(self.equity_curve) > 0 else self.initial_capital
        }
    
    def plot(self, save_path: Optional[str] = None):
        """
        Generate and display/save static plots.
        
        Args:
            save_path: Optional path to save the plot image. If None, displays the plot.
        """
        if self.plotter is None:
            raise ValueError("Must run backtest (call .run()) before plotting")
        
        self.plotter.plot_all(save_path=save_path)
    
    def _validate_data(self):
        """Validate that the input DataFrame has required columns."""
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'Hold_Signal']
        missing_cols = [col for col in required_cols if col not in self.data.columns]
        
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Check for NaN values in critical columns
        critical_cols = ['Close', 'Hold_Signal']
        for col in critical_cols:
            if self.data[col].isna().any():
                raise ValueError(f"Column '{col}' contains NaN values")

