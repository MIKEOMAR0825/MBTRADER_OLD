# bot/ai_model.py

import pandas as pd
import ta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# -----------------------------
# Ajouter les indicateurs techniques
# -----------------------------
def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ajoute RSI, MACD et EMA à un DataFrame contenant 'close'
    """
    if 'close' not in df.columns:
        raise ValueError("DataFrame doit contenir une colonne 'close'")

    df = df.copy()
    df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
    
    macd = ta.trend.MACD(df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    
    df['ema'] = ta.trend.EMAIndicator(df['close'], window=20).ema_indicator()
    
    return df

# -----------------------------
# Créer les labels pour l'IA
# -----------------------------
def create_labels(df: pd.DataFrame, n_future: int = 5) -> pd.DataFrame:
    """
    Crée la colonne 'target' : 1=BUY, -1=SELL, 0=HOLD
    """
    df = df.copy()
    df['future_price'] = df['close'].shift(-n_future)

    def signal(row):
        if row['future_price'] > row['close']:
            return 1
        elif row['future_price'] < row['close']:
            return -1
        else:
            return 0

    df['target'] = df.apply(signal, axis=1)
    return df

# -----------------------------
# Entraîner le modèle
# -----------------------------
def train_model(df: pd.DataFrame) -> RandomForestClassifier:
    df = df.dropna()
    features = ['rsi', 'macd', 'macd_signal', 'ema']
    
    X = df[features]
    y = df['target']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )
    
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=5,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    acc = model.score(X_test, y_test)
    print(f"✅ Modèle entraîné | Accuracy: {acc:.2f}")
    
    return model

# -----------------------------
# Prédiction
# -----------------------------
def predict_signal(model: RandomForestClassifier, df: pd.DataFrame) -> str:
    """
    Retourne le signal 'BUY', 'SELL', ou 'HOLD'
    """
    latest = df.iloc[-1]
    X = pd.DataFrame([{
    'rsi': latest['rsi'],
    'macd': latest['macd'],
    'macd_signal': latest['macd_signal'],
    'ema': latest['ema']
}])
    
    pred = model.predict(X)[0]
    prob = model.predict_proba(X).max()  # confiance max
    
    if pred == 1:
        return "BUY" if prob > 0.6 else "HOLD"
    elif pred == -1:
        return "SELL" if prob > 0.6 else "HOLD"
    return "HOLD"