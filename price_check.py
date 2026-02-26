
# Chargement automatique des variables d'environnement
from dotenv import load_dotenv
load_dotenv()
alpaca = connect_alpaca()
alpaca.disconnect()

from dotenv import load_dotenv
load_dotenv()
try:
    from src.alpaca_client import connect_alpaca
except ImportError:
    from alpaca_client import connect_alpaca

alpaca = connect_alpaca()
bars = alpaca.get_historical_bars('AAPL', days=1, timeframe='1Min')
if bars:
    last_bar = bars[-1]
    print(f"AAPL last price: {last_bar.close} (time: {last_bar.date})")
    print(f"High: {last_bar.high}, Low: {last_bar.low}, Volume: {last_bar.volume}")
else:
    print("No price data available")
alpaca.disconnect()
