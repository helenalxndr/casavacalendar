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
st.set_page_config(
    page_title="Kalender Tanam Singkong",
    layout="wide"
)

# =========================================================
# LOAD RESOURCE
# =========================================================
@st.cache_resource
def init():
    return load_all()

model, encoder, scaler, data = init()

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("Pengaturan")

kecamatan = st.sidebar.selectbox(
    "Pilih Kecamatan",
    encoder.classes_
)

tanggal_tanam = st.sidebar.date_input(
    "Tanggal Tanam",
    value=datetime.today()
)

kec_id = encoder.transform([kecamatan])[0]

# =========================================================
# VALIDASI & PREP DATA
# =========================================================
if "index" in data.columns:
    data["tanggal"] = pd.to_datetime(data["index"])
elif "tanggal" in data.columns:
    data["tanggal"] = pd.to_datetime(data["tanggal"])
else:
    st.error("Kolom tanggal tidak ditemukan.")
    st.stop()

if "rain_mm" not in data.columns:
    if "curah_hujan_mm" in data.columns:
        data["rain_mm"] = data["curah_hujan_mm"]
    else:
        st.error("Kolom curah hujan tidak ditemukan.")
        st.stop()

data["kecamatan"] = data["kecamatan"].astype(str)

df_kec = (
    data[data["kecamatan"] == kecamatan]
    .sort_values("tanggal")
)

if df_kec.empty:
    st.error("Data kecamatan tidak ditemukan.")
    st.stop()

if len(df_kec) < 270:
    st.error("Data historis kurang dari 270 hari.")
    st.stop()

rain_last270 = df_kec["rain_mm"].values[-270:]

# =========================================================
# FORECAST
# =========================================================
forecast = recursive_forecast(
    model,
    scaler,
    rain_last270,
    kec_id,
    days=31
)

# =========================================================
# HEADER
# =========================================================
st.title("Kalender Tanam Singkong")
st.caption("Rekomendasi berbasis Prediksi Curah Hujan + Fase Pertumbuhan (HST)")

# =========================================================
# NAVIGASI BULAN & TAHUN
# =========================================================
nav1, nav2 = st.columns(2)

with nav1:
    month = st.selectbox(
        "Pilih Bulan",
        list(range(1, 13)),
        index=datetime.today().month - 1,
        format_func=lambda x: calendar.month_name[x]
    )

with nav2:
    year = st.number_input(
        "Tahun",
        min_value=2020,
        max_value=2035,
        value=datetime.today().year
    )

days_in_month = calendar.monthrange(year, month)[1]
predictions = forecast[:days_in_month]

# reset selected_day kalau pindah bulan
if "selected_day" not in st.session_state:
    st.session_state.selected_day = 1

if st.session_state.selected_day > days_in_month:
    st.session_state.selected_day = 1

# =========================================================
# LAYOUT
# =========================================================
left, right = st.columns([2.5, 1])

# =========================================================
# KALENDER
# =========================================================
with left:

    st.subheader(f"{calendar.month_name[month]} {year}")

    # CSS agar tombol seragam
    st.markdown("""
        <style>
        div.stButton > button {
            height: 95px;
            width: 100%;
            border-radius: 12px;
            font-size: 13px;
            text-align: left;
            padding: 10px;
            white-space: pre-line;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header hari
    header = st.columns(7)
    for i, day_name in enumerate(["Sen","Sel","Rab","Kam","Jum","Sab","Min"]):
        header[i].markdown(f"**{day_name}**")

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

                aktivitas = rbs_singkong_final(hujan, hst)
                aktivitas_short = aktivitas.split("—")[0]

                label = f"{day}\n{aktivitas_short}"

                if cols[i].button(label, key=f"day_{year}_{month}_{day}"):
                    st.session_state.selected_day = day

# =========================================================
# DETAIL PANEL
# =========================================================
with right:

    selected = st.session_state.selected_day

    hujan = predictions[selected-1]
    tanggal_selected = datetime(year, month, selected)
    hst_selected = (tanggal_selected.date() - tanggal_tanam).days

    aktivitas = rbs_singkong_final(hujan, hst_selected)

    st.subheader("Detail Tanggal")

    st.write(
        f"**Tanggal:** {selected} "
        f"{calendar.month_name[month]} {year}"
    )

    st.write(f"**HST:** {hst_selected} hari")

    st.metric(
        "Prediksi Hujan",
        f"{hujan:.2f} mm"
    )

    st.markdown("### Rekomendasi")
    st.info(aktivitas)

    st.markdown("---")

    # =========================================================
    # RINGKASAN BULANAN
    # =========================================================
    summary = []

    for day in range(1, days_in_month+1):
        tanggal_loop = datetime(year, month, day)
        hst_loop = (tanggal_loop.date() - tanggal_tanam).days
        hujan_loop = predictions[day-1]
        aktivitas_loop = rbs_singkong_final(hujan_loop, hst_loop)
        summary.append(aktivitas_loop.split("—")[0])

    df_summary = pd.Series(summary)

    st.subheader("Ringkasan Aktivitas")

    for aktivitas_name, jumlah in df_summary.value_counts().items():
        st.write(f"{aktivitas_name}: {jumlah} hari")
