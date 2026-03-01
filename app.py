import streamlit as st
import calendar
from datetime import datetime
import pandas as pd
import numpy as np

from utils.loader import load_all
from utils.forecast import recursive_forecast
from utils.rbs import rbs_singkong_final, label_singkat

st.set_page_config(page_title="Kalender Tanam Singkong", layout="wide")

@st.cache_resource
def init():
    return load_all()

model, encoder, scaler, data = init()

# ==============================
# SIDEBAR
# ==============================
st.sidebar.title("Pengaturan")

kecamatan = st.sidebar.selectbox("Pilih Kecamatan", encoder.classes_)
tanggal_tanam = st.sidebar.date_input("Tanggal Tanam", value=datetime.today())
kec_id = encoder.transform([kecamatan])[0]

# ==============================
# DATA
# ==============================
data["tanggal"] = pd.to_datetime(data["tanggal"])
df_kec = data[data["kecamatan"] == kecamatan].sort_values("tanggal")

rain_last270 = df_kec["rain_mm"].values[-270:]
forecast = recursive_forecast(model, scaler, rain_last270, kec_id, days=31)

# ==============================
# NAVIGASI BULAN
# ==============================
if "month" not in st.session_state:
    st.session_state.month = datetime.today().month

if "year" not in st.session_state:
    st.session_state.year = datetime.today().year

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

st.markdown(f"<h2 style='text-align:center'>{calendar.month_name[month]} {year}</h2>", unsafe_allow_html=True)

days_in_month = calendar.monthrange(year, month)[1]
predictions = forecast[:days_in_month]

# ==============================
# SELECTED DAY
# ==============================
query_params = st.query_params
selected_day = int(query_params.get("day", 1))
if selected_day > days_in_month:
    selected_day = 1

# ==============================
# WARNA SMOOTH PROFESSIONAL
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
# BUILD FULL CALENDAR GRID HTML
# ==============================
calendar_html = """
<style>
.calendar-grid {
    display:grid;
    grid-template-columns: repeat(7, 1fr);
    gap:12px;
}
.day-card {
    height:100px;
    border-radius:16px;
    padding:10px;
    color:white;
    text-align:center;
    box-shadow:0 4px 10px rgba(0,0,0,0.15);
    text-decoration:none;
    display:flex;
    flex-direction:column;
    justify-content:center;
    align-items:center;
    transition:0.2s;
}
.day-card:hover {
    transform:translateY(-3px);
    box-shadow:0 8px 18px rgba(0,0,0,0.25);
}
.day-number {
    font-size:20px;
    font-weight:bold;
}
.day-label {
    font-size:13px;
    margin-top:6px;
}
.selected {
    border:3px solid white;
}
.today {
    border:3px solid black;
}
@media(max-width:768px){
    .day-card{
        height:80px;
        font-size:11px;
    }
}
</style>

<div class="calendar-grid">
"""

cal = calendar.monthcalendar(year, month)
today = datetime.today()

for week in cal:
    for day in week:
        if day == 0:
            calendar_html += "<div></div>"
        else:
            hujan = predictions[day-1]
            tanggal_prediksi = datetime(year, month, day)
            hst = (tanggal_prediksi.date() - tanggal_tanam).days

            aktivitas_full = rbs_singkong_final(hujan, hst)
            label = label_singkat(aktivitas_full)

            color = color_map.get(label, "#546E7A")

            extra_class = ""
            if day == selected_day:
                extra_class += " selected"
            if day == today.day and month == today.month and year == today.year:
                extra_class += " today"

            calendar_html += f"""
            <a href="?day={day}" 
               class="day-card{extra_class}" 
               style="background:{color};">
                <div class="day-number">{day}</div>
                <div class="day-label">{label}</div>
            </a>
            """

calendar_html += "</div>"

# ==============================
# LAYOUT
# ==============================
left, right = st.columns([2.5,1])

with left:
    st.markdown(calendar_html, unsafe_allow_html=True)

with right:
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
