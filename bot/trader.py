# bot/trader.py

import os
import pandas as pd
from binance.enums import SIDE_BUY, SIDE_SELL

import config
import joblib

from bot.ai_model import predict_signal
from bot.indicators import add_indicators
from bot.logger import open_position, close_position

from bot.strategies.selector import choose_strategy
from bot.strategies.scalping import scalping_signal

from services.market_data import get_latest_prices
from services.binance_client import place_market_order, get_account_balance


SYMBOLS = config.SYMBOLS

current_positions = {}

MODEL_DIR = "models"
models = {}

# -----------------------------
# LOAD MODELS
# -----------------------------
for symbol in SYMBOLS:
    path = os.path.join(MODEL_DIR, f"model_{symbol}.pkl")
    if os.path.exists(path):
        models[symbol] = joblib.load(path)
        print(f"✅ Modèle chargé pour {symbol}")
    else:
        print(f"⚠️ Modèle manquant {symbol}")


# -----------------------------
# DATA PREP
# -----------------------------
def prepare_dataframe(prices: pd.Series) -> pd.DataFrame:
    df = add_indicators(prices)
    return df.dropna()


# -----------------------------
# MAIN LOOP
# -----------------------------
def start_auto_trading():

    if not config.AUTO_TRADING:
        return

    for symbol in SYMBOLS:

        if symbol not in models:
            continue

        try:
            prices = get_latest_prices(symbol)
            if prices is None or prices.empty:
                continue

            df = prepare_dataframe(prices)

            if len(df) < 50:
                continue

            price = df.iloc[-1]["close"]

            volatility = df["close"].pct_change().std()
            if volatility < 0.0003:
                continue

            strategy = choose_strategy(df)

            if strategy == "TREND":
                signal = predict_signal(models[symbol], df)
            else:
                signal = scalping_signal(df)

            print(f"📊 {symbol} | {strategy} | {price:.2f} | {signal}")

            check_exit(symbol, price)

            if len(current_positions.get(symbol, [])) >= config.MAX_POSITIONS_PER_SYMBOL:
                continue

            if signal == "BUY":
                open_buy(symbol, price, strategy)
            elif signal == "SELL":
                open_sell(symbol, price, strategy)

        except Exception as e:
            print(f"⚠️ Erreur {symbol}: {e}")


# -----------------------------
# BUY
# -----------------------------
def open_buy(symbol, price, strategy):
    global current_positions

    balance = get_account_balance()["available"]

    qty = min(balance * config.RISK_PER_TRADE, config.MAX_TRADE_USDT)

    place_market_order(symbol, SIDE_BUY, qty)

    # TP / SL
    if strategy == "SCALPING":
        sl = price * (1 - config.SCALP_SL)
        tp = price * (1 + config.SCALP_TP)
    else:
        sl = price * (1 - config.STOP_LOSS_PCT)
        tp = price * (1 + config.TAKE_PROFIT_PCT)

    pos = {
        "entry": price,
        "quantity": qty,
        "stop_loss": round(sl, 2),
        "take_profit": round(tp, 2),
        "type": "BUY"
    }

    current_positions.setdefault(symbol, []).append(pos)

    open_position(symbol, price, qty, sl, tp)

    print(f"🟢 BUY {symbol} @ {price:.2f}")


# -----------------------------
# SELL
# -----------------------------
def open_sell(symbol, price, strategy):
    global current_positions

    balance = get_account_balance()["available"]

    qty = min(balance * config.RISK_PER_TRADE, config.MAX_TRADE_USDT)

    place_market_order(symbol, SIDE_SELL, qty)

    if strategy == "SCALPING":
        sl = price * (1 + config.SCALP_SL)
        tp = price * (1 - config.SCALP_TP)
    else:
        sl = price * (1 + config.STOP_LOSS_PCT)
        tp = price * (1 - config.TAKE_PROFIT_PCT)

    pos = {
        "entry": price,
        "quantity": qty,
        "stop_loss": round(sl, 2),
        "take_profit": round(tp, 2),
        "type": "SELL"
    }

    current_positions.setdefault(symbol, []).append(pos)

    open_position(symbol, price, qty, sl, tp)

    print(f"🔻 SELL {symbol} @ {price:.2f}")


# -----------------------------
# EXIT LOGIC
# -----------------------------
def check_exit(symbol, price):

    if symbol not in current_positions:
        return

    for pos in current_positions[symbol][:]:

        pos_type = pos.get("type", "BUY")   # ✅ FIX BUG 'type'
        entry = pos["entry"]

        if pos_type == "BUY":
            if price <= pos["stop_loss"]:
                place_market_order(symbol, SIDE_SELL, pos["quantity"])
                close_position(price, symbol=symbol, reason="SL")
                current_positions[symbol].remove(pos)

            elif price >= pos["take_profit"]:
                place_market_order(symbol, SIDE_SELL, pos["quantity"])
                close_position(price, symbol=symbol, reason="TP")
                current_positions[symbol].remove(pos)

        else:  # SELL
            if price >= pos["stop_loss"]:
                place_market_order(symbol, SIDE_BUY, pos["quantity"])
                close_position(price, symbol=symbol, reason="SL")
                current_positions[symbol].remove(pos)

            elif price <= pos["take_profit"]:
                place_market_order(symbol, SIDE_BUY, pos["quantity"])
                close_position(price, symbol=symbol, reason="TP")
                current_positions[symbol].remove(pos)

    if symbol in current_positions and len(current_positions[symbol]) == 0:
        del current_positions[symbol]