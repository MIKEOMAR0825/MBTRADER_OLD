# bot/simulator.py

from datetime import datetime

class Simulator:
    """
    Simulateur de trading pour backtesting et test IA
    """
    def __init__(self, balance: float, risk_per_trade: float = 0.02, stop_loss_pct: float = 0.02, take_profit_pct: float = 0.04):
        self.balance = balance
        self.risk_per_trade = risk_per_trade
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.position = None
        self.logger = []

    # -----------------------------
    # Ouvrir une position BUY
    # -----------------------------
    def buy(self, price: float):
        if self.position is None:
            qty = self.balance * self.risk_per_trade / price
            self.position = {
                "entry": price,
                "quantity": qty,
                "stop_loss": price * (1 - self.stop_loss_pct),
                "take_profit": price * (1 + self.take_profit_pct),
                "time_open": datetime.now()
            }
            self.logger.append({
                "action": "BUY",
                "price": price,
                "balance": self.balance,
                "time_open": self.position["time_open"]
            })

    # -----------------------------
    # Vérifier sortie automatique
    # -----------------------------
    def check_exit(self, price: float):
        if self.position:
            if price <= self.position["stop_loss"]:
                self.sell(price, reason="STOP-LOSS")
            elif price >= self.position["take_profit"]:
                self.sell(price, reason="TAKE-PROFIT")

    # -----------------------------
    # Fermer une position
    # -----------------------------
    def sell(self, price: float, reason: str = "SELL"):
        if self.position:
            profit = (price - self.position["entry"]) * self.position["quantity"]
            self.balance += profit
            self.logger.append({
                "action": reason,
                "price": price,
                "profit": profit,
                "balance": self.balance,
                "time_open": self.position["time_open"],
                "time_close": datetime.now()
            })
            self.position = None

    # -----------------------------
    # Historique
    # -----------------------------
    def get_history(self):
        return self.logger