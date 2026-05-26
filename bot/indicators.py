# bot/indicators.py

import pandas as pd

# -----------------------------
# RSI
# -----------------------------
def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
    """
    Retourne le dernier RSI arrondi
    """
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi.iloc[-1], 2)

def calculate_rsi_series(prices: pd.Series, period: int = 14) -> pd.Series:
    """
    Retourne la série complète de RSI
    """
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# -----------------------------
# EMA
# -----------------------------
def calculate_ema(prices: pd.Series, period: int = 20) -> pd.Series:
    """
    Retourne la série EMA
    """
    return prices.ewm(span=period, adjust=False).mean()

# -----------------------------
# MACD
# -----------------------------
def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal_period: int = 9):
    """
    Retourne le MACD et le signal line
    """
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    
    macd = ema_fast - ema_slow
    signal = macd.ewm(span=signal_period, adjust=False).mean()
    return macd, signal

# -----------------------------
# Fonction complète multi-indicateurs
# -----------------------------
def add_indicators(prices: pd.Series):
    """
    Retourne un DataFrame avec RSI, EMA, MACD et signal line
    """
    df = pd.DataFrame(prices).copy()
    df.columns = ['close']
    
    df['rsi'] = calculate_rsi_series(df['close'])
    df['ema'] = calculate_ema(df['close'])
    macd, signal = calculate_macd(df['close'])
    df['macd'] = macd
    df['macd_signal'] = signal
    
    return df