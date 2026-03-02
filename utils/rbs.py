def kategori_hujan(hujan_mm):
    if hujan_mm < 5:
        return "Rendah"
    elif hujan_mm <= 15:
        return "Normal"
    return "Tinggi"


def rbs_singkong_final(hujan_mm, hst):

    kategori = kategori_hujan(hujan_mm)

    if hst < 0:

        if kategori == "Normal":
            return "Waktu Tanam Ideal — Kelembapan cukup untuk memulai penanaman."

        if kategori == "Rendah":
            return "Tunda Tanam — Tanah terlalu kering, risiko gagal tumbuh tinggi."

        if kategori == "Tinggi":
            return "Tunda Tanam — Risiko genangan dan busuk batang tinggi."

        return "Menunggu Kondisi Tanam — Evaluasi kelembapan tanah."

    if 0 <= hst <= 30:

        if kategori == "Rendah":
            return "Penyiraman Intensif — Tanah harus lembap agar tunas muncul."

        if kategori == "Tinggi":
            return "Perbaikan Drainase — Hindari genangan, cegah busuk bibit."

        return "Pemantauan Awal — Kelembapan cukup untuk pertumbuhan awal."

    if 31 <= hst <= 90:

        if kategori == "Normal" and hst <= 60:
            return "Pemupukan NPK Tahap 1 — Nutrisi diserap optimal saat air cukup."

        if kategori == "Rendah":
            return "Mulsa / Pengairan — Cegah tanaman kerdil akibat kekeringan."

        if kategori == "Tinggi":
            return "Penyiangan Gulma — Hujan tinggi memicu pertumbuhan gulma."

        return "Pemantauan Vegetatif — Pertumbuhan berlangsung normal."

    if 91 <= hst <= 180:

        if kategori == "Normal" and hst <= 150:
            return "Pemupukan Tahap 2 (Tinggi K) — Fokus pembesaran umbi."

        if kategori == "Rendah":
            return "Kritikal! Harus Diairi — Kekeringan menurunkan hasil umbi drastis."

        if kategori == "Tinggi":
            return "Pemantauan Drainase — Hindari kelebihan air di fase umbi."

        return "Pemantauan Umbi — Kondisi relatif stabil."

    if hst > 180:

        if hst > 240 and kategori == "Rendah":
            return "Waktu Panen Ideal — Kadar pati maksimal & tanah mudah digali."

        if kategori == "Tinggi":
            return "Tunda Panen — Kadar pati turun akibat pertumbuhan vegetatif ulang."

        return "Siap Panen — Evaluasi ukuran dan kualitas umbi."

    return "Pemantauan Rutin — Lanjutkan observasi lapangan."

def label_singkat(aktivitas):

    if "Tanam" in aktivitas:
        return "Penanaman"

    if "Pemupukan" in aktivitas:
        return "Pemupukan"

    if "Penyiraman" in aktivitas:
        return "Penyiraman"

    if "Gulma" in aktivitas:
        return "Pembersihan Gulma"

    if "Panen" in aktivitas:
        return "Pemanenan"

    return "Pemantauan"
