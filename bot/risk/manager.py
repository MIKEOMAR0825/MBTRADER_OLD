# bot/risk/manager.py


def update_risk(position, price):
    entry = position["entry"]

    # Break-even
    if price > entry * 1.01:
        position["stop_loss"] = entry

    # Trailing stop
    if price > entry:
        new_sl = price * 0.98
        position["stop_loss"] = max(position["stop_loss"], new_sl)