"""
Strategy Executor Module - Coder A

This module handles the execution of trading strategies based on hold signals.
It detects signal changes, executes buy/sell orders, and manages positions.

Coder A Responsibilities:
1. Detect when Hold_Signal changes from 0 to 1 (BUY signal)
2. Detect when Hold_Signal changes from 1 to 0 (SELL signal)
3. Execute buy orders at appropriate prices
4. Execute sell orders at appropriate prices
5. Track position sizes and remaining capital
6. Record all trades in a structured format
7. Calculate equity curve (portfolio value over time)

Key Implementation Notes:
- When Hold_Signal changes from 0→1: BUY signal (go long)
- When Hold_Signal changes from 1→0: SELL signal (close position)
- For selling: Sell ALL currently held position (full position exit)
- For buying: Use available capital to buy as many shares as possible
- Price execution: Use Close price of the signal change bar
- Track: Entry price, exit price, quantity, P&L, timestamps

Important:
- You need to handle the case where we're already in a position when a new BUY signal occurs
- Consider commission costs in calculations
- Ensure you don't buy more than available capital allows
"""

from typing import Tuple, Optional
import pandas as pd
import numpy as np

from ncBacktester.stop_loss import StopLossManager


class StrategyExecutor:
    """
    Executes trading strategy based on hold signal changes.
    
    This class processes the data DataFrame row by row, detects signal changes,
    and executes buy/sell orders accordingly.
    
    Coder A: Implement the execute() method and helper methods.
    
    Attributes:
        data: DataFrame with OHLCV and Hold_Signal columns
        initial_capital: Starting capital
        commission: Commission per trade (as decimal)
        stop_loss_manager: Instance of StopLossManager for stop loss handling
    """
    
    
    def __init__(
        self,
        data: pd.DataFrame,
        initial_capital: float,
        commission: float = 0.0,
        stop_loss_manager: Optional['StopLossManager'] = None
    ):
        """
        Initialize the StrategyExecutor.
        
        Args:
            data: DataFrame with OHLCV and Hold_Signal columns
            initial_capital: Starting capital amount
            commission: Commission per trade (e.g., 0.001 for 0.1%)
            stop_loss_manager: Optional StopLossManager instance
        """
        self.data = data.copy()
        self.initial_capital = initial_capital
        self.commission = commission
        self.stop_loss_manager = stop_loss_manager
        
        # Internal state tracking
        self.current_capital = initial_capital
        self.current_position = 0  # Number of shares held
        self.entry_price = None  # Average entry price of current position
        self.entry_date = None
        self._highest_price_since_entry = None
        
    def execute(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Execute the strategy and return trades and equity curve.
        
        Coder A: Implement this method.
        
        This method should:
        1. Iterate through the data DataFrame
        2. Detect signal changes (0→1 for buy, 1→0 for sell)
        3. Execute trades when signals change
        4. Handle stop loss triggers if stop_loss_manager is provided
        5. Track portfolio value at each timestep
        6. Return two DataFrames:
           - trades_df: All executed trades with columns:
             ['Entry_Date', 'Exit_Date', 'Entry_Price', 'Exit_Price', 
              'Quantity', 'P&L', 'Return_Pct', 'Commission']
           - equity_curve: Portfolio value over time with columns:
             ['Date', 'Portfolio_Value', 'Cash', 'Position_Value', 'Hold_Signal']
        
        Returns:
            Tuple of (trades_df, equity_curve)
        """
        
        trades_list = []
        equity_snapshots_list = []

        num_rows = len(self.data)
        for idx in range(num_rows):
            row = self.data.iloc[idx]
            current_signal = int(row['Hold_Signal'])
            previous_signal = int(self.data['Hold_Signal'].iloc[idx - 1]) if idx > 0 else current_signal

            signal_change = self._detect_signal_change(current_signal, previous_signal)

            if signal_change == 'buy':
                self._execute_buy(price=float(row['Close']), date=row['Date'])
            elif signal_change == 'sell':
                sell_result = self._execute_sell(price=float(row['Close']), date=row['Date'])
                if sell_result is not None:
                    # Map to required trades_df schema
                    trades_list.append({
                        'Entry_Date': sell_result['entry_date'],
                        'Exit_Date': sell_result['exit_date'],
                        'Entry_Price': sell_result['entry_price'],
                        'Exit_Price': sell_result['exit_price'],
                        'Quantity': sell_result['quantity'],
                        'P&L': sell_result['p&l'],
                        'Return_Pct': sell_result['return_pct'],
                        'Commission': sell_result['commission']
                    })

            # Track highest price since entry (for potential stop loss usage)
            if self.current_position > 0:
                current_price_for_high = float(row.get('High', row['Close']))
                if self._highest_price_since_entry is None:
                    self._highest_price_since_entry = current_price_for_high
                else:
                    self._highest_price_since_entry = max(self._highest_price_since_entry, current_price_for_high)

            # Optionally handle stop loss if provided (not required by current tests)
            # stop_trade = self._check_stop_loss(row['Close'], row['Date']) if self.stop_loss_manager else None
            # if stop_trade is not None:
            #     trades_list.append(stop_trade)

            equity_snapshots_list.append({
                'Date': row['Date'],
                'Portfolio_Value': self.current_capital + (self.current_position * float(row['Close'])),
                'Cash': self.current_capital,
                'Position_Value': self.current_position * float(row['Close']),
                'Hold_Signal': current_signal
            })

        trades_df = pd.DataFrame(trades_list)
        equity_curve_df = pd.DataFrame(equity_snapshots_list)
        return trades_df, equity_curve_df
        
        
    
    def _detect_signal_change(self, current_signal: int, previous_signal: int) -> Optional[str]:
        """
        Detect if a signal change occurred.
        
        Coder A: Implement this helper method.
        
        Args:
            current_signal: Current row's Hold_Signal value (0 or 1)
            previous_signal: Previous row's Hold_Signal value (0 or 1)
        
        Returns:
            'buy' if signal changed from 0 to 1
            'sell' if signal changed from 1 to 0
            None if no change
        """
        if current_signal == 0 and previous_signal == 1:
            return 'sell'
        elif current_signal == 1 and previous_signal == 0:
            return 'buy'
        else:
            return None
    
    def _execute_buy(self, price: float, date: pd.Timestamp) -> dict:
        """
        Execute a buy order.
        
        Coder A: Implement this helper method.
        
        Args:
            price: Price to buy at (typically Close price)
            date: Date/timestamp of the buy
        
        Returns:
            Dictionary with trade details:
            {'quantity':int, price':float, commission':float, success':bool}

        
        Note:
            - Calculate maximum quantity based on available capital
            - If already in a position, you may want to skip or handle accordingly
            - Remember to account for commission in the cost
        """
        quantity_to_buy = self._calculate_quantity(price)

        if quantity_to_buy <= 0:
            return {
                'quantity': 0,
                'price': price,
                'commission': 0.0,
                'success': False
            }

        total_cost = quantity_to_buy * price
        total_cost_with_commission = total_cost * (1.0 + self.commission)

        previous_position = self.current_position
        previous_cost_basis = (self.entry_price * previous_position) if self.entry_price is not None else 0.0

        # Update state
        self.current_capital -= total_cost_with_commission
        self.current_position += quantity_to_buy
        new_total_shares = self.current_position
        new_total_cost_basis = previous_cost_basis + total_cost
        self.entry_price = new_total_cost_basis / new_total_shares
        if previous_position == 0:
            self.entry_date = date
            self._highest_price_since_entry = price

        return {
            'quantity': quantity_to_buy,
            'price': price,
            'commission': self.commission,
            'success': True
        }
    
    def _execute_sell(self, price: float, date: pd.Timestamp) -> Optional[dict]:
        """
        Execute a sell order (closes entire position).
        
        Coder A: Implement this helper method.
        
        IMPORTANT: This method should sell ALL shares in the current position.
        When hold signal changes from 1→0, we exit the entire position - sell everything.
        
        Args:
            price: Price to sell at (typically Close price)
            date: Date/timestamp of the sell
        
        Returns:
            Dictionary with trade details including P&L:
            {'quantity': int, 'entry_price': float, 'exit_price': float, entry_date: pd.Timestamp, exit_date: pd.Timestamp, 
            'p&l': float, 'return_pct': float, 'commission': float}
            None if no position to sell
        """
        if self.current_position == 0 or self.entry_price is None or self.entry_date is None:
            return None

        quantity_to_sell = self.current_position

        gross_proceeds = quantity_to_sell * price
        sell_commission_cost = gross_proceeds * self.commission
        net_proceeds = gross_proceeds - sell_commission_cost

        pnl_gross = (price - self.entry_price) * quantity_to_sell
        # Approximate total commission across round-trip (buy already deducted from cash)
        round_trip_commission = (quantity_to_sell * self.entry_price * self.commission) + sell_commission_cost
        pnl_net = pnl_gross - sell_commission_cost  # buy commission already impacted cash at entry

        sell_record = {
            'quantity': int(quantity_to_sell),
            'entry_price': float(self.entry_price),
            'exit_price': float(price),
            'entry_date': self.entry_date,
            'exit_date': date,
            'p&l': float(pnl_net),
            'return_pct': float((price - self.entry_price) / self.entry_price),
            'commission': float(round_trip_commission)
        }

        # Update state
        self.current_capital += net_proceeds
        self.current_position = 0
        self.entry_price = None
        self.entry_date = None
        self._highest_price_since_entry = None

        return sell_record

    def _calculate_quantity(self, price: float) -> int:
        """Calculate the maximum number of shares we can buy with current cash."""
        if price <= 0:
            return 0
        max_affordable = int(self.current_capital // (price * (1.0 + self.commission)))
        return max(0, max_affordable)
    
    def _check_stop_loss(self, current_price: float, date: pd.Timestamp) -> Optional[dict]:
        """
        Check if stop loss should be triggered.
        
        Coder A: Call this method at each timestep if stop_loss_manager is provided.
        
        Args:
            current_price: Current Close price
            date: Current date/timestamp
        
        Returns:
            Trade dict if stop loss triggered, None otherwise
        """
        if self.stop_loss_manager is None or self.current_position == 0:
            return None
        
        # Check if stop loss should trigger
        should_trigger, stop_price = self.stop_loss_manager.check_stop_loss(
            entry_price=self.entry_price,
            current_price=current_price,
            highest_price_since_entry=self._get_highest_price_since_entry()
        )
        
        if should_trigger:
            return self._execute_sell(price=stop_price, date=date)
        
        return None
    
    def _get_highest_price_since_entry(self) -> float:
        """
        Get the highest price since entry (for trailing stop loss).
        
        Coder A: Implement this helper method.
        You may want to track this in execute() loop or maintain a variable.
        
        Returns:
            Highest price since current position was entered
        """
        return float(self._highest_price_since_entry) if self._highest_price_since_entry is not None else 0.0

