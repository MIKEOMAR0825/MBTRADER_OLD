# bot/engine.py

import time
import threading
import config
from bot.trader import start_auto_trading
from bot.risk import GlobalRisk
from services.binance_client import get_account_balance
from bot.logger import get_total_pnl

engine_thread = None
engine_running = False
risk_manager = None  # sera initialisé au démarrage

# -----------------------------
# Boucle principale de trading
# -----------------------------
def trading_loop():
    global engine_running, risk_manager
    print("🔄 Boucle de trading démarrée")

    while engine_running:
        try:
            # 🔹 Solde disponible
            balance = get_account_balance()["available"]

            # 🔹 Initialiser risk manager
            if risk_manager is None:
                risk_manager = GlobalRisk(
                    initial_balance=balance,
                    max_drawdown_pct=config.MAX_DRAWDOWN
                )

            # 🔹 Vérifier risque global
            if not risk_manager.check(balance):
                print("⛔ STOP GLOBAL, boucle arrêtée")
                engine_running = False
                break

            # 🔹 Lancer trading multi-crypto
            start_auto_trading()

            # 🔹 Affichage PnL par crypto
            pnl_summary = get_total_pnl()
            pnl_text = " | ".join([f"{s}: {p:.2f}" for s, p in pnl_summary.items()])
            print(f"💰 Solde: {balance:.2f} | Risque actif: {risk_manager.active} | PnL: {pnl_text}")

            time.sleep(config.LOOP_INTERVAL)

        except Exception as e:
            print(f"⚠️ Erreur boucle trading: {e}")
            time.sleep(5)

# -----------------------------
# Démarrer le moteur
# -----------------------------
def start_engine():
    global engine_thread, engine_running, risk_manager

    if engine_running:
        print("⚠️ Boucle déjà active")
        return

    try:
        balance = get_account_balance()["available"]
    except:
        balance = 1000  # fallback

    risk_manager = GlobalRisk(
        initial_balance=balance,
        max_drawdown_pct=config.MAX_DRAWDOWN
    )

    engine_running = True
    engine_thread = threading.Thread(target=trading_loop, daemon=True)
    engine_thread.start()
    print("🟢 Moteur de trading démarré")

# -----------------------------
# Arrêter le moteur
# -----------------------------
def stop_engine():
    global engine_running
    engine_running = False
    if engine_thread:
        engine_thread.join(timeout=1)
    print("🛑 Moteur de trading arrêté")