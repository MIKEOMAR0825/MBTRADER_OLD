# bot/ai/model_loader.py


import joblib

models = {}

def load_models(symbols):
    for symbol in symbols:
        try:
            models[symbol] = joblib.load(f"models/{symbol}.pkl")
            print(f"✅ Modèle chargé pour {symbol}")
        except:
            print(f"⚠️ Pas de modèle pour {symbol}")