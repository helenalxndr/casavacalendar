import numpy as np

def recursive_forecast(model, scaler, rain_last270, kec_id, days=30):

    rain_scaled = scaler.transform(
        rain_last270.reshape(-1,1)
    )

    forecast_scaled = []
    current_window = rain_scaled.copy()

    for _ in range(days):

        X_rain = current_window.reshape(1,270,1)
        X_kec  = np.array([[kec_id]])

        pred_scaled = model.predict(
            [X_rain, X_kec],
            verbose=0
        )[0][0]

        forecast_scaled.append(pred_scaled)

        current_window = np.append(
            current_window[1:], pred_scaled
        )

    forecast_mm = scaler.inverse_transform(
        np.array(forecast_scaled).reshape(-1,1)
    ).flatten()

    return forecast_mm
