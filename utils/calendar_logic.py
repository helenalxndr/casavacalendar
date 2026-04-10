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

def get_color(label):

    if not label:
        return "#9ca3af"

    label = label.lower()

    # TANAM
    if "tanam" in label:
        return "#22c55e"

    # PEMUPUKAN (INI FIX UTAMA)
    if "pupuk" in label or "nutrisi" in label:
        return "#facc15"

    # PENYIRAMAN / AIR
    if "sir" in label or "air" in label or "kelembapan" in label:
        return "#3b82f6"

    # GULMA
    if "gulma" in label or "penyiang" in label:
        return "#a855f7"

    # PANEN
    if "panen" in label:
        return "#ef4444"

    # DRAINASE
    if "drainase" in label or "genangan" in label:
        return "#06b6d4"

    return "#9ca3af"
