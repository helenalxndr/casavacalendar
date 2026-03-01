import joblib
import pandas as pd
from tensorflow.keras.models import load_model

def load_all():
    model = load_model("model/best_lstm_multikecamatan.h5", compile=False)
    encoder = joblib.load("model/label_encoder_kecamatan.pkl")
    scaler = joblib.load("model/scaler_rain.pkl")
    
    data = pd.read_csv("data/data_fix.csv")

    if "index" in data.columns:
        data.rename(columns={"index": "tanggal"}, inplace=True)
    elif "date" in data.columns:
        data.rename(columns={"date": "tanggal"}, inplace=True)

    data["tanggal"] = pd.to_datetime(data["tanggal"])

    return model, encoder, scaler, data
