import streamlit as st
import calendar
from datetime import datetime
import numpy as np
import pandas as pd

from utils.loader import load_all
from utils.forecast import recursive_forecast
from utils.rbs import rbs_singkong_final

# ==============================
# CONFIG
# ==============================
st.set_page_config(
    page_title="Kalender Tanam Singkong",
    layout="wide"
)

# ==============================
# LOAD RESOURCE
# ==============================
@st.cache_resource
def init():
    return load_all()

model, encoder, scaler, data = init()

# ==============================
# SIDEBAR
# ==============================
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

# ==============================
# AMBIL 270 HARI TERAKHIR
# ==============================
if "tanggal" not in data.columns:
    if "index" in data.columns:
        data["tanggal"] = pd.to_datetime(data["index"])
    else:
        st.error("Kolom tanggal tidak ditemukan.")
        st.stop()

df_kec = (
    data[data["kecamatan"] == kecamatan]
    .sort_values("tanggal")
)

# ==============================
# FORECAST 30 HARI
# ==============================
forecast = recursive_forecast(
    model,
    scaler,
    rain_last270,
    kec_id,
    days=30
)

# ==============================
# SET BULAN
# ==============================
today = datetime.today()
year = today.year
month = today.month
days = calendar.monthrange(year, month)[1]

predictions = forecast[:days]

if "selected_day" not in st.session_state:
    st.session_state.selected_day = 1

# ==============================
# UI HEADER
# ==============================
st.title("Kalender Tanam Singkong")
st.caption("Rekomendasi berbasis Prediksi Curah Hujan + Fase Pertumbuhan (HST)")

left, right = st.columns([2.5, 1])

# ==============================
# KALENDER
# ==============================
with left:

    st.subheader(calendar.month_name[month] + " " + str(year))

    cal = calendar.monthcalendar(year, month)

    for week in cal:
        cols = st.columns(7)

        for i, day in enumerate(week):

            if day != 0 and day <= len(predictions):

                hujan = predictions[day-1]

                # Hitung HST per tanggal
                tanggal_prediksi = datetime(year, month, day)
                hst = (tanggal_prediksi.date() - tanggal_tanam).days

                aktivitas = rbs_singkong_final(hujan, hst)

                if cols[i].button(
                    f"{day}\n{aktivitas.split('—')[0]}",
                    key=f"day_{day}"
                ):
                    st.session_state.selected_day = day

# ==============================
# DETAIL PANEL
# ==============================
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

    # ==============================
    # RINGKASAN BULANAN
    # ==============================
    summary = []

    for day in range(1, len(predictions)+1):
        tanggal_loop = datetime(year, month, day)
        hst_loop = (tanggal_loop.date() - tanggal_tanam).days
        hujan_loop = predictions[day-1]
        aktivitas_loop = rbs_singkong_final(hujan_loop, hst_loop)
        summary.append(aktivitas_loop.split("—")[0])

    df_summary = pd.Series(summary)

    st.subheader("Ringkasan Aktivitas")

    for aktivitas in df_summary.value_counts().index:
        st.write(
            aktivitas,
            ":",
            df_summary.value_counts()[aktivitas]
        )
