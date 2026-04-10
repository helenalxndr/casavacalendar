def generate_decision(hujan, hst):
    rekom = rbs_singkong_final(hujan, hst)
    label = label_singkat(rekom)
    return {
        "label": label,
        "rekomendasi": rekom
    }
