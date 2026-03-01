import streamlit as st
import calendar
from datetime import datetime
import pandas as pd
import numpy as np

from utils.loader import load_all
from utils.forecast import recursive_forecast
from utils.rbs import rbs_singkong_final, label_singkat

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Dashboard Kalender Tanam Singkong",
    layout="wide"
)

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
st.sidebar.title("⚙ Pengaturan")

kecamatan = st.sidebar.selectbox("Pilih Kecamatan", encoder.classes_)
tanggal_tanam = st.sidebar.date_input(
    "Tanggal Tanam",
    value=datetime.today()
)

kec_id = encoder.transform([kecamatan])[0]

# =========================================================
# DATA PREPARATION
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

col_prev, col_title, col_next = st.columns([1,6,1])

with col_prev:
    if st.button("◀"):
        if st.session_state.month == 1:
            st.session_state.month = 12
            st.session_state.year -= 1
        else:
            st.session_state.month -= 1

with col_next:
    if st.button("▶"):
        if st.session_state.month == 12:
            st.session_state.month = 1
            st.session_state.year += 1
        else:
            st.session_state.month += 1

month = st.session_state.month
year = st.session_state.year

with col_title:
    st.markdown(
        f"<h2 style='text-align:center'>{calendar.month_name[month]} {year}</h2>",
        unsafe_allow_html=True
    )

days_in_month = calendar.monthrange(year, month)[1]
predictions = forecast[:days_in_month]

# =========================================================
# COLOR MAP PROFESSIONAL
# =========================================================
color_map = {
    "Penanaman": "#2E7D32",
    "Pemupukan": "#EF6C00",
    "Penyiraman": "#1565C0",
    "Pembersihan Gulma": "#6A1B9A",
    "Pemanenan": "#F9A825",
    "Pemantauan": "#455A64"
}

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>
div[data-testid="column"] {
    padding-left:4px !important;
    padding-right:4px !important;
}

div[data-testid="stHorizontalBlock"] {
    gap:6px !important;
}

div.stButton > button {
    height:90px;
    border-radius:14px;
    font-weight:600;
    font-size:14px;
    border:none;
    box-shadow:0 3px 8px rgba(0,0,0,0.12);
    transition:0.2s;
    white-space:pre-line;
    padding:6px;
}

div.stButton > button:hover {
    transform:translateY(-2px);
    box-shadow:0 6px 14px rgba(0,0,0,0.2);
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# LAYOUT
# =========================================================
left, right = st.columns([2.3,1])

# =========================================================
# CALENDAR GRID
# =========================================================
with left:

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

                color = color_map.get(label, "#546E7A")

                button_label = f"{day}\n{label}"

                clicked = cols[i].button(
                    button_label,
                    key=f"day_{day}",
                    use_container_width=True
                )

                if clicked:
                    st.session_state.selected_day = day

                # Dynamic color styling
                st.markdown(f"""
                <style>
                button[key="day_{day}"] {{
                    background:{color} !important;
                    color:white !important;
                }}
                </style>
                """, unsafe_allow_html=True)

# =========================================================
# DETAIL PANEL
# =========================================================
with right:

    selected_day = st.session_state.selected_day

    hujan = predictions[selected_day-1]
    tanggal_selected = datetime(year, month, selected_day)
    hst_selected = (tanggal_selected.date() - tanggal_tanam).days

    aktivitas_full = rbs_singkong_final(hujan, hst_selected)

    st.subheader("📋 Detail Rekomendasi")

    st.write(f"📅 Tanggal : {selected_day} {calendar.month_name[month]} {year}")
    st.write(f"🌱 HST     : {hst_selected} hari")
    st.metric("🌧 Prediksi Hujan", f"{hujan:.2f} mm")

    st.info(aktivitas_full)

    st.divider()

    st.subheader("📈 Grafik Prediksi Hujan")

    df_chart = pd.DataFrame({
        "Hari": list(range(1, days_in_month+1)),
        "Curah Hujan (mm)": predictions
    })

    st.line_chart(df_chart.set_index("Hari"))
