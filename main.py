# app.py

from flask import Flask, render_template, request, jsonify
import config
from bot.trader import start_auto_trading
from bot.engine import start_engine, stop_engine
from bot.logger import get_history, get_total_pnl
from services.binance_client import get_account_balance
from services.market_data import get_latest_prices

app = Flask(__name__)

SECRET_KEY = "12345"

def check_auth(req) -> bool:
    """
    Vérifie la clé API dans l'en-tête
    """
    return req.headers.get("X-API-KEY") == SECRET_KEY

# -----------------------------
# État du bot
# -----------------------------
BOT_STATE = {
    "running": False
}

# -----------------------------
# Dashboard
# -----------------------------
@app.route("/")
def dashboard():
    return render_template("dashboard.html")

# -----------------------------
# Activer / désactiver trading auto
# -----------------------------
@app.route("/toggle_trade", methods=["POST"])
def toggle_trade():
    #if not check_auth(request):
    #    return jsonify({"error": "Unauthorized"}), 401

    if not BOT_STATE["running"]:
        config.AUTO_TRADING = True
        start_engine()
        BOT_STATE["running"] = True
        print("🟢 Trading automatique ACTIVÉ")
        return jsonify({"status": "ON"})

    else:
        config.AUTO_TRADING = False
        stop_engine()
        BOT_STATE["running"] = False
        print("🔴 Trading automatique DÉSACTIVÉ")
        return jsonify({"status": "OFF"})

# -----------------------------
# Simulation
# -----------------------------
@app.route("/simulate", methods=["POST"])
def simulate():
    if not check_auth(request):
        return jsonify({"error": "Unauthorized"}), 401

    if BOT_STATE["running"]:
        return jsonify({"error": "Bot déjà en cours"}), 400

    start_auto_trading()
    return jsonify({"status": "trade checked"})

# -----------------------------
# Status général
# -----------------------------
@app.route("/status")
def status():
    return jsonify({
        "auto_trading": config.AUTO_TRADING,
        "testnet": config.USE_TESTNET
    })

from bot.trader import current_positions
from services.market_data import get_latest_prices
from bot.logger import get_total_pnl

@app.route("/bot_status")
def bot_status():
    # 1️⃣ Solde
    balance_data = get_account_balance()
    balance = {
        "available": balance_data.get("available", 0.0),
        "locked": balance_data.get("locked", 0.0)
    }

    # 2️⃣ PnL total réalisé
    total_pnl_dict = get_total_pnl()  # maintenant c'est directement un dict

    # 3️⃣ PnL non réalisé pour positions ouvertes
    unrealized_pnl = 0.0
    from bot.logger import open_trades
    for trade in list(open_trades.values()):
        symbol = trade["symbol"]
        entry = trade["entry"]
        qty = trade["quantity"]
        current_price = get_latest_prices(symbol).iloc[-1]
        if trade.get("type", "BUY") == "BUY":
            pnl = (current_price - entry) * qty
        else:
            pnl = (entry - current_price) * qty
        unrealized_pnl += pnl

    # 4️⃣ Somme du PnL total
    total_realized = sum(total_pnl_dict.values())
    total_value = total_realized + unrealized_pnl

    # 5️⃣ JSON à retourner
    return jsonify({
        "running": BOT_STATE["running"],
        "auto_trading": config.AUTO_TRADING,
        "balance": balance,
        "pnl": {
            "realized": round(total_realized, 2),
            "unrealized": round(unrealized_pnl, 2),
            "total": round(total_value, 2)
        }
    })    
        
# -----------------------------
# Historique des trades
# -----------------------------
@app.route("/trades")
def trades():
    history = get_history()
    return jsonify(history)

@app.route("/pnl")
def pnl():
    history = get_history()
    return jsonify({
        "total_pnl": sum([t["pnl"] for t in history]),
        "total_trades": len(history),
        "wins": len([t for t in history if t["pnl"] > 0]),
        "losses": len([t for t in history if t["pnl"] < 0]),
        "history": history[-10:]  # derniers 10 trades
    })
    
# -----------------------------
# Solde
# -----------------------------
@app.route("/balance")
def balance():
    balances = get_account_balance()
    return {
        "available": balances["available"],
        "locked": balances["locked"]
    }
    
    
from bot.logger import trade_history, open_trades
from services.market_data import get_latest_prices

@app.route("/all_trades")
def all_trades():

    all_trades_list = []

    # CLOSED TRADES
    for t in trade_history:
        all_trades_list.append({
            "symbol": t["symbol"],
            "action": t["action"],
            "entry": t["entry"],
            "exit": t["exit"],
            "time_open": t["time_open"],
            "time_close": t["time_close"],
            "pnl": t["pnl"],
            "reason": t.get("reason", "-"),
            "status": "CLOSED"
        })

    # OPEN TRADES (FIXED)
    for symbol, trade in open_trades.items():

        current_price = get_latest_prices(symbol).iloc[-1]
        trade_type = trade.get("type", "BUY")

        if trade_type == "BUY":
            pnl = (current_price - trade["entry"]) * trade["quantity"]
        else:
            pnl = (trade["entry"] - current_price) * trade["quantity"]

        all_trades_list.append({
            "symbol": symbol,
            "action": trade_type,
            "entry": trade["entry"],
            "exit": None,
            "time_open": trade["time_open"],
            "time_close": None,
            "pnl": round(pnl, 2),
            "reason": "-",
            "status": "OPEN"
        })

    all_trades_list.sort(
        key=lambda x: x.get("time_open", ""),
        reverse=True
    )

    return jsonify(all_trades_list[:20])
    
# app.py ou routes.py

from flask import jsonify
from bot.trader import current_positions
from services.market_data import get_latest_prices

@app.route("/dashboard_data")
def dashboard_data():
    positions_data = []

    for symbol, trades in list(current_positions.items()):  # trades = liste de positions
        current_price = get_latest_prices(symbol).iloc[-1]  # prix actuel

        for trade in trades:
            # calcul du PnL en temps réel
            if trade["type"] == "BUY":
                pnl = (current_price - trade["entry"]) * trade["quantity"]
            else:  # SELL
                pnl = (trade["entry"] - current_price) * trade["quantity"]

            positions_data.append({
                "symbol": symbol,
                "entry": trade["entry"],
                "quantity": trade["quantity"],
                "stop_loss": trade["stop_loss"],
                "take_profit": trade["take_profit"],
                "type": trade["type"],
                "pnl": round(pnl, 2)
            })

    return jsonify(positions_data)


# -----------------------------
# Lancer Flask
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)