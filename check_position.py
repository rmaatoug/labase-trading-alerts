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
    positions = alpaca.get_positions()
    for pos in positions:
        if pos.symbol == 'AAPL':
            print(f"Position AAPL: quantité={pos.qty}, prix moyen={pos.avg_entry_price}, valeur de marché={pos.market_value}")
            break
    else:
        print("Aucune position AAPL trouvée.")
