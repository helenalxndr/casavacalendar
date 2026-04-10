import os
import joblib
import pandas as pd
from tensorflow.keras.models import load_model


def load_all():
    # =========================
    # 1. PATH FILE
    # =========================
    model_path = "model/best_lstm_multikecamatan.h5"
    encoder_path = "model/label_encoder_kecamatan.pkl"
    scaler_path = "model/scaler_rain.pkl"
    data_path = "data/data_fix.csv"

    # =========================
    # 2. VALIDASI FILE
    # =========================
    for path in [model_path, encoder_path, scaler_path, data_path]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"File tidak ditemukan: {path}")

    # =========================
    # 3. LOAD RESOURCE
    # =========================
    model = load_model(model_path, compile=False)
    encoder = joblib.load(encoder_path)
    scaler = joblib.load(scaler_path)
    data = pd.read_csv(data_path)

    # =========================
    # 4. FIX KOLOM TANGGAL
    # =========================
    if "tanggal" in data.columns:
        pass
    elif "index" in data.columns:
        data.rename(columns={"index": "tanggal"}, inplace=True)
    else:
        # fallback jika tanggal jadi index
        data.reset_index(inplace=True)
        data.rename(columns={"index": "tanggal"}, inplace=True)

    # Convert ke datetime
    data["tanggal"] = pd.to_datetime(data["tanggal"], errors="coerce")

    # Drop tanggal invalid
    data = data.dropna(subset=["tanggal"])

    # =========================
    # 5. FIX KOLOM HUJAN
    # =========================
    if "curah_hujan_mm" in data.columns:
        data.rename(columns={"curah_hujan_mm": "rain_mm"}, inplace=True)
    elif "chirps_power_corrected" in data.columns:
        data.rename(columns={"chirps_power_corrected": "rain_mm"}, inplace=True)

    # =========================
    # 6. VALIDASI KOLOM WAJIB
    # =========================
    required_cols = ["tanggal", "rain_mm", "kecamatan"]

    for col in required_cols:
        if col not in data.columns:
            raise ValueError(f"Kolom wajib '{col}' tidak ditemukan dalam dataset")

    # =========================
    # 7. CLEANING DATA
    # =========================
    # Urutkan berdasarkan waktu (WAJIB untuk time-series)
    data = data.sort_values("tanggal")

    # Pastikan rain numeric
    data["rain_mm"] = pd.to_numeric(data["rain_mm"], errors="coerce")

    # Isi missing value (pandas terbaru)
    data["rain_mm"] = data["rain_mm"].ffill().bfill()

    # Drop jika masih ada NaN
    data = data.dropna(subset=["rain_mm"])

    # Reset index biar rapi
    data = data.reset_index(drop=True)

    # =========================
    # 8. VALIDASI AKHIR
    # =========================
    if len(data) == 0:
        raise ValueError("Dataset kosong setelah preprocessing")

    if data["rain_mm"].isna().any():
        raise ValueError("Masih terdapat nilai NaN pada rain_mm")

    # =========================
    # RETURN
    # =========================
    return model, encoder, scaler, data
