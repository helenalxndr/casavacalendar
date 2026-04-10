from datetime import date

def get_forecast_index(curr_dt, start_pred_date, forecast_len):
    idx = (curr_dt - start_pred_date).days
    return max(0, min(idx, forecast_len - 1))


def get_hst(curr_dt, tgl_tanam):
    return max(0, (curr_dt - tgl_tanam).days)


def get_color(label):

    if not label:
        return "#9ca3af"

    label = label.lower()

    # 🌱 TANAM / PENANAMAN
    if "tanam" in label:
        return "#22c55e"

    # 💧 PENYIRAMAN / AIR / KEKERINGAN
    if "siram" in label or "air" in label or "kelembapan" in label:
        return "#3b82f6"

    # 🌿 PEMUPUKAN
    if "pupuk" in label or "nutrisi" in label:
        return "#f59e0b"

    # 🌿 PENYIANGAN / GULMA
    if "gulma" in label or "penyiangan" in label:
        return "#8b5cf6"

    # 🌾 PANEN
    if "panen" in label:
        return "#ef4444"

    # 🌧️ DRAINASE / GENANGAN
    if "drainase" in label or "genangan" in label:
        return "#06b6d4"

    # 🌱 DEFAULT / PEMANTAUAN
    return "#9ca3af"
