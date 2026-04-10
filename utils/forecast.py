import numpy as np

def recursive_forecast(model, scaler, rain_last270, kec_id, days=30):

    # ==============================
    # VALIDASI INPUT
    # ==============================
    rain_last270 = np.array(rain_last270)

    if len(rain_last270) != 270:
        raise ValueError("Input rain_last270 harus tepat 270 hari.")

    if np.isnan(rain_last270).any():
        raise ValueError("Data hujan mengandung NaN.")

    # ==============================
    # SCALE INPUT
    # ==============================
    rain_scaled = scaler.transform(
        rain_last270.reshape(-1, 1)
    )

    if rain_scaled.shape != (270, 1):
        raise ValueError("Shape setelah scaling tidak sesuai.")

    forecast_scaled = []
    current_window = rain_scaled.copy()

    # ==============================
    # RECURSIVE FORECAST
    # ==============================
    for _ in range(days):

        X_rain = current_window.reshape(1, 270, 1)
        X_kec = np.array([[kec_id]])

        pred_scaled = model.predict(
            [X_rain, X_kec],
            verbose=0
        )[0][0]

        # Hindari nilai negatif (hujan tidak mungkin minus)
        pred_scaled = max(0, pred_scaled)

        forecast_scaled.append(pred_scaled)

        # Update window (lebih efisien)
        current_window = np.roll(current_window, -1)
        current_window[-1] = pred_scaled

    # ==============================
    # INVERSE SCALE
    # ==============================
    forecast_mm = scaler.inverse_transform(
        np.array(forecast_scaled).reshape(-1, 1)
    ).flatten()

    # Final safety (no negative rainfall)
    forecast_mm = np.clip(forecast_mm, 0, None)

    return forecast_mm
