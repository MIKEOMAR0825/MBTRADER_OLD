# bot/strategies/scalping.py


def scalping_signal(df):

    rsi = df['rsi'].iloc[-1]

    print(f"📈 RSI={rsi:.2f}")

    if rsi < 45:
        return "BUY"

    elif rsi > 55:
        return "SELL"

    return "HOLD"