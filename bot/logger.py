from datetime import datetime
from database import db, Trade

# -----------------------------
# MEMORY STORAGE
# -----------------------------
trade_history = []
total_pnl = {}

# 🔹 FIX IMPORTANT: multi-trades support
open_trades = {}  # symbol -> list of trades


# -----------------------------
# OPEN POSITION
# -----------------------------
def open_position(symbol, price, quantity, stop_loss, take_profit, trade_type="BUY"):

    trade_data = {
        "symbol": symbol,
        "entry": price,
        "quantity": quantity,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "type": trade_type,
        "time_open": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }

    # 🔹 support multi positions
    open_trades.setdefault(symbol, []).append(trade_data)

    # 🔹 DB
    trade = Trade(
        symbol=symbol,
        type=trade_type,
        entry_price=price,
        quantity=quantity,
        status="OPEN",
        timestamp=datetime.utcnow()
    )

    db.session.add(trade)
    db.session.commit()

    print(f"🟢 OPEN {trade_type} {symbol} @ {price}")


# -----------------------------
# CLOSE POSITION
# -----------------------------
def close_position(price: float, reason: str = "CLOSE", symbol: str = None):

    if symbol is None or symbol not in open_trades or len(open_trades[symbol]) == 0:
        print("❌ No open position")
        return

    # 🔹 take LAST position (safe FIFO logic)
    trade_mem = open_trades[symbol].pop(0)

    # -----------------------------
    # PnL CALCULATION
    # -----------------------------
    if trade_mem["type"] == "BUY":
        pnl = (price - trade_mem["entry"]) * trade_mem["quantity"]
    else:
        pnl = (trade_mem["entry"] - price) * trade_mem["quantity"]

    # -----------------------------
    # DB FIX (avoid wrong trade selection)
    # -----------------------------
    trade_db = Trade.query.filter_by(
        symbol=symbol,
        status="OPEN"
    ).order_by(Trade.timestamp.asc()).first()

    if trade_db:
        trade_db.exit_price = price
        trade_db.profit = pnl
        trade_db.status = "CLOSED"
        db.session.commit()

    # -----------------------------
    # HISTORY
    # -----------------------------
    record = {
        "symbol": symbol,
        "entry": trade_mem["entry"],
        "exit": price,
        "quantity": trade_mem["quantity"],
        "pnl": round(pnl, 2),
        "time_open": trade_mem["time_open"],
        "time_close": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "reason": reason,
        "type": trade_mem["type"]
    }

    trade_history.append(record)

    # -----------------------------
    # TOTAL PNL
    # -----------------------------
    total_pnl[symbol] = total_pnl.get(symbol, 0) + pnl

    print(f"🔴 CLOSE {trade_mem['type']} {symbol} | PnL={round(pnl,2)}")

    # cleanup empty
    if len(open_trades[symbol]) == 0:
        del open_trades[symbol]


# -----------------------------
# HISTORY
# -----------------------------
def get_history(symbol: str = None):
    if symbol:
        return [t for t in trade_history if t["symbol"] == symbol]
    return trade_history


# -----------------------------
# PNL
# -----------------------------
def get_total_pnl(symbol: str = None):
    if symbol:
        return round(total_pnl.get(symbol, 0.0), 2)
    return {s: round(p, 2) for s, p in total_pnl.items()}