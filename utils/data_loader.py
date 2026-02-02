import pandas as pd
import joblib
from tensorflow.keras.models import load_model


def load_all():
    # 🔹 Load data
    df_all = pd.read_csv(
        "data.csv",
        parse_dates=["tanggal"]
    )

    df_all["kecamatan"] = df_all["kecamatan"].str.strip()
    df_all = df_all.sort_values(["kecamatan", "tanggal"])

    # 🔹 Load model & asset global
    model = load_model(
        "models/global_lstm_kecamatan.h5",
        compile=False
    )

    scaler = joblib.load("scalers/global_scaler.pkl")
    encoder = joblib.load("encoders/kecamatan_encoder.pkl")
    features = joblib.load("features/feature_list.pkl")

    return df_all, model, scaler, encoder, features
