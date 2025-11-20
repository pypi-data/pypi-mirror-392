"""
Plotter Module - Coder C (Part 2)

This module creates static visualizations of backtest results.

Coder C Responsibilities (Part 2 - Plotting):
1. Create equity curve plot (portfolio value over time)
2. Create trades overlay plot (buy/sell points on price chart)
3. Create drawdown plot
4. Create metrics summary visualization
5. Combine all plots into a comprehensive dashboard

Key Implementation Notes:
- Use matplotlib for static plots (not interactive/dynamic)
- Keep plots simple and clean
- Include key metrics in plot titles or annotations
- Save plots to file if save_path provided, else display

Important:
- Plot equity curve with portfolio value over time
- Overlay trades (green for buys, red for sells) on price chart
- Show drawdown periods
- Display key metrics (Sharpe, Returns, Max DD) on plots
"""

from typing import Optional
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter


class Plotter:
    """
    Creates static visualizations of backtest results.
    
    Coder C: Implement all plotting methods.
    
    Attributes:
        data: Original OHLCV data with dates
        trades_df: DataFrame of executed trades
        equity_curve: DataFrame with portfolio value over time
        metrics: Dictionary of calculated metrics
    """
    
    def __init__(
        self,
        data: pd.DataFrame,
        trades_df: pd.DataFrame,
        equity_curve: pd.DataFrame,
        metrics: dict
    ):
        """
        Initialize the Plotter.
        
        Args:
            data: Original DataFrame with OHLCV data
            trades_df: DataFrame with trade information
            equity_curve: DataFrame with Date and Portfolio_Value
            metrics: Dictionary of calculated metrics
        """
        self.data = data.copy()
        self.trades_df = trades_df.copy()
        self.equity_curve = equity_curve.copy()
        self.metrics = metrics
    
    def plot_all(self, save_path: Optional[str] = None):
        """
        Create all plots in a comprehensive dashboard.
        
        Coder C: Implement this method.
        
        Create a figure with subplots:
        1. Price chart with buy/sell markers
        2. Equity curve
        3. Drawdown chart
        
        Args:
            save_path: Path to save the figure. If None, display it.
        """
        # TODO: Coder C - Implement this method
        # 
        # Steps:
        # 1. Create figure with subplots (use plt.subplots or gridspec)
        # 2. Call plot_price_with_trades() for first subplot
        # 3. Call plot_equity_curve() for second subplot
        # 4. Call plot_drawdown() for third subplot
        # 5. Add title with key metrics
        # 6. Adjust layout
        # 7. Save or show based on save_path
        
        # 1. Create figure with 3 rows, 1 column. Sharex for linked zooming/panning.
        fig, axes = plt.subplots(
            nrows=3, 
            ncols=1, 
            figsize=(15, 20), 
            sharex=True,
            gridspec_kw={'height_ratios': [2, 1, 1]} # Give price chart more space
        )
        
        # 2. Call plot_price_with_trades
        self.plot_price_with_trades(ax=axes[0])
        
        # 3. Call plot_equity_curve
        self.plot_equity_curve(ax=axes[1])
        
        # 4. Call plot_drawdown
        self.plot_drawdown(ax=axes[2])
        
        # 5. Add title with key metrics
        total_return = self.metrics.get('Total Return', 0)
        sharpe = self.metrics.get('Sharpe Ratio', 0)
        max_dd = self.metrics.get('Max Drawdown', 0)
        win_rate = self.metrics.get('Win Rate', 0)
        
        title_str = (
            f"Backtest Results\n"
            f"Total Return: {total_return:.2%} | "
            f"Sharpe Ratio: {sharpe:.2f} | "
            f"Max Drawdown: {max_dd:.2%} | "
            f"Win Rate: {win_rate:.2%}"
        )
        fig.suptitle(title_str, fontsize=16, y=1.0) # y > 1 to avoid overlap
        
        # 6. Adjust layout
        fig.tight_layout(rect=[0, 0.03, 1, 0.96]) # rect to make room for suptitle
        
        # 7. Save or show
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to {save_path}")
            plt.close(fig) # Close figure to free memory
        else:
            plt.show()
    
    def plot_price_with_trades(self, ax: Optional[plt.Axes] = None):
        """
        Plot price chart with buy/sell trade markers.
        
        Coder C: Implement this method.
        
        Args:
            ax: Matplotlib axes to plot on. If None, create new figure.
        
        Returns:
            The axes object
        """
        # TODO: Coder C - Implement this method
        # 
        # Steps:
        # 1. Plot Close price from self.data
        # 2. Mark buy points (green markers) from trades_df Entry_Date, Entry_Price
        # 3. Mark sell points (red markers) from trades_df Exit_Date, Exit_Price
        # 4. Add labels and title
        # 5. Format x-axis dates
        
        if ax is None:
            fig, ax = plt.subplots(figsize=(15, 7))
            
        # 1. Plot Close price
        ax.plot(self.data.index, self.data['Close'], label='Close Price', color='blue', alpha=0.7)
        
        # 2. Mark buy points
        buys = self.trades_df
        ax.scatter(
            buys['Entry_Date'], 
            buys['Entry_Price'], 
            color='green', 
            marker='^', 
            s=60, 
            label='Buy', 
            zorder=5 # Plot on top
        )
        
        # 3. Mark sell points
        sells = self.trades_df
        ax.scatter(
            sells['Exit_Date'], 
            sells['Exit_Price'], 
            color='red', 
            marker='v', 
            s=60, 
            label='Sell', 
            zorder=5 # Plot on top
        )
        
        # 4. Add labels and title
        ax.set_title('Price Chart with Trades')
        ax.set_ylabel('Price')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.5)
        
        # 5. Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        
        return ax
    
    def plot_equity_curve(self, ax: Optional[plt.Axes] = None):
        """
        Plot portfolio equity curve over time.
        
        Coder C: Implement this method.
        
        Args:
            ax: Matplotlib axes to plot on. If None, create new figure.
        
        Returns:
            The axes object
        """
        # TODO: Coder C - Implement this method
        # 
        # Steps:
        # 1. Plot Portfolio_Value from equity_curve
        # 2. Add horizontal line for initial capital (reference)
        # 3. Add annotations for key metrics (total return, Sharpe, etc.)
        # 4. Add labels and title
        # 5. Format x-axis dates
        
        if ax is None:
            fig, ax = plt.subplots(figsize=(15, 7))
        
        # 1. Plot Portfolio_Value
        ax.plot(
            self.equity_curve.index, 
            self.equity_curve['Portfolio_Value'], 
            label='Equity Curve', 
            color='purple'
        )
        
        # 2. Add horizontal line for initial capital
        initial_capital = self.equity_curve['Portfolio_Value'].iloc[0]
        ax.axhline(
            y=initial_capital, 
            color='grey', 
            linestyle='--', 
            label=f'Initial Capital (${initial_capital:,.2f})'
        )
        
        # 3. Add labels and title
        ax.set_title('Portfolio Equity Curve')
        ax.set_ylabel('Portfolio Value ($)')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.5)
        
        # Format Y-axis as currency
        ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f'${y:,.0f}'))
        
        # 4. Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        
        return ax
    
    def plot_drawdown(self, ax: Optional[plt.Axes] = None):
        """
        Plot drawdown chart.
        
        Coder C: Implement this method.
        
        Drawdown = (Peak Value - Current Value) / Peak Value
        
        Args:
            ax: Matplotlib axes to plot on. If None, create new figure.
        
        Returns:
            The axes object
        """
        # TODO: Coder C - Implement this method
        # 
        # Steps:
        # 1. Calculate drawdown from equity_curve Portfolio_Value
        # 2. Plot drawdown as area chart or line
        # 3. Highlight max drawdown period
        # 4. Add labels and title
        # 5. Format x-axis dates
        
        if ax is None:
            fig, ax = plt.subplots(figsize=(15, 7))
            
        # 1. Calculate drawdown
        equity = self.equity_curve['Portfolio_Value']
        # Calculate running peak (cumulative max)
        peak = equity.expanding(min_periods=1).max()
        # Calculate drawdown (as a positive percentage)
        drawdown = (peak - equity) / peak
        
        # 2. Plot drawdown as area chart
        ax.fill_between(drawdown.index, 0, drawdown, color='red', alpha=0.3)
        # Add a line plot for clarity
        ax.plot(drawdown.index, drawdown, color='red', alpha=0.7, label='Drawdown')
        
        # 3. Add labels and title (including Max DD)
        max_dd_val = self.metrics.get('Max Drawdown', drawdown.max())
        ax.set_title(f'Portfolio Drawdown (Max: {max_dd_val:.2%})')
        ax.set_ylabel('Drawdown')
        ax.set_xlabel('Date')
        
        # 4. Format Y-axis as percentage
        ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f'{y:.0%}'))
        ax.set_ylim(bottom=0) # Ensure y-axis starts at 0
        
        ax.grid(True, linestyle='--', alpha=0.5)
        
        # 5. Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

        return ax
    
    def plot_metrics_summary(self, ax: Optional[plt.Axes] = None):
        """
        Create a text summary of key metrics.
        
        Coder C: Optional method - can be used to display metrics in text format.
        
        Args:
            ax: Matplotlib axes to plot on. If None, create new figure.
        
        Returns:
            The axes object
        """
        # TODO: Coder C - Optional: Implement this method
        # Display key metrics in a text box or table format
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 6))

        # Turn off axes
        ax.axis('off')
        
        # Build metrics string
        metrics_str = "Backtest Metrics Summary\n"
        metrics_str += "-" * 26 + "\n\n"
        
        for key, value in self.metrics.items():
            if isinstance(value, float):
                # Format percentages and floats differently
                if "Return" in key or "Drawdown" in key or "Rate" in key:
                    metrics_str += f"{key:<18}: {value: >8.2%}\n"
                else:
                    metrics_str += f"{key:<18}: {value: >8.2f}\n"
            else:
                metrics_str += f"{key:<18}: {str(value): >8}\n"

        # Display text
        ax.text(
            0.05, 0.95, 
            metrics_str, 
            va='top', 
            ha='left', 
            fontsize=12, 
            family='monospace' # Monospace for alignment
        )
        
        return ax

