import os
import joblib
import pandas as pd
from tensorflow.keras.models import load_model


def load_all():

    # =========================
    # VALIDASI FILE
    # =========================
    model_path = "model/best_lstm_multikecamatan.h5"
    encoder_path = "model/label_encoder_kecamatan.pkl"
    scaler_path = "model/scaler_rain.pkl"
    data_path = "data/data_fix.csv"

    for path in [model_path, encoder_path, scaler_path, data_path]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"File tidak ditemukan: {path}")

    # =========================
    # LOAD RESOURCE
    # =========================
    model = load_model(model_path, compile=False)
    encoder = joblib.load(encoder_path)
    scaler = joblib.load(scaler_path)
    data = pd.read_csv(data_path)

    # =========================
    # FIX KOLOM TANGGAL
    # =========================
    if "tanggal" in data.columns:
        pass
    elif "index" in data.columns:
        data.rename(columns={"index": "tanggal"}, inplace=True)
    else:
        data.reset_index(inplace=True)
        data.rename(columns={"index": "tanggal"}, inplace=True)

    data["tanggal"] = pd.to_datetime(data["tanggal"], errors="coerce")
    data = data.dropna(subset=["tanggal"])

    # =========================
    # FIX KOLOM HUJAN
    # =========================
    if "curah_hujan_mm" in data.columns:
        data.rename(columns={"curah_hujan_mm": "rain_mm"}, inplace=True)
    elif "chirps_power_corrected" in data.columns:
        data.rename(columns={"chirps_power_corrected": "rain_mm"}, inplace=True)

    # =========================
    # VALIDASI KOLOM WAJIB
    # =========================
    required_cols = ["tanggal", "rain_mm", "kecamatan"]
    for col in required_cols:
        if col not in data.columns:
            raise ValueError(f"Kolom wajib '{col}' tidak ditemukan")

    # =========================
    # CLEANING DATA
    # =========================
    data = data.sort_values("tanggal")

    data["rain_mm"] = pd.to_numeric(data["rain_mm"], errors="coerce")
    data["rain_mm"] = data["rain_mm"].fillna(method="ffill")

    # Drop jika masih ada NaN
    data = data.dropna(subset=["rain_mm"])

    return model, encoder, scaler, data
