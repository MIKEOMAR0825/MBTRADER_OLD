import joblib
import os

models = {}

MODEL_DIR = "models"


def load_models(symbols):
    """
    Charge les modèles ML de manière sécurisée
    """

    for symbol in symbols:

        model_path = os.path.join(MODEL_DIR, f"{symbol}.pkl")

        try:
            if not os.path.exists(model_path):
                print(f"⚠️ Model file missing: {symbol}")
                continue

            model = joblib.load(model_path)

            # 🔥 validation simple
            if model is None:
                print(f"❌ Invalid model: {symbol}")
                continue

            models[symbol] = model

            print(f"✅ Model loaded: {symbol}")

        except Exception as e:
            print(f"❌ Error loading {symbol}: {e}")