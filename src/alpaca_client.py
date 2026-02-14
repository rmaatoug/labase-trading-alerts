"""
Alpaca client helper for trading operations.
Replaces IBKR client with Alpaca API.
"""

import os
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta
import pandas as pd


class AlpacaClient:
    """Wrapper for Alpaca API with methods similar to ib_insync"""
    
    def __init__(self):
        self.api_key = os.getenv('ALPACA_API_KEY')
        self.secret_key = os.getenv('ALPACA_SECRET_KEY')
        self.base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets/v2')
        
        if not self.api_key or not self.secret_key:
            raise ValueError("ALPACA_API_KEY and ALPACA_SECRET_KEY must be set in .env")
        
        # Create REST API client
        self.api = tradeapi.REST(
            key_id=self.api_key,
            secret_key=self.secret_key,
            base_url=self.base_url,
            api_version='v2'
        )
        
        self.connected = False
    
    def connect(self):
        """Test connection to Alpaca API"""
        try:
            account = self.api.get_account()
            self.connected = True
            return True
        except Exception as e:
            print(f"Alpaca connection failed: {e}")
            return False
    
    def disconnect(self):
        """Alpaca is REST API - no persistent connection to close"""
        self.connected = False
    
    def get_historical_bars(self, symbol, days=2, timeframe='5Min'):
        """
        Get historical bars for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            days: Number of days of history to fetch
            timeframe: Bar size ('5Min', '1Hour', etc.)
        
        Returns:
            list of bar objects with: date, open, high, low, close, volume
        """
        try:
            end = datetime.now()
            start = end - timedelta(days=days)
            
            # Format timestamps for API
            start_str = start.strftime('%Y-%m-%d')
            end_str = end.strftime('%Y-%m-%d')
            
            # Get bars using Alpaca API
            bars_df = self.api.get_bars(
                symbol,
                timeframe,
                start=start_str,
                end=end_str,
                limit=10000
            ).df
            
            if bars_df.empty:
                return []
            
            # Convert DataFrame to list of bar objects
            result = []
            for idx, row in bars_df.iterrows():
                class Bar:
                    pass
                b = Bar()
                b.date = idx
                b.open = float(row['open'])
                b.high = float(row['high'])
                b.low = float(row['low'])
                b.close = float(row['close'])
                b.volume = int(row['volume'])
                result.append(b)
            
            return result
        
        except Exception as e:
            print(f"Error fetching bars for {symbol}: {e}")
            return []
    
    def get_positions(self):
        """
        Get current positions.
        
        Returns:
            list of position objects with: symbol, qty, avg_entry_price
        """
        try:
            positions = self.api.list_positions()
            
            # Convert to simple format
            result = []
            for pos in positions:
                class Position:
                    pass
                p = Position()
                p.symbol = pos.symbol
                p.qty = float(pos.qty)
                p.avg_entry_price = float(pos.avg_entry_price)
                p.current_price = float(pos.current_price)
                p.market_value = float(pos.market_value)
                p.unrealized_pl = float(pos.unrealized_pl)
                result.append(p)
            
            return result
        
        except Exception as e:
            print(f"Error fetching positions: {e}")
            return []
    
    def get_account(self):
        """Get account information"""
        try:
            account = self.api.get_account()
            
            class Account:
                pass
            acc = Account()
            acc.equity = float(account.equity)
            acc.cash = float(account.cash)
            acc.buying_power = float(account.buying_power)
            acc.portfolio_value = float(account.portfolio_value)
            
            return acc
        
        except Exception as e:
            print(f"Error fetching account: {e}")
            return None
    
    def place_market_order(self, symbol, qty, side='buy'):
        """
        Place a market order.
        
        Args:
            symbol: Stock symbol
            qty: Quantity to buy/sell
            side: 'buy' or 'sell'
        
        Returns:
            order object with status
        """
        try:
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type='market',
                time_in_force='day'
            )
            
            # Convert to simple format
            class Order:
                pass
            o = Order()
            o.id = order.id
            o.symbol = order.symbol
            o.qty = float(order.qty)
            o.status = order.status
            o.side = order.side
            o.type = order.type
            
            return o
        
        except Exception as e:
            print(f"Error placing market order for {symbol}: {e}")
            return None
    
    def place_stop_order(self, symbol, qty, stop_price, side='sell'):
        """
        Place a stop loss order.
        
        Args:
            symbol: Stock symbol
            qty: Quantity to sell
            stop_price: Stop loss price
            side: 'buy' or 'sell' (usually 'sell' for protective stop)
        
        Returns:
            order object with status
        """
        try:
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type='stop',
                time_in_force='gtc',  # Good till cancelled
                stop_price=stop_price
            )
            
            # Convert to simple format
            class Order:
                pass
            o = Order()
            o.id = order.id
            o.symbol = order.symbol
            o.qty = float(order.qty)
            o.stop_price = float(stop_price)
            o.status = order.status
            o.side = order.side
            o.type = order.type
            
            return o
        
        except Exception as e:
            print(f"Error placing stop order for {symbol}: {e}")
            return None
    
    def get_orders(self, status='open'):
        """
        Get orders.
        
        Args:
            status: 'open', 'closed', or 'all'
        
        Returns:
            list of order objects
        """
        try:
            orders = self.api.list_orders(status=status)
            
            # Convert to simple format
            result = []
            for order in orders:
                class Order:
                    pass
                o = Order()
                o.id = order.id
                o.symbol = order.symbol
                o.qty = float(order.qty)
                o.status = order.status
                o.side = order.side
                o.type = order.type
                
                if hasattr(order, 'stop_price') and order.stop_price:
                    o.stop_price = float(order.stop_price)
                
                result.append(o)
            
            return result
        
        except Exception as e:
            print(f"Error fetching orders: {e}")
            return []
    
    def cancel_order(self, order_id):
        """Cancel an order by ID"""
        try:
            self.api.cancel_order(order_id)
            return True
        except Exception as e:
            print(f"Error cancelling order {order_id}: {e}")
            return False


# Helper function for backward compatibility
def connect_alpaca():
    """Connect to Alpaca API (similar to connect_ibkr)"""
    client = AlpacaClient()
    if client.connect():
        return client
    else:
        raise ConnectionError("Failed to connect to Alpaca API")

