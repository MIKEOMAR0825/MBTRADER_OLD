from datetime import datetime

trade_history = []
total_pnl = {
    "realized": 0.0
}
open_trades = {}

# -----------------------------
# Ouvrir une position
# -----------------------------
def open_position(symbol: str, price: float, quantity: float = 1.0,
                  stop_loss: float = None, take_profit: float = None,
                  trade_type: str = "BUY"):

    open_trades[symbol] = {
        "symbol": symbol,
        "entry": price,
        "quantity": quantity,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "type": trade_type,   # ✅ FIX IMPORTANT
        "time_open": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    print(f"🟢 {trade_type} ouvert: {symbol} à {price} | Qty: {quantity}")

# -----------------------------
# Fermer une position
# -----------------------------
def close_position(price: float, reason: str = "SELL", symbol: str = None):

    if symbol is None or symbol not in open_trades:
        print("❌ Aucune position ouverte")
        return

    trade = open_trades[symbol]

    if trade.get("type", "BUY") == "BUY":
        pnl = (price - trade["entry"]) * trade["quantity"]
    else:
        pnl = (trade["entry"] - price) * trade["quantity"]

    trade_record = {
        "symbol": symbol,
        "entry": trade["entry"],
        "exit": price,
        "quantity": trade["quantity"],
        "pnl": round(pnl, 2),
        "time_open": trade["time_open"],
        "time_close": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "reason": reason,
        "action": trade["type"],
        "type": trade["type"]   # ✅ FIX FRONTEND COMPAT
    }

    trade_history.append(trade_record)

    total_pnl["realized"] += pnl

    print(f"🔴 {trade['type']} {symbol} PnL: {round(pnl,2)}")

    del open_trades[symbol]


def get_history(symbol: str = None):
    if symbol:
        return [t for t in trade_history if t["symbol"] == symbol]
    return trade_history


def get_total_pnl():
    return {
        "realized": round(total_pnl.get("realized", 0.0), 2)
    }


def get_trade_stats():
    total = len(trade_history)
    wins = len([t for t in trade_history if t["pnl"] > 0])
    losses = total - wins

    avg = total_pnl.get("realized", 0.0) / total if total > 0 else 0

    return {
        "total_trades": total,
        "wins": wins,
        "losses": losses,
        "avg_pnl": round(avg, 2)
    }