from datetime import date

def get_forecast_index(curr_dt, start_pred_date, forecast_len):
    idx = (curr_dt - start_pred_date).days
    return max(0, min(idx, forecast_len - 1))


def get_hst(curr_dt, tgl_tanam):
    return max(0, (curr_dt - tgl_tanam).days)

def get_color(kode):
    color_map = {
        "tanam": "#22c55e",     # hijau
        "air": "#3b82f6",       # biru
        "pupuk": "#f59e0b",     # kuning
        "gulma": "#8b5cf6",     # ungu
        "panen": "#ef4444",     # merah
        "tunda": "#f97316",     # oranye
        "monitor": "#efe3ca"    # beige
    }
    return color_map.get(kode)
