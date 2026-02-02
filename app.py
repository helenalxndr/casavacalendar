import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from components.header import render_header
from components.calendar_view import render_calendar
from components.detail_panel import render_detail_panel
from components.summary_cards import render_summary
from utils.data_loader import load_all
from utils.forecast import build_dashboard_df


# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="Kalender Tanam Singkong",
    layout="wide"
)

st.title("📅 Kalender Tanam Singkong")
st.caption("Prediksi waktu tanam berbasis LSTM dan data iklim")


# ===============================
# LOAD RESOURCE (CACHED)
# ===============================
@st.cache_resource
def load_resources():
    return load_all()

df_all, model, scaler, encoder, features = load_resources()


# ===============================
# HEADER (FILTER)
# ===============================
kecamatan, tanggal_acuan = render_header(df_all)

if kecamatan is None or tanggal_acuan is None:
    st.info("Silakan pilih kecamatan dan tanggal terlebih dahulu.")
    st.stop()


# ===============================
# BUILD DASHBOARD DATA
# ===============================
df_dashboard = build_dashboard_df(
    df_all=df_all,
    model=model,
    scaler=scaler,
    encoder=encoder,
    features=features,
    kecamatan=kecamatan,
    tanggal_acuan=tanggal_acuan
)

if df_dashboard.empty:
    st.warning("Data tidak tersedia untuk pilihan tersebut.")
    st.stop()


# ===============================
# LAYOUT
# ===============================
col_kal, col_detail = st.columns([3, 2])

with col_kal:
    calendar_state = render_calendar(
        df_dashboard=df_dashboard,
        tanggal_acuan=tanggal_acuan
    )

with col_detail:
    if calendar_state:
        render_detail_panel(
            df_dashboard=df_dashboard,
            calendar_state=calendar_state
        )
    else:
        st.info("Klik salah satu tanggal pada kalender untuk melihat detail.")


# ===============================
# SUMMARY
# ===============================
render_summary(df_dashboard)
