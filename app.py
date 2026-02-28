import streamlit as st
import calendar
from datetime import datetime
import numpy as np
import pandas as pd

from utils.loader import load_all
from utils.forecast import recursive_forecast
from utils.rbs import rbs_singkong_final

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="Kalender Tanam Singkong", layout="wide")

# =========================================================
# LOAD
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

col1, col2, col3 = st.columns([1,6,1])

with col1:
    if st.button("<"):
        if st.session_state.month == 1:
            st.session_state.month = 12
            st.session_state.year -= 1
        else:
            st.session_state.month -= 1

with col3:
    if st.button(">"):
        if st.session_state.month == 12:
            st.session_state.month = 1
            st.session_state.year += 1
        else:
            st.session_state.month += 1

month = st.session_state.month
year = st.session_state.year

st.markdown(f"<h2 style='text-align:center;'>{calendar.month_name[month]} {year}</h2>", unsafe_allow_html=True)

days_in_month = calendar.monthrange(year, month)[1]
predictions = forecast[:days_in_month]

# =========================================================
# WARNA
# =========================================================
def warna_fase(aktivitas):

    if "Waktu Tanam Ideal" in aktivitas:
        return "#00C853"
    if "Tunda Tanam" in aktivitas:
        return "#D50000"
    if "Penyiraman" in aktivitas:
        return "#2962FF"
    if "Pemupukan" in aktivitas:
        return "#FF6D00"
    if "Panen" in aktivitas:
        return "#FFD600"
    return "#455A64"

# =========================================================
# LAYOUT
# =========================================================
left, right = st.columns([2.5,1])

# =========================================================
# KALENDER PREMIUM
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

                aktivitas = rbs_singkong_final(hujan, hst)
                color = warna_fase(aktivitas)

                border = ""
                if (day == today.day and month == today.month and year == today.year):
                    border = "border:3px solid black;"

                box = f"""
                <div style="
                    background:{color};
                    padding:10px;
                    border-radius:10px;
                    color:white;
                    height:85px;
                    {border}">
                    <b>{day}</b><br>
                    {aktivitas}
                </div>
                """

                cols[i].markdown(box, unsafe_allow_html=True)

# =========================================================
# PANEL DETAIL
# =========================================================
with right:

    st.subheader("Grafik Prediksi Hujan")

    df_chart = pd.DataFrame({
        "Hari": list(range(1, days_in_month+1)),
        "Hujan": predictions[:days_in_month]
    })

    st.line_chart(df_chart.set_index("Hari"))
