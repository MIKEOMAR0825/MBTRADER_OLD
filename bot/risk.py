class GlobalRisk:
    """
    Gestion du risque global + protection capital
    """

    def __init__(self, initial_balance: float, max_drawdown_pct: float):
        self.initial_balance = initial_balance
        self.max_drawdown_pct = max_drawdown_pct

        self.peak_balance = initial_balance
        self.active = True
        self.last_drawdown = 0.0

    # -----------------------------
    # CHECK GLOBAL RISK
    # -----------------------------
    def check(self, balance: float) -> bool:
        """
        Active / désactive le bot selon drawdown
        """

        # update peak
        if balance > self.peak_balance:
            self.peak_balance = balance

        # drawdown calcul
        drawdown = (self.peak_balance - balance) / self.peak_balance
        self.last_drawdown = drawdown

        # kill switch
        if drawdown >= self.max_drawdown_pct:
            self.active = False
            print(f"⛔ KILL SWITCH ACTIVÉ | Drawdown: {drawdown*100:.2f}%")

        return self.active

    # -----------------------------
    # STOP LOSS
    # -----------------------------
    @staticmethod
    def stop_loss_hit(entry_price: float, current_price: float, stop_loss_pct: float) -> bool:
        return current_price <= entry_price * (1 - stop_loss_pct)

    # -----------------------------
    # TAKE PROFIT
    # -----------------------------
    @staticmethod
    def take_profit_hit(entry_price: float, current_price: float, take_profit_pct: float) -> bool:
        return current_price >= entry_price * (1 + take_profit_pct)

    # -----------------------------
    # DEBUG RISK
    # -----------------------------
    def status(self):
        return {
            "active": self.active,
            "peak_balance": self.peak_balance,
            "drawdown_pct": round(self.last_drawdown * 100, 2)
        }