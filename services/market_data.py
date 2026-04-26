import pandas as pd
import time
from services.binance_client import client

# -----------------------------
# CACHE
# -----------------------------
_cache_seconds = 10
_cached_data = {}  # (symbol, interval, limit)

# -----------------------------
# Récupération OHLCV
# -----------------------------
def get_latest_prices(symbol: str = "BTCUSDT", interval: str = "1m", limit: int = 100) -> pd.Series:
    """
    Récupère les prix de clôture Binance avec cache sécurisé
    """

    now = time.time()
    cache_key = (symbol, interval, limit)

    # 🔹 cache check
    if cache_key in _cached_data:
        cached = _cached_data[cache_key]
        if now - cached["last_fetch"] < _cache_seconds:
            return cached["df"]["close"]

    try:
        klines = client.get_klines(
            symbol=symbol,
            interval=interval,
            limit=limit
        )

        df = pd.DataFrame(klines, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume",
            "number_of_trades", "taker_buy_base",
            "taker_buy_quote", "ignore"
        ])

        # -----------------------------
        # Nettoyage SAFE
        # -----------------------------
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # supprimer données invalides
        df.dropna(inplace=True)

        # -----------------------------
        # index temps
        # -----------------------------
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
        df.set_index("open_time", inplace=True)

        # -----------------------------
        # cache update
        # -----------------------------
        _cached_data[cache_key] = {
            "df": df,
            "last_fetch": now
        }

        return df["close"]

    except Exception as e:
        print(f"❌ Market data error {symbol}: {e}")
        return pd.Series(dtype=float)