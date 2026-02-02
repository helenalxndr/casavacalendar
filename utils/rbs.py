def rbs_singkong_final(hujan_mm, hst):
    """
    Rule-Based System rekomendasi aktivitas singkong
    berdasarkan curah hujan dan HST.
    """

    if hst <= 14:
        return "Penanaman" if 5 <= hujan_mm <= 15 else "Pemantauan Awal"

    if 15 <= hst <= 30:
        return "Pemupukan I" if 5 <= hujan_mm <= 15 else "Tunda Pemupukan"

    if 31 <= hst <= 59:
        return (
            "Pembersihan Hama & Gulma"
            if hujan_mm > 15
            else "Pemantauan"
        )

    if 60 <= hst <= 90:
        if 5 <= hujan_mm <= 15:
            return "Pemupukan II"
        elif hujan_mm > 15:
            return "Pembersihan Hama & Gulma"
        else:
            return "Tunda Pemupukan"

    if 91 <= hst <= 180:
        return (
            "Pembersihan Hama & Gulma"
            if hujan_mm > 15
            else "Pemantauan"
        )

    if 181 <= hst <= 300:
        return "Panen" if hujan_mm < 10 else "Pembersihan Hama & Gulma"

    return "Tidak Disarankan"
