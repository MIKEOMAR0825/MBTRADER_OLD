# train_model.py
import pandas as pd
import os
from bot.ai_model import add_indicators, create_labels, train_model
import joblib

# 🔹 Dossier avec CSV historiques
DATA_DIR = "historical_data"
MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

# 🔹 Boucle sur tous les CSV
for file in os.listdir(DATA_DIR):
    if file.endswith(".csv"):
        symbol = file.replace(".csv", "")
        print(f"📊 Entraînement du modèle pour {symbol} ...")
        
        df = pd.read_csv(os.path.join(DATA_DIR, file))
        df = add_indicators(df)
        df = create_labels(df)
        
        model = train_model(df)
        
        model_path = os.path.join(MODEL_DIR, f"model_{symbol}.pkl")
        joblib.dump(model, model_path)
        print(f"✅ {model_path} créé")