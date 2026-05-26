# Risk.py

class GlobalRisk:
    """
    Gestion du risque global et stop-loss individuel
    """
    def __init__(self, initial_balance: float, max_drawdown_pct: float):
        self.initial_balance = initial_balance
        self.max_drawdown_pct = max_drawdown_pct
        self.peak_balance = initial_balance
        self.active = True

    # -----------------------------
    # Vérification du risque global
    # -----------------------------
    def check(self, balance: float) -> bool:
        """
        Vérifie si le drawdown max est atteint
        """
        # Mise à jour du pic
        if balance > self.peak_balance:
            self.peak_balance = balance

        drawdown = (self.peak_balance - balance) / self.peak_balance

        if drawdown >= self.max_drawdown_pct:
            self.active = False
            print(f"⛔ MAX DRAWDOWN ATTEINT: {round(drawdown*100,2)}%")

        return self.active

    # -----------------------------
    # Stop-loss pour un trade individuel
    # -----------------------------
    @staticmethod
    def stop_loss_hit(entry_price: float, current_price: float, stop_loss_pct: float = 0.02) -> bool:
        """
        Retourne True si le stop-loss est touché
        """
        return current_price <= entry_price * (1 - stop_loss_pct)

    # -----------------------------
    # Take-profit pour un trade individuel
    # -----------------------------
    @staticmethod
    def take_profit_hit(entry_price: float, current_price: float, take_profit_pct: float = 0.04) -> bool:
        """
        Retourne True si le take-profit est touché
        """
        return current_price >= entry_price * (1 + take_profit_pct)