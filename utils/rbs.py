def kategori_hujan(hujan_mm):
    """
    Klasifikasi curah hujan:
    Rendah   : < 5 mm
    Normal   : 5–15 mm
    Tinggi   : > 15 mm
    """
    if hujan_mm < 5:
        return "Rendah"
    elif 5 <= hujan_mm <= 15:
        return "Normal"
    else:
        return "Tinggi"


def rbs_singkong_final(hujan_mm, hst):
    """
    Rule-Based System Kalender Tanam Singkong
    berbasis HST dan kategori curah hujan.
    """

    # Tanaman belum ditanam
    if hst < 0:
        return "Belum Tanam"

    kategori = kategori_hujan(hujan_mm)

    # =========================================
    # FASE 1: 0–30 HST (Perkecambahan & Awal)
    # =========================================
    if 0 <= hst <= 30:

        if kategori == "Rendah":
            return "Penyiraman Intensif — Tanah harus lembap agar tunas muncul."

        if kategori == "Tinggi":
            return "Perbaikan Drainase — Hindari genangan, cegah busuk bibit."

        return "Pemantauan Awal — Kelembapan cukup untuk pertumbuhan awal."


    # =========================================
    # FASE 2: 31–90 HST (Vegetatif)
    # =========================================
    if 31 <= hst <= 90:

        if kategori == "Normal" and hst <= 60:
            return "Pemupukan NPK Tahap 1 — Nutrisi diserap optimal saat air cukup."

        if kategori == "Rendah":
            return "Mulsa / Pengairan — Cegah tanaman kerdil akibat kekeringan."

        if kategori == "Tinggi":
            return "Penyiangan Gulma — Hujan tinggi memicu pertumbuhan gulma."

        return "Pemantauan Vegetatif — Pertumbuhan berlangsung normal."


    # =========================================
    # FASE 3: 91–180 HST (Pembentukan Umbi)
    # =========================================
    if 91 <= hst <= 180:

        if kategori == "Normal" and hst <= 150:
            return "Pemupukan Tahap 2 (Tinggi K) — Fokus pembesaran umbi."

        if kategori == "Rendah":
            return "Kritikal! Harus Diairi — Kekeringan menurunkan hasil umbi drastis."

        if kategori == "Tinggi":
            return "Pemantauan Drainase — Hindari kelebihan air di fase umbi."

        return "Pemantauan Umbi — Kondisi relatif stabil."


    # =========================================
    # FASE 4: > 180 HST (Pematangan & Panen)
    # =========================================
    if hst > 180:

        if hst > 240 and kategori == "Rendah":
            return "Waktu Panen Ideal — Kadar pati maksimal & tanah mudah digali."

        if kategori == "Tinggi":
            return "Tunda Panen — Kadar pati turun akibat pertumbuhan vegetatif ulang."

        return "Siap Panen — Evaluasi ukuran dan kualitas umbi."


    return "Pemantauan Rutin — Lanjutkan observasi lapangan."
