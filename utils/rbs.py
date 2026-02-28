def kategori_hujan(hujan_mm):
    """
    Klasifikasi curah hujan menjadi:
    Rendah, Normal, Tinggi
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
    berdasarkan HST dan kategori curah hujan.
    """

    kategori = kategori_hujan(hujan_mm)

    if 0 <= hst <= 15 and kategori == "Rendah":
        return "Penyiraman Intensif — Tanah harus lembap agar tunas muncul."

    if 0 <= hst <= 30 and kategori == "Tinggi":
        return "Perbaikan Drainase — Hindari genangan, cegah busuk bibit."

    if 31 <= hst <= 60 and kategori == "Normal":
        return "Pemupukan NPK Tahap 1 — Nutrisi diserap optimal saat air cukup."

    if 31 <= hst <= 90 and kategori == "Rendah":
        return "Mulsa / Pengairan — Cegah tanaman kerdil akibat kekeringan."

    if 61 <= hst <= 90 and kategori == "Tinggi":
        return "Penyiangan Gulma — Hujan tinggi memicu pertumbuhan gulma."

    if 91 <= hst <= 150 and kategori == "Normal":
        return "Pemupukan Tahap 2 (Tinggi K) — Fokus pembesaran umbi."

    if 91 <= hst <= 180 and kategori == "Rendah":
        return "Kritikal! Harus Diairi — Kekeringan menurunkan hasil umbi drastis."

    if hst > 181 and kategori == "Tinggi":
        return "Tunda Panen — Kadar pati turun karena pertumbuhan vegetatif ulang."

    if hst > 240 and kategori == "Rendah":
        return "Waktu Panen Ideal — Kadar pati maksimal & tanah mudah digali."

    return "Pemantauan Rutin — Kondisi relatif aman, lanjutkan observasi lapangan."
