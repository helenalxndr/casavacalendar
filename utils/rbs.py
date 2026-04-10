import numpy as np


# =========================
# 1. KATEGORI HUJAN (SAFE)
# =========================
def kategori_hujan(hujan_mm):
    try:
        if hujan_mm is None or np.isnan(float(hujan_mm)):
            return "Tidak Diketahui"
    except:
        return "Tidak Diketahui"

    hujan_mm = float(hujan_mm)

    if hujan_mm < 5:
        return "Rendah"
    elif hujan_mm <= 15:
        return "Sedang"
    else:
        return "Tinggi"


# =========================
# 2. RULE BASED SYSTEM SINGKONG
# =========================
def rbs_singkong_final(hujan_mm, hst):

    kategori = kategori_hujan(hujan_mm)
    hst = int(hst)

    # =========================
    # PRA-TANAM
    # =========================
    if hst < 0:
        if kategori == "Sedang":
            return "Waktu Tanam Ideal — Kelembapan tanah optimal untuk penanaman."
        elif kategori == "Rendah":
            return "Tunda Tanam — Tanah terlalu kering."
        elif kategori == "Tinggi":
            return "Tunda Tanam — Risiko genangan tinggi."
        else:
            return "Evaluasi Kondisi Tanam."

    # =========================
    # FASE AWAL (0–30 HST)
    # =========================
    if 0 <= hst <= 30:
        if kategori == "Rendah":
            return "Penyiraman Intensif — Tanah perlu kelembapan tambahan."
        elif kategori == "Tinggi":
            return "Perbaikan Drainase — Cegah genangan air."
        else:
            return "Pemantauan Awal — Kondisi pertumbuhan normal."

    # =========================
    # FASE VEGETATIF (31–90 HST)
    # =========================
    if 31 <= hst <= 90:
        if kategori == "Sedang" and hst <= 60:
            return "Pemupukan NPK Tahap 1 — Mendukung pertumbuhan vegetatif."
        elif kategori == "Rendah":
            return "Mulsa / Pengairan — Cegah kekeringan."
        elif kategori == "Tinggi":
            return "Penyiangan Gulma — Hujan tinggi memicu gulma."
        else:
            return "Pemantauan Vegetatif — Pertumbuhan stabil."

    # =========================
    # FASE PEMBENTUKAN UMBI (91–180 HST)
    # =========================
    if 91 <= hst <= 180:
        if kategori == "Sedang" and hst <= 150:
            return "Pemupukan Tahap 2 (Tinggi K) — Fokus pembesaran umbi."
        elif kategori == "Rendah":
            return "Kritikal — Perlu pengairan tambahan."
        elif kategori == "Tinggi":
            return "Pemantauan Drainase — Hindari kelebihan air."
        else:
            return "Pemantauan Umbi — Kondisi stabil."

    # =========================
    # FASE PANEN (>180 HST)
    # =========================
    if hst > 180:
        if hst > 240 and kategori == "Rendah":
            return "Waktu Panen Ideal — Kadar pati maksimal."
        elif kategori == "Tinggi":
            return "Tunda Panen — Risiko kualitas turun."
        else:
            return "Siap Panen — Evaluasi kondisi umbi."

    return "Pemantauan Rutin."


# =========================
# 3. LABEL SINGKAT (FIXED)
# =========================
def label_singkat(aktivitas):

    if not aktivitas:
        return "Pemantauan"

    a = aktivitas.lower()

    if "tanam" in a:
        return "Penanaman"

    if "pupuk" in a:
        return "Pemupukan"

    if "siram" in a:
        return "Penyiraman"

    if "drainase" in a:
        return "Penyiraman"

    if "gulma" in a:
        return "Pembersihan Gulma"

    if "panen" in a:
        return "Pemanenan"

    if "mulsa" in a:
        return "Pemeliharaan"

    if "pemantauan" in a:
        return "Pemantauan"

    return "Pemantauan"
