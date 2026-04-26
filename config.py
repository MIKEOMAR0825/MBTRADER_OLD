import os
from dotenv import load_dotenv


load_dotenv()

# 🔑 API
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")


SYMBOLS = ["BTCUSDT", "AVAXUSDT", "XRPUSDT", "SOLUSDT"]  # ajoute ici d'autres symboles
#SYMBOLS = ["BTCUSDT", "XRPUSDT", "AVAXUSDT", "ETHUSDT"]  # ajoute ici d'autres symboles


# 🧪 ENVIRONNEMENT
USE_TESTNET = False
AUTO_TRADING = True  # sécurité par défaut


# 💰 CAPITAL / RISK
##RISK_PER_TRADE = 0.5         # 0.5% du capital par trade
RISK_PER_TRADE = 0.02       # 2% du capital par trade
MAX_DRAWDOWN = 0.2           # 20% perte globale


# 🛑 TRADES
STOP_LOSS_PCT = 0.02         # -1%
TAKE_PROFIT_PCT = 0.04       # +2%


# ⏱ BOT
LOOP_INTERVAL = 5            # secondes entre chaque analyse
MAX_TRADE_USDT = 10         # pour test uniquement
#MAX_TRADE_USDT = 5           # montant max par trade (en USDT)


# SCALPING
SCALP_TP = 0.003  # 0.3%
SCALP_SL = 0.002  # 0.2%


##SCALP_TP = 0.006  # 0.6%
##SCALP_SL = 0.004  # 0.4%


# NOMBRE MAX DE TRADES SIMULTANES PAR CRYPTO
MAX_POSITIONS_PER_SYMBOL = 1


# Active le mode simulation pour tester le bot sans signal réel
SIMULATE_TRADES = False