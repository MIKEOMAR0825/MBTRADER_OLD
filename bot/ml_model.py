import pandas as pd
from bot.indicators import calculate_rsi_series, calculate_macd, calculate_ema
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# -----------------------------
# DATASET BUILD
# -----------------------------
def prepare_data(df: pd.DataFrame, n_future: int = 5, threshold: float = 0.002) -> pd.DataFrame:

    df = df.copy()

    df["rsi"] = calculate_rsi_series(df["close"])
    df["ema"] = calculate_ema(df["close"])

    macd, signal = calculate_macd(df["close"])
    df["macd"] = macd
    df["macd_signal"] = signal

    # -----------------------------
    # future return (important)
    # -----------------------------
    df["future"] = df["close"].shift(-n_future)

    df["return"] = (df["future"] - df["close"]) / df["close"]

    # -----------------------------
    # LABEL PRO (avec seuil)
    # -----------------------------
    def label(row):
        if row["return"] > threshold:
            return 1   # BUY
        elif row["return"] < -threshold:
            return -1  # SELL
        return 0       # HOLD

    df["target"] = df.apply(label, axis=1)

    # 🔥 important: enlever bruit extrême
    df = df.dropna()

    return df


# -----------------------------
# TRAIN MODEL
# -----------------------------
def train_model(df: pd.DataFrame):

    features = ["rsi", "macd", "macd_signal", "ema"]

    X = df[features]
    y = df["target"]

    # 🔥 split temporel correct
    split = int(len(df) * 0.8)

    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=6,
        random_state=42,
        class_weight="balanced"
    )

    model.fit(X_train, y_train)

    acc = model.score(X_test, y_test)

    print(f"✅ Model trained | Accuracy: {acc:.2f}")

    return model