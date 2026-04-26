def choose_strategy(df):

    ema_fast = df["ema"].iloc[-1]

    # EMA slow réelle (plus stable que rolling mean)
    ema_slow = df["close"].ewm(span=50, adjust=False).mean().iloc[-1]

    # tendance directionnelle
    trend_strength = abs(ema_fast - ema_slow) / ema_slow

    # volatilité marché
    volatility = df["close"].pct_change().std()

    # -----------------------------
    # TREND MODE
    # -----------------------------
    if trend_strength > 0.002 and volatility > 0.0003:
        return "TREND"

    # -----------------------------
    # SCALPING MODE
    # -----------------------------
    return "SCALPING"