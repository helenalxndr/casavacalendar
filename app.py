import streamlit as st
import calendar
from datetime import datetime
import numpy as np
import pandas as pd

from utils.loader import load_all
from utils.forecast import recursive_forecast
from utils.rbs import rbs_singkong_final, label_singkat

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="Kalender Tanam Singkong", layout="wide")

# =========================================================
# LOAD MODEL & DATA
# =========================================================
@st.cache_resource
def init():
    return load_all()

model, encoder, scaler, data = init()

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("Pengaturan")

kecamatan = st.sidebar.selectbox("Pilih Kecamatan", encoder.classes_)
tanggal_tanam = st.sidebar.date_input("Tanggal Tanam", value=datetime.today())
kec_id = encoder.transform([kecamatan])[0]

# =========================================================
# DATA PREP
# =========================================================
data["tanggal"] = pd.to_datetime(data["tanggal"])
df_kec = data[data["kecamatan"] == kecamatan].sort_values("tanggal")

rain_last270 = df_kec["rain_mm"].values[-270:]
forecast = recursive_forecast(model, scaler, rain_last270, kec_id, days=31)

# =========================================================
# NAVIGASI BULAN
# =========================================================
if "month" not in st.session_state:
    st.session_state.month = datetime.today().month

if "year" not in st.session_state:
    st.session_state.year = datetime.today().year

if "selected_day" not in st.session_state:
    st.session_state.selected_day = 1

col1, col2, col3 = st.columns([1,6,1])

with col1:
    if st.button("◀"):
        if st.session_state.month == 1:
            st.session_state.month = 12
            st.session_state.year -= 1
        else:
            st.session_state.month -= 1

with col3:
    if st.button("▶"):
        if st.session_state.month == 12:
            st.session_state.month = 1
            st.session_state.year += 1
        else:
            st.session_state.month += 1

month = st.session_state.month
year = st.session_state.year

st.markdown(
    f"<h2 style='text-align:center;'>{calendar.month_name[month]} {year}</h2>",
    unsafe_allow_html=True
)

days_in_month = calendar.monthrange(year, month)[1]
predictions = forecast[:days_in_month]

# =========================================================
# WARNA AKTIVITAS
# =========================================================
color_map = {
    "Penanaman": "#43A047",
    "Pemupukan": "#FB8C00",
    "Penyiraman": "#1E88E5",
    "Pembersihan Gulma": "#8E24AA",
    "Pemanenan": "#FDD835",
    "Pemantauan": "#546E7A"
}

# =========================================================
# LAYOUT
# =========================================================
left, right = st.columns([2.5,1])

# =========================================================
# KALENDER (TAMPILAN CLEAN + CLICKABLE)
# =========================================================
with left:

    header = st.columns(7)
    for i, d in enumerate(["Sen","Sel","Rab","Kam","Jum","Sab","Min"]):
        header[i].markdown(f"**{d}**")

    cal = calendar.monthcalendar(year, month)
    today = datetime.today()

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

                bg_color = color_map.get(label, "#546E7A")

                border = ""
                if day == today.day and month == today.month and year == today.year:
                    border = "border:3px solid black;"

                if st.session_state.selected_day == day:
                    border = "border:3px solid white; box-shadow:0 0 10px rgba(0,0,0,0.4);"

                box_html = f"""
                <div style="
                    background:{bg_color};
                    padding:10px;
                    border-radius:14px;
                    color:white;
                    height:85px;
                    text-align:center;
                    {border}">
                    <div style="font-size:20px;font-weight:bold;">{day}</div>
                    <div style="font-size:13px;">{label}</div>
                </div>
                """

                with cols[i]:
                    # Invisible button trigger
                    if st.button("", key=f"btn_{day}"):
                        st.session_state.selected_day = day

                    st.markdown(box_html, unsafe_allow_html=True)

# =========================================================
# PANEL DETAIL
# =========================================================
with right:

    selected = st.session_state.selected_day

    hujan = predictions[selected-1]
    tanggal_selected = datetime(year, month, selected)
    hst_selected = (tanggal_selected.date() - tanggal_tanam).days

    aktivitas_full = rbs_singkong_final(hujan, hst_selected)

    st.subheader("Detail Rekomendasi")

    st.write(f"📅 {selected} {calendar.month_name[month]} {year}")
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
