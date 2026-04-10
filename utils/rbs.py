def rbs_singkong_final(hujan_mm, hst):

    kategori = kategori_hujan(hujan_mm)
    hst = int(hst)

    # ================= PRA TANAM =================
    if hst < 0:
        if kategori == "Sedang":
            return ("🌱 Masa Tanam Ideal",
                    "Kondisi tanah sudah cukup baik. Anda bisa mulai menanam untuk mendapatkan hasil pertumbuhan yang optimal.")
        elif kategori == "Rendah":
            return ("⏳ Sebaiknya Menunda Tanam",
                    "Tanah masih terlalu kering. Menunggu hujan atau melakukan pengairan akan membantu bibit tumbuh lebih baik.")
        elif kategori == "Tinggi":
            return ("⏳ Sebaiknya Menunda Tanam",
                    "Curah hujan cukup tinggi, berisiko genangan. Menunggu kondisi lebih stabil akan lebih aman.")
        return ("ℹ️ Menunggu Kondisi Terbaik",
                "Kondisi lahan masih perlu diamati sebelum memulai penanaman.")

    # ================= AWAL =================
    if 0 <= hst <= 30:
        if kategori == "Rendah":
            return ("💧 Pendampingan Penyiraman",
                    "Tanaman masih muda dan membutuhkan tambahan air agar akar dapat berkembang dengan baik.")
        elif kategori == "Tinggi":
            return ("🌧️ Perhatian Drainase",
                    "Air cukup tinggi, pastikan tidak terjadi genangan agar akar tetap sehat.")
        return ("🌱 Masa Pertumbuhan Awal",
                "Tanaman sedang beradaptasi dengan lingkungan. Kondisi saat ini cukup baik.")

    # ================= VEGETATIF =================
    if 31 <= hst <= 90:
        if kategori == "Sedang" and hst <= 60:
            return ("🌿 Waktu Pemupukan Awal",
                    "Nutrisi tambahan akan membantu tanaman tumbuh lebih kuat dan sehat.")
        elif kategori == "Rendah":
            return ("💧 Dukungan Air & Mulsa",
                    "Tanaman membutuhkan kelembapan agar tidak mengalami stres kekeringan.")
        elif kategori == "Tinggi":
            return ("🌿 Pengendalian Gulma",
                    "Pertumbuhan gulma lebih cepat saat hujan tinggi, perlu perhatian tambahan.")
        return ("🌱 Pertumbuhan Vegetatif Stabil",
                "Tanaman sedang tumbuh dengan baik dan tidak membutuhkan tindakan khusus.")

    # ================= UMBI =================
    if 91 <= hst <= 180:
        if kategori == "Sedang" and hst <= 150:
            return ("🌿 Pemupukan Lanjutan",
                    "Nutrisi tambahan membantu pembentukan umbi yang lebih optimal.")
        elif kategori == "Rendah":
            return ("💧 Perhatian Kelembapan",
                    "Tanah terlalu kering dapat menghambat pembentukan umbi.")
        elif kategori == "Tinggi":
            return ("🌧️ Pengawasan Drainase",
                    "Kelebihan air bisa mengganggu perkembangan umbi.")
        return ("🌾 Masa Pembentukan Umbi",
                "Tanaman sedang fokus membentuk umbi. Kondisi relatif stabil.")

    # ================= PANEN =================
    if hst > 180:
        if hst > 240 and kategori == "Rendah":
            return ("🌾 Waktu Panen Terbaik",
                    "Umbi sudah matang optimal dan siap dipanen dengan hasil maksimal.")
        elif kategori == "Tinggi":
            return ("⏳ Pertimbangkan Menunda Panen",
                    "Kondisi masih lembap, menunggu waktu lebih kering dapat menjaga kualitas hasil.")
        return ("🌾 Siap Panen",
                "Tanaman sudah berada pada fase panen. Silakan evaluasi kondisi lapangan.")

    return ("ℹ️ Pemantauan Rutin",
            "Tanaman dalam kondisi normal. Tetap lakukan pengamatan berkala.")
