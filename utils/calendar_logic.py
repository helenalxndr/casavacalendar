from datetime import date

def get_forecast_index(curr_dt, start_pred_date, forecast_len):
    idx = (curr_dt - start_pred_date).days
    return max(0, min(idx, forecast_len - 1))


def get_hst(curr_dt, tgl_tanam):
    return max(0, (curr_dt - tgl_tanam).days)


def get_color(label):
    color_map = {
        "Penanaman": "#22c55e",       # hijau
        "Penyiraman": "#3b82f6",      # biru
        "Pemupukan": "#f59e0b",       # kuning
        "Pembersihan Gulma": "#8b5cf6", # ungu
        "Pemanenan": "#ef4444",       # merah
        "Pemantauan": "#9ca3af"       # abu
    }
    return color_map.get(label, "#e5e7eb")
