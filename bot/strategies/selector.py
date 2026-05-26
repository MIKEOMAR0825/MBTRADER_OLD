# bot/strategies/selector.py


def choose_strategy(df):
    ema_fast = df['ema'].iloc[-1]
    ema_slow = df['ema'].rolling(20).mean().iloc[-1]

    # marché en tendance
    if ema_fast > ema_slow:
        return "TREND"
    else:
        return "SCALPING"