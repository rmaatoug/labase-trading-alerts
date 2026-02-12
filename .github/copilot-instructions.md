<!-- Generated: guidance for AI coding agents working on labase-trading-alerts -->
# Copilot instructions — labase-trading-alerts

**IMPORTANT** — At each Codespace session start: check `CONVERSATION_CONTEXT.md` in repo root for ongoing decisions and session notes.

Purpose: quick, actionable guidance so an AI assistant can be immediately productive in this repo.

- Big picture:
  - This repo is a collection of small scripts (root) that interact with Interactive Brokers (IBKR) via `ib_insync` and send alerts via Telegram. Key examples: [trade_breakout_paper.py](trade_breakout_paper.py), [signal_breakout.py](signal_breakout.py), [price_check.py](price_check.py).
  - Shared integrations live in `src/`: `src/ibkr_client.py` (IB connection helper) and `src/telegram_client.py` (Telegram POST wrapper). `src/main.py` demonstrates environment loading and basic connectivity checks.

- Runtime & environment (how to run):
  - Install dependencies from `requirements.txt` into a virtualenv: `pip install -r requirements.txt`.
  - Provide environment variables via a `.env` file or environment: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `IBKR_HOST`, `IBKR_PORT`, `IBKR_CLIENT_ID`.
  - Run quick connectivity test: `python src/main.py` ([src/main.py](src/main.py#L1-L40)).
  - Run trading script examples directly: `python trade_breakout_paper.py` or `python signal_breakout.py` from repo root.

- Integration notes (observed, do not change lightly):
  - IBKR connections use `ib_insync.IB()` and `ib.connect(host, port, clientId=...)`. Scripts pick different `clientId` values (see `trade_breakout_paper.py` clientId=8, `signal_breakout.py` clientId=7, `price_check.py` clientId=3) — avoid clientId collisions when running multiple scripts concurrently.
  - Telegram helper is a simple POST to `https://api.telegram.org/bot{token}/sendMessage` (see [src/telegram_client.py](src/telegram_client.py#L1-L40)). Errors are raised via `requests.raise_for_status()`.
  - Historical data and live orders are handled with `ib.reqHistoricalData(...)`, `ib.placeOrder(...)`, `MarketOrder`, `StopOrder` patterns (see [trade_breakout_paper.py](trade_breakout_paper.py#L1-L220)).

- Project-specific behaviors and conventions to follow:
  - Single-run scripts: most files are intended to be executed directly and are synchronous/blocking (they call `ib.connect()` / `ib.disconnect()` within the script). Prefer lightweight, minimal edits that preserve this flow.
  - Basic local persistence: `trade_breakout_paper.py` logs trades to `trades_log.csv` and enforces one trade per day per symbol — honour this guard when modifying trade logic.
  - Order placement safeguards: code checks for existing positions and existing stops before placing new orders. Keep these checks when changing execution logic.
  - Environment-first configuration: sensitive values are read from environment or `.env`; do not hardcode tokens/credentials in code.

- Testing & debugging tips discovered in repo:
  - There are no automated tests. Use `src/main.py` to test connectivity with IBKR and Telegram before running strategies.
  - Local IBKR host/port defaults in examples: `127.0.0.1:7497` (TWS/IBGateway). Ensure TWS/IBG is running and API access is enabled.

- Files of interest (quick links):
  - Connectivity sample: [src/main.py](src/main.py#L1-L40)
  - IB helper: [src/ibkr_client.py](src/ibkr_client.py#L1-L40)
  - Telegram helper: [src/telegram_client.py](src/telegram_client.py#L1-L40)
  - Entry-level strategy and execution: [trade_breakout_paper.py](trade_breakout_paper.py#L1-L220)
  - Signal computation: [signal_breakout.py](signal_breakout.py#L1-L120)

- Editing guidance for AI agents (do this first):
  1. Run `python src/main.py` locally (or in CI) to confirm Telegram + IBKR connectivity.
 2. If modifying order placement, preserve position checks (`ib.positions()`), stop dedup logic, and the daily-trade guard in `trade_breakout_paper.py`.
 3. If changing `clientId`, scan repo for other scripts to avoid conflicts.
 4. Update `requirements.txt` when adding packages and keep versions aligned with the project (pinning style is used).

If any of these sections are unclear or you'd like me to add CI, tests, or a runbook for local development, tell me which part to expand.
