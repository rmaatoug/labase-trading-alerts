<!-- Generated: guidance for AI coding agents working on labase-trading-alerts -->
# Copilot instructions — labase-trading-alerts

**IMPORTANT** — At each Codespace session start: check `CONVERSATION_CONTEXT.md` in repo root for ongoing decisions and session notes.

Purpose: quick, actionable guidance so an AI assistant can be immediately productive in this repo.

- Big picture:
  - This repo is a trading bot that detects breakout signals on US stocks and executes trades via **Alpaca Markets API** with Telegram alerts. Key examples: [trade_breakout_paper.py](trade_breakout_paper.py), [signal_breakout.py](signal_breakout.py), [price_check.py](price_check.py).
  - Shared integrations live in `src/`: `src/alpaca_client.py` (Alpaca API wrapper) and `src/telegram_client.py` (Telegram POST wrapper). `src/main.py` demonstrates environment loading and basic connectivity checks.

- Runtime & environment (how to run):
  - Install dependencies from `requirements.txt` into a virtualenv: `pip install -r requirements.txt`.
  - Provide environment variables via a `.env` file: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `ALPACA_API_KEY`, `ALPACA_SECRET_KEY`, `ALPACA_BASE_URL`.
  - Run quick connectivity test: `python src/main.py` ([src/main.py](src/main.py#L1-L40)).
  - Run trading script: `python trade_breakout_paper.py` from repo root.

- Integration notes (observed, do not change lightly):
  - Alpaca uses REST API (`alpaca-trade-api` package). No persistent connection needed.
  - Alpaca client wrapper (`src/alpaca_client.py`) provides methods: `get_historical_bars()`, `place_market_order()`, `place_stop_order()`, `get_positions()`, `get_account()`.
  - Telegram helper is a simple POST to `https://api.telegram.org/bot{token}/sendMessage` (see [src/telegram_client.py](src/telegram_client.py#L1-L40)). Errors are raised via `requests.raise_for_status()`.
  - Historical data: `alpaca.get_historical_bars(symbol, days=2, timeframe='5Min')` returns list of bars with: date, open, high, low, close, volume.
  - Orders: `alpaca.place_market_order(symbol, qty, side='buy')` and `alpaca.place_stop_order(symbol, qty, stop_price, side='sell')`.

- Project-specific behaviors and conventions to follow:
  - Single-run scripts: most files are executed directly and are synchronous (no persistent connection).
  - Basic local persistence: `trade_breakout_paper.py` logs trades to `trades_log.csv` and enforces one trade per day per symbol — honour this guard when modifying trade logic.
  - Order placement safeguards: code checks for existing positions and existing stops before placing new orders. Keep these checks when changing execution logic.
  - Environment-first configuration: sensitive values are read from `.env`; do not hardcode tokens/credentials in code.
  - **US stocks only**: Alpaca only supports US markets. Tickers must be US-listed (no EU or crypto).

- Testing & debugging tips:
  - There are no automated tests. Use `src/main.py` to test connectivity with Alpaca and Telegram before running strategies.
  - Test with paper trading first: `ALPACA_BASE_URL=https://paper-api.alpaca.markets/v2`
  - Check account: `python account_check.py`
  - Check price: `python price_check.py`

- Files of interest (quick links):
  - Connectivity sample: [src/main.py](src/main.py#L1-L40)
  - Alpaca helper: [src/alpaca_client.py](src/alpaca_client.py#L1-L300)
  - Telegram helper: [src/telegram_client.py](src/telegram_client.py#L1-L40)
  - Main trading script: [trade_breakout_paper.py](trade_breakout_paper.py#L1-L300)
  - Signal computation: [signal_breakout.py](signal_breakout.py#L1-L50)

- Editing guidance for AI agents (do this first):
  1. Run `python src/main.py` locally to confirm Telegram + Alpaca connectivity.
  2. If modifying order placement, preserve position checks, stop dedup logic, and the daily-trade guard in `trade_breakout_paper.py`.
  3. Update `requirements.txt` when adding packages and keep versions aligned with the project (pinning style is used).
  4. Remember: Alpaca = US stocks only (no `.PA`, `.AS`, `BTC-EUR`, etc.).

If any of these sections are unclear or you'd like me to add CI, tests, or a runbook for local development, tell me which part to expand.
