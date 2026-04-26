import pandas as pd

# -----------------------------
# RSI (version plus réactive)
# -----------------------------
def calculate_rsi_series(prices: pd.Series, period: int = 14) -> pd.Series:

    delta = prices.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # 🔥 EMA smoothing au lieu de SMA (beaucoup mieux pour trading)
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()

    rs = avg_gain / (avg_loss.replace(0, 1e-10))

    return 100 - (100 / (1 + rs))


def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
    rsi = calculate_rsi_series(prices, period)
    return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0


# -----------------------------
# EMA
# -----------------------------
def calculate_ema(prices: pd.Series, period: int = 20) -> pd.Series:
    return prices.ewm(span=period, adjust=False).mean()


# -----------------------------
# MACD (normalisé)
# -----------------------------
def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal_period: int = 9):

    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()

    macd = ema_fast - ema_slow
    signal = macd.ewm(span=signal_period, adjust=False).mean()

    # 🔥 normalisation (important pour IA multi-crypto)
    macd_norm = macd / prices
    signal_norm = signal / prices

    return macd_norm, signal_norm


# -----------------------------
# FULL INDICATORS
# -----------------------------
def add_indicators(prices: pd.Series):

    df = pd.DataFrame({"close": prices})

    df["rsi"] = calculate_rsi_series(df["close"])

    df["ema"] = calculate_ema(df["close"])

    macd, signal = calculate_macd(df["close"])
    df["macd"] = macd
    df["macd_signal"] = signal

    # 🔥 feature supplémentaire TRÈS utile pour ton selector
    df["ema_slope"] = df["ema"].diff()

    # clean
    df.dropna(inplace=True)

    return df