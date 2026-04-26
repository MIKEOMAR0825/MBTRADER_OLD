# fetch_data.py
import pandas as pd
from binance.client import Client
import config
import os

client = Client(config.BINANCE_API_KEY, config.BINANCE_SECRET_KEY, testnet=config.USE_TESTNET)

# 🔹 Liste des cryptos à récupérer
SYMBOLS = config.SYMBOLS

# 🔹 Créer dossier si nécessaire
os.makedirs("historical_data", exist_ok=True)

for symbol in SYMBOLS:
    print(f"⏱ Récupération des données pour {symbol} ...")
    klines = client.get_klines(symbol=symbol, interval="1h", limit=1000)
    
    df = pd.DataFrame(klines, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])
    
    df["close"] = df["close"].astype(float)
    df = df[["close"]]
    
    csv_path = f"historical_data/{symbol}.csv"
    df.to_csv(csv_path, index=False)
    print(f"✅ {csv_path} créé")