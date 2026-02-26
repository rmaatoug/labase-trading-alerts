import os
from dotenv import load_dotenv
try:
    from src.alpaca_client import connect_alpaca
except ImportError:
    from alpaca_client import connect_alpaca

if __name__ == "__main__":
    from pathlib import Path
    env_path = Path(__file__).parent / '.env'
    if not env_path.exists():
        env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
    alpaca = connect_alpaca()
    orders = alpaca.get_orders(status='open')
    found = False
    for order in orders:
        if order.symbol == 'AAPL':
            print(f"Ordre ouvert AAPL: qty={order.qty}, side={order.side}, status={order.status}, type={order.type}")
            found = True
    if not found:
        print("Aucun ordre ouvert AAPL trouvé.")
