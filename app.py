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
    f"<h2 style='text-align:center; margin-bottom:30px;'>{calendar.month_name[month]} {year}</h2>",
    unsafe_allow_html=True
)

days_in_month = calendar.monthrange(year, month)[1]
predictions = forecast[:days_in_month]

# =========================================================
# HANDLE SELECTED DAY (QUERY PARAM)
# =========================================================
query_params = st.query_params
selected_day = int(query_params.get("day", 1))

if selected_day > days_in_month:
    selected_day = 1

# =========================================================
# WARNA PROFESIONAL (SOFT & SMOOTH)
# =========================================================
color_map = {
    "Penanaman": "linear-gradient(135deg, #2E7D32, #66BB6A)",
    "Pemupukan": "linear-gradient(135deg, #EF6C00, #FFA726)",
    "Penyiraman": "linear-gradient(135deg, #1565C0, #42A5F5)",
    "Pembersihan Gulma": "linear-gradient(135deg, #6A1B9A, #AB47BC)",
    "Pemanenan": "linear-gradient(135deg, #F9A825, #FFD54F)",
    "Pemantauan": "linear-gradient(135deg, #37474F, #78909C)"
}

# =========================================================
# LAYOUT
# =========================================================
left, right = st.columns([2.5,1])

# =========================================================
# KALENDER SUPER CLEAN
# =========================================================
with left:

    # CSS Modern Smooth
    st.markdown("""
    <style>
    .day-card {
        height:95px;
        border-radius:16px;
        padding:12px;
        color:white;
        text-align:center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transition: all 0.2s ease-in-out;
        text-decoration:none;
        display:block;
    }
    .day-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 18px rgba(0,0,0,0.25);
    }
    .day-number {
        font-size:20px;
        font-weight:bold;
        margin-bottom:6px;
    }
    </style>
    """, unsafe_allow_html=True)

    header = st.columns(7)
    for i, d in enumerate(["Sen","Sel","Rab","Kam","Jum","Sab","Min"]):
        header[i].markdown(f"<center><b>{d}</b></center>", unsafe_allow_html=True)

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

                bg_color = color_map.get(label, "linear-gradient(135deg,#546E7A,#90A4AE)")

                border = ""
                if day == today.day and month == today.month and year == today.year:
                    border = "border:3px solid black;"

                if selected_day == day:
                    border = "border:3px solid white;"

                card_html = f"""
                <a href="?day={day}" class="day-card"
                   style="background:{bg_color}; {border}">
                    <div class="day-number">{day}</div>
                    <div style="font-size:13px;">{label}</div>
                </a>
                """

                cols[i].markdown(card_html, unsafe_allow_html=True)

# =========================================================
# DETAIL PANEL
# =========================================================
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
