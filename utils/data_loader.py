import joblib
import pandas as pd
from tensorflow.keras.models import load_model

def load_all():
    model = load_model("model/best_lstm_multikecamatan.h5")
    encoder = joblib.load("model/label_encoder_kecamatan.pkl")
    scaler = joblib.load("model/scaler_rain.pkl")
    data = pd.read_csv("data/data.csv")
    data["index"] = pd.to_datetime(data["index"])
    return model, encoder, scaler, data
