#!/bin/bash
# Script de vérification accès US Market Data pour Alpaca
# Usage: ./scripts/check_alpaca_marketdata.sh

set -e
cd "$(dirname "$0")/.."

if ! grep -q '^ALPACA_BASE_URL=' .env; then
  echo "❌ ALPACA_BASE_URL manquant dans .env" >&2
  exit 1
fi

URL=$(grep '^ALPACA_BASE_URL=' .env | cut -d'=' -f2-)
KEY=$(grep '^ALPACA_API_KEY=' .env | cut -d'=' -f2-)
SECRET=$(grep '^ALPACA_SECRET_KEY=' .env | cut -d'=' -f2-)

if [[ -z "$URL" || -z "$KEY" || -z "$SECRET" ]]; then
  echo "❌ Clés Alpaca manquantes dans .env" >&2
  exit 1
fi

# Test accès Market Data

resp=$(curl -s -H "APCA-API-KEY-ID: $KEY" -H "APCA-API-SECRET-KEY: $SECRET" "$URL/v2/account")
if echo "$resp" | grep -q '"status":"ACTIVE"'; then
  echo "✅ Accès API Alpaca OK"
else
  echo "❌ Problème accès API Alpaca : $resp" >&2
  exit 2
fi

# Test accès US Market Data (endpoint spécifique)
resp2=$(curl -s -H "APCA-API-KEY-ID: $KEY" -H "APCA-API-SECRET-KEY: $SECRET" "$URL/v2/account/configurations")
if echo "$resp2" | grep -q 'us_market_data'; then
  echo "✅ US Market Data activé"
else
  echo "⚠️  US Market Data non détecté dans la config. Vérifiez votre abonnement sur le dashboard Alpaca."
fi
