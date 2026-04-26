from binance.client import Client
from binance.enums import ORDER_TYPE_MARKET, SIDE_BUY, SIDE_SELL
import config
import math

# 🔹 Client Binance
client = Client(
    config.BINANCE_API_KEY,
    config.BINANCE_SECRET_KEY,
    testnet=config.USE_TESTNET
)

# 🔹 Testnet URL override
if config.USE_TESTNET:
    client.API_URL = "https://testnet.binance.vision/api/"

# 🔹 Sync time Binance
try:
    server_time = client.get_server_time()
    print(f"⏱ Binance server time: {server_time['serverTime']}")
except Exception as e:
    print(f"❌ Server time error: {e}")


# -----------------------------
# 🔹 MIN NOTIONAL
# -----------------------------
def get_min_notional(symbol: str) -> float:
    info = client.get_symbol_info(symbol)
    for f in info["filters"]:
        if f["filterType"] == "MIN_NOTIONAL":
            return float(f["minNotional"])
    return 5.0


# -----------------------------
# 🔹 BALANCE
# -----------------------------
def get_account_balance() -> dict:
    try:
        info = client.get_account()
        for asset in info["balances"]:
            if asset["asset"] == "USDT":
                return {
                    "available": float(asset["free"]),
                    "locked": float(asset["locked"])
                }
    except Exception as e:
        print(f"❌ Balance error: {e}")

    return {"available": 0.0, "locked": 0.0}


# -----------------------------
# 🔹 LOT SIZE
# -----------------------------
def get_lot_size(symbol: str) -> tuple:
    info = client.get_symbol_info(symbol)
    for f in info["filters"]:
        if f["filterType"] == "LOT_SIZE":
            return float(f["minQty"]), float(f["stepSize"])
    raise Exception("LOT_SIZE introuvable")


# -----------------------------
# 🔹 FORMAT QUANTITY SAFE
# -----------------------------
def format_quantity(quantity: float, step_size: float) -> float:
    precision = int(round(-math.log(step_size, 10)))
    return round(math.floor(quantity / step_size) * step_size, precision)


# -----------------------------
# 🔹 MARKET ORDER
# -----------------------------
def place_market_order(symbol: str, side: str, usdt_amount: float):
    try:
        # 🔹 balance check
        balance = get_account_balance()["available"]
        if usdt_amount > balance:
            raise Exception(f"❌ Insufficient balance: {balance} USDT")

        # 🔹 price
        price = float(client.get_symbol_ticker(symbol=symbol)["price"])

        # 🔹 convert USDT → quantity
        raw_qty = usdt_amount / price

        min_qty, step_size = get_lot_size(symbol)
        quantity = format_quantity(raw_qty, step_size)

        # 🔹 validations
        if quantity <= 0:
            raise Exception("❌ Invalid quantity after formatting")

        min_notional = get_min_notional(symbol)
        value = quantity * price

        # 🔍 DEBUG IMPORTANT
        print(f"🔍 DEBUG {symbol} → qty={quantity} | value={value:.2f} USDT | min={min_notional}")

        if quantity < min_qty:
            raise Exception(f"❌ Quantity too small: {quantity}")

        if value < min_notional:
            raise Exception(f"❌ Too small trade: {value:.2f} < {min_notional}")

        # 🔥 EXECUTION
        print(f"📦 ORDER → {side} {quantity} {symbol} | price ~ {price}")

        order = client.create_order(
            symbol=symbol,
            side=side,
            type=ORDER_TYPE_MARKET,
            quantity=quantity
        )

        print("✅ ORDER EXECUTED")
        return order

    except Exception as e:
        print(f"🚨 BINANCE ERROR: {e}")
        return None