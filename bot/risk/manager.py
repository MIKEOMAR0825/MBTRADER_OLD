def update_risk(position, price):
    """
    Gestion avancée du risk management:
    - Break-even intelligent
    - Trailing stop conditionnel
    """

    entry = position["entry"]

    # -----------------------------
    # BREAK-EVEN (plus safe)
    # -----------------------------
    if price >= entry * 1.02:  # 🔥 2% au lieu de 1%
        position["stop_loss"] = max(position["stop_loss"], entry)

    # -----------------------------
    # TRAILING STOP INTELLIGENT
    # -----------------------------
    if price > entry * 1.01:  # activation seulement après 1%

        new_sl = price * 0.985  # trailing plus large (évite shakeout)

        # ne jamais baisser le SL
        position["stop_loss"] = max(position["stop_loss"], new_sl)