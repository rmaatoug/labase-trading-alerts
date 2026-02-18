"""
Alpaca client helper for trading operations.
Replaces IBKR client with Alpaca API.
"""

import os
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, StopOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType
from alpaca.trading.models import Order
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
        self.trading_client = TradingClient(self.api_key, self.secret_key, paper="paper" in self.base_url)
        self.data_client = StockHistoricalDataClient(self.api_key, self.secret_key)
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
        self.connected = False
    
    def get_historical_bars(self, symbol, days=2, timeframe='5Min'):
        """
        Get historical bars for a symbol.
        Returns list of bar objects with: date, open, high, low, close, volume
        """
        try:
            end = datetime.now()
            start = end - timedelta(days=days)
            tf_map = {'5Min': TimeFrame.Minute, '1Hour': TimeFrame.Hour, '1Min': TimeFrame.Minute}
            tf = tf_map.get(timeframe, TimeFrame.Minute)
            request_params = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=tf,
                start=start,
                end=end
            )
            bars = self.data_client.get_stock_bars(request_params)
            if symbol in bars:
                bars = bars[symbol]
            else:
                return []
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
        """Get current positions."""
        try:
            positions = self.trading_client.get_all_positions()
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
        """Place a market order."""
        try:
            order_data = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY if side == 'buy' else OrderSide.SELL,
                time_in_force=TimeInForce.DAY
            )
            order = self.trading_client.submit_order(order_data)
            class OrderObj:
                pass
            o = OrderObj()
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
        """Place a stop loss order."""
        try:
            order_data = StopOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.SELL if side == 'sell' else OrderSide.BUY,
                time_in_force=TimeInForce.GTC,
                stop_price=stop_price
            )
            order = self.trading_client.submit_order(order_data)
            class OrderObj:
                pass
            o = OrderObj()
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
        """Get orders."""
        try:
            orders = self.trading_client.get_orders(status=status)
            result = []
            for order in orders:
                class OrderObj:
                    pass
                o = OrderObj()
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

