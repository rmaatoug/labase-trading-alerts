
# Chargement automatique des variables d'environnement
from dotenv import load_dotenv
load_dotenv()
alpaca = connect_alpaca()
alpaca.disconnect()

from dotenv import load_dotenv
load_dotenv()
from src.alpaca_client import connect_alpaca

alpaca = connect_alpaca()
account = alpaca.get_account()
if account:
    print(f"Equity: ${account.equity}")
    print(f"Cash: ${account.cash}")
    print(f"Buying Power: ${account.buying_power}")
    print(f"Portfolio Value: ${account.portfolio_value}")
else:
    print("Failed to fetch account info")
alpaca.disconnect()
