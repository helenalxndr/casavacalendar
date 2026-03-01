# ==============================
# CSS CLEAN PROFESSIONAL
# ==============================
st.markdown("""
<style>
div.stButton > button {
    height:100px;
    border-radius:16px;
    font-weight:600;
    font-size:15px;
    border:none;
    box-shadow:0 4px 10px rgba(0,0,0,0.15);
    transition:0.2s;
}
div.stButton > button:hover {
    transform:translateY(-3px);
    box-shadow:0 8px 18px rgba(0,0,0,0.25);
}
</style>
""", unsafe_allow_html=True)

# ==============================
# SESSION
# ==============================
if "selected_day" not in st.session_state:
    st.session_state.selected_day = 1

# ==============================
# COLOR MAP PROFESSIONAL
# ==============================
color_map = {
    "Penanaman": "#2E7D32",
    "Pemupukan": "#EF6C00",
    "Penyiraman": "#1565C0",
    "Pembersihan Gulma": "#6A1B9A",
    "Pemanenan": "#F9A825",
    "Pemantauan": "#455A64"
}

# ==============================
# KALENDER GRID STABLE
# ==============================
left, right = st.columns([2.5,1])

with left:

    header = st.columns(7)
    for i, d in enumerate(["Sen","Sel","Rab","Kam","Jum","Sab","Min"]):
        header[i].markdown(f"<center><b>{d}</b></center>", unsafe_allow_html=True)

    cal = calendar.monthcalendar(year, month)

    for week in cal:
        cols = st.columns(7)

        for i, day in enumerate(week):

            if day == 0:
                cols[i].write("")
            else:
                hujan = predictions[day-1]
                tanggal_prediksi = datetime(year, month, day)
                hst = (tanggal_prediksi.date() - tanggal_tanam).days

                aktivitas_full = rbs_singkong_final(hujan, hst)
                label = label_singkat(aktivitas_full)

                color = color_map.get(label, "#546E7A")

                button_label = f"{day}\n{label}"

                if cols[i].button(
                    button_label,
                    key=f"day_{day}",
                    use_container_width=True
                ):
                    st.session_state.selected_day = day

                # inject color style per button
                st.markdown(f"""
                <style>
                button[data-testid="baseButton-secondary"][key="day_{day}"] {{
                    background:{color} !important;
                    color:white !important;
                }}
                </style>
                """, unsafe_allow_html=True)

# ==============================
# DETAIL PANEL
# ==============================
with right:

    selected_day = st.session_state.selected_day
    hujan = predictions[selected_day-1]
    tanggal_selected = datetime(year, month, selected_day)
    hst_selected = (tanggal_selected.date() - tanggal_tanam).days
    aktivitas_full = rbs_singkong_final(hujan, hst_selected)

    st.subheader("Detail Rekomendasi")
    st.write(f"📅 {selected_day} {calendar.month_name[month]} {year}")
    st.write(f"🌱 HST: {hst_selected} hari")
    st.metric("🌧 Prediksi Hujan", f"{hujan:.2f} mm")
    st.info(aktivitas_full)

    st.divider()

    st.subheader("Grafik Prediksi Hujan")

    df_chart = pd.DataFrame({
        "Hari": list(range(1, days_in_month+1)),
        "Hujan": predictions
    })

    st.line_chart(df_chart.set_index("Hari"))
