def warna_aktivitas(a):
    if "Penanaman" in a:
        return "#2ecc71"
    if "Pemupukan" in a:
        return "#3498db"
    if "Hama" in a:
        return "#f39c12"
    if "Panen" in a:
        return "#9b59b6"
    return "#95a5a6"
