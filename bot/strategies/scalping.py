# bot/strategies/scalping.py


def scalping_signal(df):

    rsi = df['rsi'].iloc[-1]

    print(f"📈 RSI={rsi:.2f}")

    if rsi < 35:
        return "BUY"

    elif rsi > 65:
        return "SELL"

    return "HOLD"