import pandas as pd
from bot.indicators import calculate_rsi_series, calculate_macd, calculate_ema
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# -----------------------------
# Préparer les données
# -----------------------------
def prepare_data(df: pd.DataFrame, n_future: int = 5) -> pd.DataFrame:
    """
    Ajoute RSI, EMA, MACD et crée la colonne target pour prédiction
    """
    df = df.copy()
    df['rsi'] = calculate_rsi_series(df['close'])
    df['ema'] = calculate_ema(df['close'])
    
    macd, signal = calculate_macd(df['close'])
    df['macd'] = macd
    df['macd_signal'] = signal

    # Target sur n_future bougies
    df['future'] = df['close'].shift(-n_future)

    def label(row):
        if row['future'] > row['close']:
            return 1   # BUY
        elif row['future'] < row['close']:
            return -1  # SELL
        return 0       # HOLD

    df['target'] = df.apply(label, axis=1)
    return df.dropna()

# -----------------------------
# Entraîner le modèle
# -----------------------------
def train_model(df: pd.DataFrame) -> RandomForestClassifier:
    """
    Entraîne un RandomForestClassifier sur les features RSI, EMA, MACD
    """
    features = ['rsi', 'macd', 'macd_signal', 'ema']
    X = df[features]
    y = df['target']

    # Split train/test pour évaluer la performance
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=5,
        random_state=42
    )
    model.fit(X_train, y_train)

    acc = model.score(X_test, y_test)
    print(f"✅ RandomForest entraîné | Accuracy: {acc:.2f}")

    return model