import numpy as np


def recursive_forecast(model, scaler, rain_last270, kec_id, days=30):

    # ==============================
    # VALIDASI INPUT
    # ==============================
    if len(rain_last270) != 270:
        raise ValueError("Input rain_last270 harus tepat 270 hari.")

    # ==============================
    # SCALE INPUT
    # ==============================
    rain_scaled = scaler.transform(
        np.array(rain_last270).reshape(-1, 1)
    )

    forecast_scaled = []

    # Pastikan shape tetap (270,1)
    current_window = rain_scaled.copy()

    for _ in range(days):

        # Shape model multi-input
        X_rain = current_window.reshape(1, 270, 1)
        X_kec = np.array([[kec_id]])

        pred_scaled = model.predict(
            [X_rain, X_kec],
            verbose=0
        )[0][0]

        forecast_scaled.append(pred_scaled)

        # ==============================
        # UPDATE WINDOW (SAFE)
        # ==============================
        current_window = np.vstack([
            current_window[1:],
            [[pred_scaled]]
        ])

    # ==============================
    # INVERSE SCALE
    # ==============================
    forecast_mm = scaler.inverse_transform(
        np.array(forecast_scaled).reshape(-1, 1)
    ).flatten()

    return forecast_mm
