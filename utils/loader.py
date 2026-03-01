import joblib
import pandas as pd
from tensorflow.keras.models import load_model

def load_all():
    model = load_model("model/best_lstm_multikecamatan.h5", compile=False)
    encoder = joblib.load("model/label_encoder_kecamatan.pkl")
    scaler = joblib.load("model/scaler_rain.pkl")

    data = pd.read_csv("data/data_fix.csv")

    # =========================
    # FIX KOLOM TANGGAL
    # =========================
    if "tanggal" in data.columns:
        pass

    elif "index" in data.columns:
        data.rename(columns={"index": "tanggal"}, inplace=True)

    else:
        # fallback kalau tanggal jadi index dataframe
        data.reset_index(inplace=True)
        data.rename(columns={"index": "tanggal"}, inplace=True)

    data["tanggal"] = pd.to_datetime(data["tanggal"], errors="coerce")

    # =========================
    # FIX KOLOM RAIN
    # =========================
    if "curah_hujan_mm" in data.columns:
        data.rename(columns={"curah_hujan_mm": "rain_mm"}, inplace=True)

    elif "chirps_power_corrected" in data.columns:
        data.rename(columns={"chirps_power_corrected": "rain_mm"}, inplace=True)

    return model, encoder, scaler, data
