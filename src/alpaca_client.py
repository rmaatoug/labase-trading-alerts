"""
Alpaca client helper for trading operations.
Replaces IBKR client with Alpaca API.
"""

import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, StopLossRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta
import pandas as pd


class AlpacaClient:
    """Wrapper for Alpaca API with methods similar to ib_insync"""
    
    def __init__(self):
        self.api_key = os.getenv('ALPACA_API_KEY')
        self.secret_key = os.getenv('ALPACA_SECRET_KEY')
        self.base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
        
        if not self.api_key or not self.secret_key:
            raise ValueError("ALPACA_API_KEY and ALPACA_SECRET_KEY must be set in .env")
        
        # Trading client (for orders, positions, account)
        self.trading_client = TradingClient(
            api_key=self.api_key,
            secret_key=self.secret_key,
            paper=True if 'paper' in self.base_url else False
        )
        
        # Data client (for historical data)
        self.data_client = StockHistoricalDataClient(
            api_key=self.api_key,
            secret_key=self.secret_key
        )
        
        self.connected = False
    
    def connect(self):
        """Test connection to Alpaca API"""
        try:
            account = self.trading_client.get_account()
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
            
            # Map timeframe string to TimeFrame enum
            timeframe_map = {
                '1Min': TimeFrame.Minute,
                '5Min': TimeFrame(5, 'Min'),
                '15Min': TimeFrame(15, 'Min'),
                '1Hour': TimeFrame.Hour,
                '1Day': TimeFrame.Day
            }
            
            tf = timeframe_map.get(timeframe, TimeFrame(5, 'Min'))
            
            request_params = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=tf,
                start=start,
                end=end
            )
            
            bars_data = self.data_client.get_stock_bars(request_params)
            
            if symbol not in bars_data:
                return []
            
            bars = bars_data[symbol]
            
            # Convert to simple objects similar to ib_insync format
            result = []
            for bar in bars:
                class Bar:
                    pass
                b = Bar()
                b.date = bar.timestamp
                b.open = float(bar.open)
                b.high = float(bar.high)
                b.low = float(bar.low)
                b.close = float(bar.close)
                b.volume = int(bar.volume)
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
            positions = self.trading_client.get_all_positions()
            
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
            account = self.trading_client.get_account()
            
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
            market_order_data = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL,
                time_in_force=TimeInForce.DAY
            )
            
            order = self.trading_client.submit_order(order_data=market_order_data)
            
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
            # Use stop loss request for protective stops
            from alpaca.trading.requests import StopOrderRequest
            
            stop_order_data = StopOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL,
                time_in_force=TimeInForce.GTC,  # Good till cancelled
                stop_price=stop_price
            )
            
            order = self.trading_client.submit_order(order_data=stop_order_data)
            
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
            from alpaca.trading.requests import GetOrdersRequest
            from alpaca.trading.enums import QueryOrderStatus
            
            status_map = {
                'open': QueryOrderStatus.OPEN,
                'closed': QueryOrderStatus.CLOSED,
                'all': QueryOrderStatus.ALL
            }
            
            request = GetOrdersRequest(
                status=status_map.get(status, QueryOrderStatus.OPEN)
            )
            
            orders = self.trading_client.get_orders(filter=request)
            
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
            self.trading_client.cancel_order_by_id(order_id)
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
