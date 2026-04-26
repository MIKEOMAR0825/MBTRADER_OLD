def scalping_signal(df):

    rsi = df["rsi"].iloc[-1]
    ema = df["ema"].iloc[-1]
    price = df["close"].iloc[-1]

    ema_prev = df["ema"].iloc[-2] if len(df) > 1 else ema

    trend_up = price > ema and ema > ema_prev
    trend_down = price < ema and ema < ema_prev

    # -----------------------------
    # BUY (RSI + tendance haussière)
    # -----------------------------
    if rsi < 30 and trend_up:
        return "BUY"

    # -----------------------------
    # SELL (RSI + tendance baissière)
    # -----------------------------
    if rsi > 70 and trend_down:
        return "SELL"

    return "HOLD"