import numpy as np


# =========================
# KATEGORI HUJAN SAFE
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
# RBS FINAL (FASE + LABEL + KODE WARNA)
# =========================
def rbs_singkong_final(hujan_mm, hst):

    kategori = kategori_hujan(hujan_mm)
    hst = int(hst)

    # ================= PRA TANAM =================
    if hst < 0:
        if kategori == "Sedang":
            return ("🌱 Masa Tanam Ideal",
                    "Kondisi tanah sudah cukup baik. Anda bisa mulai menanam untuk hasil optimal.",
                    "tanam")

        elif kategori == "Rendah":
            return ("⏳ Sebaiknya Menunda Tanam",
                    "Tanah masih terlalu kering, sebaiknya menunggu kondisi lebih baik.",
                    "tunda")

        elif kategori == "Tinggi":
            return ("⏳ Sebaiknya Menunda Tanam",
                    "Risiko genangan cukup tinggi, tunggu kondisi stabil.",
                    "tunda")

        return ("ℹ️ Menunggu Kondisi Terbaik",
                "Kondisi lahan masih perlu pemantauan lebih lanjut.",
                "monitor")

    # ================= AWAL =================
    if 0 <= hst <= 30:
        if kategori == "Rendah":
            return ("💧 Pendampingan Penyiraman",
                    "Tanaman membutuhkan tambahan air agar akar berkembang optimal.",
                    "air")

        elif kategori == "Tinggi":
            return ("🌧️ Perhatian Drainase",
                    "Pastikan tidak terjadi genangan air di lahan.",
                    "air")

        return ("🌱 Masa Pertumbuhan Awal",
                "Tanaman sedang beradaptasi dengan lingkungan.",
                "monitor")

    # ================= VEGETATIF =================
    if 31 <= hst <= 90:
        if kategori == "Sedang" and hst <= 40:
            return ("🌿 Waktu Pemupukan Awal",
                    "Nutrisi tambahan membantu pertumbuhan tanaman lebih kuat.",
                    "pupuk")

        elif kategori == "Rendah":
            return ("💧 Dukungan Air & Mulsa",
                    "Tanaman perlu kelembapan agar tidak stres kekeringan.",
                    "air")

        elif kategori == "Tinggi":
            return ("🌿 Pengendalian Gulma",
                    "Pertumbuhan gulma meningkat saat hujan tinggi.",
                    "gulma")

        return ("🌱 Pertumbuhan Vegetatif Stabil",
                "Tanaman tumbuh dengan baik tanpa tindakan khusus.",
                "monitor")

    # ================= UMBI =================
    if 91 <= hst <= 180:
        if kategori == "Sedang" and hst <= 150:
            return ("🌿 Pemupukan Lanjutan",
                    "Nutrisi tambahan membantu pembentukan umbi optimal.",
                    "pupuk")

        elif kategori == "Rendah":
            return ("💧 Perhatian Kelembapan",
                    "Kekeringan dapat menghambat pembentukan umbi.",
                    "air")

        elif kategori == "Tinggi":
            return ("🌧️ Pengawasan Drainase",
                    "Kelebihan air perlu dihindari pada fase umbi.",
                    "air")

        return ("🌾 Masa Pembentukan Umbi",
                "Tanaman sedang fokus membentuk umbi.",
                "monitor")

    # ================= PANEN =================
    if hst > 180:
        if hst > 240 and kategori == "Rendah":
            return ("🌾 Waktu Panen Terbaik",
                    "Umbi matang optimal, siap dipanen.",
                    "panen")

        elif kategori == "Tinggi":
            return ("⏳ Pertimbangkan Menunda Panen",
                    "Kondisi lembap dapat menurunkan kualitas hasil.",
                    "tunda")

        return ("🌾 Siap Panen",
                "Tanaman sudah siap dipanen.",
                "panen")

    return ("ℹ️ Pemantauan Rutin",
            "Kondisi tanaman stabil, lakukan pengamatan berkala.",
            "monitor")


# =========================
# LABEL SINGKAT (UNTUK UI)
# =========================
def label_singkat(result):
    if isinstance(result, tuple):
        return result[0]   # FASE (dipakai UI)
    return "ℹ️ Pemantauan"
