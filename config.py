import os
from dotenv import load_dotenv

load_dotenv()

# 🔑 API
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")


SYMBOLS = ["BTCUSDT", "AVAXUSDT", "XRPUSDT", "SOLUSDT", "ETHUSDT", "BNBUSDT", "LINKUSDT", "INJUSDT", "DOGEUSDT"]  # ajoute ici d'autres symboles


# 🧪 ENVIRONNEMENT
USE_TESTNET = True
AUTO_TRADING = True  # sécurité par défaut

# 💰 CAPITAL / RISK
RISK_PER_TRADE = 0.01       # 1% du capital par trade
MAX_DRAWDOWN = 0.2           # 20% perte globale

# 🛑 TRADES
STOP_LOSS_PCT = 0.01        # -1%
TAKE_PROFIT_PCT = 0.02       # +2%

# ⏱ BOT
LOOP_INTERVAL = 10            # secondes entre chaque analyse
MAX_TRADE_USDT = 20           # pour test uniquement

# SCALPING
SCALP_TP = 0.003  # 0.3%
SCALP_SL = 0.002  # 0.2%

# NOMBRE MAX DE TRADES SIMULTANES PAR CRYPTO
MAX_POSITIONS_PER_SYMBOL = 1


# Active le mode simulation pour tester le bot sans signal réel
SIMULATE_TRADES = False