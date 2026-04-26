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


# 🔹 CONFIG
SYMBOLS = config.SYMBOLS
current_positions = {}

MODEL_DIR = "models"
models = {}

# -----------------------------
# LOAD MODELS
# -----------------------------
for symbol in SYMBOLS:
    model_path = os.path.join(MODEL_DIR, f"model_{symbol}.pkl")
    if os.path.exists(model_path):
        models[symbol] = joblib.load(model_path)
        print(f"✅ Model loaded {symbol}")
    else:
        print(f"⚠️ Missing model {symbol}")


# -----------------------------
# DATA
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

            signal = (
                predict_signal(models[symbol], df)
                if strategy == "TREND"
                else scalping_signal(df)
            )

            print(f"📊 {symbol} | {strategy} | {price:.2f} | {signal}")

            if symbol in current_positions:
                check_exit(symbol, price)

            if len(current_positions.get(symbol, [])) >= config.MAX_POSITIONS_PER_SYMBOL:
                continue

            if signal == "BUY":
                open_buy(symbol, price)

            elif signal == "SELL":
                open_sell(symbol, price)

        except Exception as e:
            print(f"⚠️ Error {symbol}: {e}")


# -----------------------------
# BUY
# -----------------------------
def open_buy(symbol: str, price: float):

    balance = get_account_balance()["available"]

    risk_usdt = min(
        balance * config.RISK_PER_TRADE,
        config.MAX_TRADE_USDT,
        balance
    )

    order = place_market_order(symbol, SIDE_BUY, risk_usdt)

    if order is None:
        print("❌ BUY ORDER FAILED")
        return

    qty = risk_usdt / price

    position = {
        "entry": price,
        "quantity": qty,
        "type": "BUY",
        "stop_loss": price * (1 - config.STOP_LOSS_PCT),
        "take_profit": price * (1 + config.TAKE_PROFIT_PCT)
    }

    current_positions.setdefault(symbol, []).append(position)

    open_position(symbol, price, risk_usdt,
                 position["stop_loss"], position["take_profit"])

    print(f"🟢 BUY {symbol} | qty={qty:.6f} | {price:.2f}")


# -----------------------------
# SELL
# -----------------------------
def open_sell(symbol: str, price: float):

    balance = get_account_balance()["available"]

    risk_usdt = min(
        balance * config.RISK_PER_TRADE,
        config.MAX_TRADE_USDT,
        balance
    )

    order = place_market_order(symbol, SIDE_SELL, risk_usdt)

    if order is None:
        print("❌ SELL ORDER FAILED")
        return

    qty = risk_usdt / price

    position = {
        "entry": price,
        "quantity": qty,
        "type": "SELL",
        "stop_loss": price * (1 + config.STOP_LOSS_PCT),
        "take_profit": price * (1 - config.TAKE_PROFIT_PCT)
    }

    current_positions.setdefault(symbol, []).append(position)

    open_position(symbol, price, risk_usdt,
                 position["stop_loss"], position["take_profit"])

    print(f"🔴 SELL {symbol} | qty={qty:.6f} | {price:.2f}")


# -----------------------------
# EXIT
# -----------------------------
def check_exit(symbol: str, price: float):

    if symbol not in current_positions:
        return

    positions = current_positions[symbol]

    for pos in positions[:]:

        qty = pos["quantity"]
        side = pos["type"]

        if side == "BUY":

            if price <= pos["stop_loss"]:
                print(f"❌ SL BUY {symbol}")
                place_market_order(symbol, SIDE_SELL, qty * price)
                close_position(price, "STOP LOSS", symbol)
                positions.remove(pos)
                continue

            if price >= pos["take_profit"]:
                print(f"💰 TP BUY {symbol}")
                place_market_order(symbol, SIDE_SELL, qty * price)
                close_position(price, "TAKE PROFIT", symbol)
                positions.remove(pos)
                continue

        else:

            if price >= pos["stop_loss"]:
                print(f"❌ SL SELL {symbol}")
                place_market_order(symbol, SIDE_BUY, qty * price)
                close_position(price, "STOP LOSS", symbol)
                positions.remove(pos)
                continue

            if price <= pos["take_profit"]:
                print(f"💰 TP SELL {symbol}")
                place_market_order(symbol, SIDE_BUY, qty * price)
                close_position(price, "TAKE PROFIT", symbol)
                positions.remove(pos)
                continue

    if len(positions) == 0:
        del current_positions[symbol]