import streamlit as st
import calendar
from datetime import datetime
import numpy as np
import pandas as pd

from utils.loader import load_all
from utils.forecast import recursive_forecast
from utils.rbs import rbs_singkong

# ==============================
# CONFIG
# ==============================
st.set_page_config(
    page_title="Kalender Tanam Singkong",
    layout="wide"
)

# ==============================
# LOAD RESOURCE (CACHE)
# ==============================
@st.cache_resource
def init():
    return load_all()

model, encoder, scaler, data = init()

# ==============================
# SIDEBAR
# ==============================
st.sidebar.title("Lokasi")

kecamatan = st.sidebar.selectbox(
    "Pilih Kecamatan",
    encoder.classes_
)

kec_id = encoder.transform([kecamatan])[0]

# ==============================
# AMBIL 270 HARI TERAKHIR
# ==============================
df_kec = data[data["kecamatan"] == kecamatan] \
            .sort_values("tanggal")

rain_last270 = df_kec["rain_mm"].values[-270:]

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
# SET BULAN AKTIF
# ==============================
today = datetime.today()
year = today.year
month = today.month
days = calendar.monthrange(year, month)[1]

predictions = forecast[:days]

if "selected_day" not in st.session_state:
    st.session_state.selected_day = 1

# ==============================
# UI
# ==============================
st.title("Kalender Tanam Singkong")
st.caption("Rekomendasi aktivitas berdasarkan prediksi curah hujan harian")

left, right = st.columns([2.5,1])

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
                aktivitas = rbs_singkong(hujan)

                if cols[i].button(
                    f"{day}\n{aktivitas}",
                    key=f"day_{day}"
                ):
                    st.session_state.selected_day = day

# ==============================
# DETAIL PANEL
# ==============================
with right:

    selected = st.session_state.selected_day

    hujan = predictions[selected-1]
    aktivitas = rbs_singkong(hujan)

    st.subheader("Detail Tanggal")

    st.write(
        f"**Tanggal:** {selected} "
        f"{calendar.month_name[month]} {year}"
    )

    st.metric(
        "Prediksi Hujan",
        f"{hujan:.2f} mm"
    )

    st.write("Aktivitas:", aktivitas)

    st.markdown("---")

    df_summary = pd.DataFrame({
        "hujan": predictions
    })

    df_summary["aktivitas"] = \
        df_summary["hujan"].apply(rbs_singkong)

    st.write("Hari tanam:",
             (df_summary["aktivitas"]=="Penanaman").sum())

    st.write("Hari pupuk:",
             (df_summary["aktivitas"]=="Pemupukan").sum())

    st.write("Hari hama:",
             (df_summary["aktivitas"]=="Pembersihan Hama").sum())

    st.write("Hari panen:",
             (df_summary["aktivitas"]=="Panen").sum())
