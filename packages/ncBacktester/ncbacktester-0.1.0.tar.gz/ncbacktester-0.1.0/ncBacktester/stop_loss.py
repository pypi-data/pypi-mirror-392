"""
Stop Loss Manager Module - Coder C (Part 1)

This module handles stop loss logic, including trailing stop loss.

Coder C Responsibilities (Part 1 - Stop Loss):
1. Implement fixed stop loss logic
2. Implement trailing stop loss logic
3. Track highest price since entry (for trailing stop)
4. Check if stop loss conditions are met

Key Implementation Notes:
- Fixed Stop Loss: Trigger when price drops X% below entry price
- Trailing Stop Loss: Trigger when price drops X% below highest price since entry
- The check_stop_loss() method is called by StrategyExecutor at each timestep
- You need to track the highest price since entry for trailing stops

Important:
- Stop loss should only apply when in a long position
- Consider both fixed and trailing stops - if both provided, use the more restrictive one
- Return (should_trigger: bool, stop_price: float) tuple
"""

from typing import Optional, Tuple


class StopLossManager:
    """
    Manages stop loss logic for trades.
    
    Coder C: Implement the check_stop_loss() method and helper methods.
    
    Supports:
    - Fixed stop loss: Exits if price drops X% from entry
    - Trailing stop loss: Exits if price drops X% from highest price since entry
    
    Attributes:
        stop_loss_pct: Fixed stop loss percentage (e.g., 0.05 for 5%)
        trailing_stop_pct: Trailing stop loss percentage
    """
    
    def __init__(
        self,
        stop_loss_pct: Optional[float] = None,
        trailing_stop_pct: Optional[float] = None
    ):
        """
        Initialize StopLossManager.
        
        Args:
            stop_loss_pct: Fixed stop loss percentage (e.g., 0.05 = 5%)
            trailing_stop_pct: Trailing stop loss percentage
        """
        self.stop_loss_pct = stop_loss_pct
        self.trailing_stop_pct = trailing_stop_pct
    
    def check_stop_loss(
        self,
        entry_price: float,
        current_price: float,
        highest_price_since_entry: float
    ) -> Tuple[bool, float]:
        """
        Check if stop loss should be triggered.
        
        Coder C: Implement this method.
        
        This method should:
        1. Check fixed stop loss (if stop_loss_pct provided)
           - Trigger if current_price <= entry_price * (1 - stop_loss_pct)
        2. Check trailing stop loss (if trailing_stop_pct provided)
           - Trigger if current_price <= highest_price_since_entry * (1 - trailing_stop_pct)
        3. If both provided, use the more restrictive (higher) stop price
        4. Return whether to trigger and at what price
        
        Args:
            entry_price: Price at which position was entered
            current_price: Current market price
            highest_price_since_entry: Highest price reached since entry
        
        Returns:
            Tuple of (should_trigger: bool, stop_price: float)
            If should_trigger is True, stop_price is the price at which to execute
        """
        # Coder C - Implement this method
        # 
        # Steps:
        # 1. Calculate fixed stop price if stop_loss_pct provided
        # 2. Calculate trailing stop price if trailing_stop_pct provided
        # 3. Determine which stop is more restrictive (higher price)
        # 4. Check if current_price has breached the stop
        # 5. Return (True/False, stop_price)
        
        fixed_stop = self._calculate_fixed_stop_price(entry_price)
        trailing_stop = self._calculate_trailing_stop_price(highest_price_since_entry)
        
        active_stops = []
        if fixed_stop is not None:
            active_stops.append(fixed_stop)
        if trailing_stop is not None:
            active_stops.append(trailing_stop)

        if not active_stops:
            # No stop loss is active
            return (False, 0.0)
            
        # The effective stop loss is the most restrictive (highest) price
        effective_stop_price = max(active_stops)
        
        # Check if the current price is at or below the stop level
        should_trigger = current_price <= effective_stop_price
        
        return (should_trigger, effective_stop_price)
    
    def _calculate_fixed_stop_price(self, entry_price: float) -> Optional[float]:
        """
        Calculate fixed stop loss price.
        
        Coder C: Implement this helper method.
        
        Args:
            entry_price: Entry price
        
        Returns:
            Stop loss price or None if not applicable
        """
        # : Coder C - Implement this method
        if self.stop_loss_pct is None:
            return None
        return entry_price * (1.0 - self.stop_loss_pct)
        
    
    def _calculate_trailing_stop_price(
        self,
        highest_price: float
    ) -> Optional[float]:
        """
        Calculate trailing stop loss price.
        
        Coder C: Implement this helper method.
        
        Args:
            highest_price: Highest price since entry
        
        Returns:
            Trailing stop price or None if not applicable
        """
        # : Coder C - Implement this method
        if self.trailing_stop_pct is None:
            return None
        return highest_price * (1.0 - self.trailing_stop_pct)
        

