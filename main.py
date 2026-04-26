# app.py

from flask import Flask, render_template, request, jsonify
import config
from bot.trader import start_auto_trading
from bot.engine import start_engine, stop_engine
from bot.logger import get_history, get_total_pnl
from services.binance_client import get_account_balance
from services.market_data import get_latest_prices

from database import db

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trades.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


SECRET_KEY = "12345"

def check_auth(req) -> bool:
    """
    Vérifie la clé API dans l'en-tête
    """
    return req.headers.get("X-API-KEY") == SECRET_KEY


def safe_price(symbol):
    try:
        df = get_latest_prices(symbol)
        if df is None or df.empty:
            return 0.0
        return float(df.iloc[-1])
    except:
        return 0.0
    
    
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

    balance_data = get_account_balance()
    balance = {
        "available": balance_data.get("available", 0.0),
        "locked": balance_data.get("locked", 0.0)
    }

    total_pnl_dict = get_total_pnl()

    unrealized_pnl = 0.0

    from bot.logger import open_trades

    for trade in list(open_trades.values()):
        symbol = trade["symbol"]
        entry = trade["entry"]
        qty = trade["quantity"]

        price = safe_price(symbol)

        if price == 0:
            continue

        if trade.get("type", "BUY") == "BUY":
            pnl = (price - entry) * qty
        else:
            pnl = (entry - price) * qty

        unrealized_pnl += pnl

    total_realized = sum(total_pnl_dict.values())
    equity = balance["available"] + total_realized + unrealized_pnl

    return jsonify({
        "running": BOT_STATE["running"],
        "auto_trading": config.AUTO_TRADING,
        "balance": balance,
        "pnl": {
            "realized": round(total_realized, 2),
            "unrealized": round(unrealized_pnl, 2),
            "total": round(total_realized + unrealized_pnl, 2),
            "equity": round(equity, 2)
        }
    })


# -----------------------------
# Historique des trades
# -----------------------------
@app.route("/trades")
def trades():
    history = get_history()
    return jsonify(history)



from database import Trade

@app.route("/pnl")

def pnl():
    trades = Trade.query.filter_by(status="CLOSED").all()

    profits = [t.profit for t in trades if t.profit is not None]

    wins = [p for p in profits if p > 0]
    losses = [p for p in profits if p < 0]

    total = len(profits)
    total_pnl = sum(profits)

    winrate = (len(wins) / total * 100) if total > 0 else 0

    avg_win = sum(wins) / len(wins) if wins else 0
    avg_loss = sum(losses) / len(losses) if losses else 0

    # 📈 equity curve
    equity = []
    balance = 0
    for p in profits:
        balance += p
        equity.append(round(balance, 2))

    return jsonify({
        "total_pnl": round(total_pnl, 2),
        "total_trades": total,
        "wins": len(wins),
        "losses": len(losses),
        "winrate": round(winrate, 2),
        "avg_win": round(avg_win, 2),
        "avg_loss": round(avg_loss, 2),
        "equity": equity
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

@app.route("/all_trades")
def all_trades():
    all_trades_list = []

    # 🔹 Trades fermés
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

    # 🔹 Trades ouverts
    for symbol, trade in open_trades.items():

        df = get_latest_prices(symbol)

        if df is None or df.empty:
            continue

        current_price = float(df.iloc[-1])
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

    # 🔹 tri
    all_trades_list.sort(key=lambda x: x["time_open"], reverse=True)

    return jsonify(all_trades_list[:20])

# app.py ou routes.py




from flask import jsonify
from bot.trader import current_positions
from services.market_data import get_latest_prices

@app.route("/dashboard_data")
def dashboard_data():

    positions_data = []

    for symbol, trades in list(current_positions.items()):

        price = safe_price(symbol)

        for trade in trades:

            if price == 0:
                pnl = 0
            elif trade["type"] == "BUY":
                pnl = (price - trade["entry"]) * trade["quantity"]
            else:
                pnl = (trade["entry"] - price) * trade["quantity"]

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


with app.app_context():
    db.create_all()

# -----------------------------
# Lancer Flask
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)