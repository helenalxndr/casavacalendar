import pandas as pd
import streamlit as st
import joblib
from tensorflow.keras.models import load_model


@st.cache_resource
def load_all():
    """
    Load dataset, model LSTM global, scaler, encoder kecamatan,
    dan daftar fitur (WAJIB konsisten dengan training).
    """

    # ===============================
    # LOAD DATA
    # ===============================
    df = pd.read_csv("data/data.csv")
    df["index"] = pd.to_datetime(df["index"])
    df["kecamatan"] = df["kecamatan"].str.strip()
    df = df.sort_values(["kecamatan", "index"])

    # ===============================
    # LOAD MODEL GLOBAL
    # ===============================
    model = load_model(
        "data/models/global_lstm_kecamatan.h5",
        compile=False
    )

    # ===============================
    # LOAD ASSET PENDUKUNG
    # ===============================
    scaler = joblib.load(
        "data/scalers/global_scaler.pkl"
    )

    encoder = joblib.load(
        "data/encoders/kecamatan_encoder.pkl"
    )

    features = joblib.load(
        "data/features/feature_list.pkl"
    )

    return df, model, scaler, encoder, features
