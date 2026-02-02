import numpy as np
import pandas as pd
from utils.rbs import rbs_singkong_final

WINDOW = 30


def preprocess_input(df, scaler, features):
    """
    Preprocessing HARUS IDENTIK dengan training
    """
    df = df.copy()

    df["rain_log"] = np.log1p(df["curah_hujan_mm_corrected"])

    df["roll7"] = df["rain_log"].rolling(7).mean()
    df["roll30"] = df["rain_log"].rolling(30).mean()
    df["std7"] = df["rain_log"].rolling(7).std()
    df["delta"] = df["rain_log"].diff()

    df = df.fillna(0)

    df[features] = scaler.transform(df[features])

    return df


def forecast_lstm_global(
    model,
    df_kec,
    scaler,
    encoder,
    features,
    n_days=30
):
    """
    Recursive forecasting untuk model LSTM global
    """

    kecamatan = df_kec["kecamatan"].iloc[0]
    kec_id = encoder.transform([kecamatan])[0]

    df_proc = preprocess_input(df_kec, scaler, features)
    df_temp = df_proc.copy()

    preds = []
    dates = []

    last_date = df_kec["index"].max()

    for i in range(n_days):
        X_input = df_temp[features].values[-WINDOW:]
        X_input = X_input.reshape(1, WINDOW, len(features))

        pred_log = model.predict(
            [X_input, np.array([[kec_id]])],
            verbose=0
        )[0][0]

        pred_mm = max(np.expm1(pred_log), 0)

        preds.append(pred_mm)
        dates.append(last_date + pd.Timedelta(days=i + 1))

        # append baris prediksi (recursive)
        new_row = df_temp.iloc[-1].copy()
        new_row["rain_log"] = pred_log
        df_temp = pd.concat(
            [df_temp, new_row.to_frame().T],
            ignore_index=True
        )

    return pd.DataFrame({
        "Tanggal": dates,
        "Prediksi Hujan (mm)": preds
    })


def build_dashboard_df(
    df_all,
    model,
    scaler,
    encoder,
    features,
    kecamatan,
    tanggal_acuan,
    n_days=30
):
    """
    Menyusun dataframe final untuk dashboard kalender
    """

    # ===============================
    # FILTER DATA KECAMATAN
    # ===============================
    df_kec = (
        df_all[df_all["kecamatan"] == kecamatan]
        .sort_values("index")
    )

    df_kec = df_kec[df_kec["index"] <= tanggal_acuan]

    if len(df_kec) < WINDOW:
        return pd.DataFrame()

    # ===============================
    # FORECAST
    # ===============================
    pred_df = forecast_lstm_global(
        model=model,
        df_kec=df_kec,
        scaler=scaler,
        encoder=encoder,
        features=features,
        n_days=n_days
    )

    # ===============================
    # HST & AKTIVITAS
    # ===============================
    pred_df["HST"] = range(1, len(pred_df) + 1)

    pred_df["Aktivitas"] = pred_df.apply(
        lambda x: rbs_singkong_final(
            x["Prediksi Hujan (mm)"],
            x["HST"]
        ),
        axis=1
    )

    return pred_df
