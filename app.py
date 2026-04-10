import streamlit as st
import pandas as pd
import numpy as np
import calendar
import os
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# Import dari folder utils
from utils.loader import load_all
from utils.forecast import recursive_forecast
from utils.rbs import kategori_hujan, rbs_singkong_final, label_singkat

st.set_page_config(layout="wide", page_title="Dashboard Tanam Singkong")

# =========================
# 1. LOAD DATA & INITIAL STATE
# =========================
try:
    model, encoder, scaler, data = load_all()
    data["tanggal"] = pd.to_datetime(data["tanggal"])
except Exception as e:
    st.error(f"Gagal memuat resource: {e}")
    st.stop()

if "view_date" not in st.session_state:
    st.session_state.view_date = date(2026, 3, 1)

if "selected_day" not in st.session_state:
    st.session_state.selected_day = date.today().day

# =========================
# 2. SIDEBAR
# =========================
st.sidebar.title("⚙️ Pengaturan")
kec_list = sorted(data["kecamatan"].unique())
sel_kecamatan = st.sidebar.selectbox("Pilih Kecamatan", kec_list)
tgl_tanam = st.sidebar.date_input("Tanggal Tanam", value=date(2026, 3, 1))

kec_id = encoder.transform([sel_kecamatan])[0]
df_kec = data[data["kecamatan"] == sel_kecamatan].copy().sort_values("tanggal")

rain_last270 = df_kec["rain_mm"].values[-270:]

forecast_30 = recursive_forecast(
    model=model,
    scaler=scaler,
    rain_last270=rain_last270,
    kec_id=kec_id,
    days=31
)

forecast_30 = np.clip(forecast_30, 0, 300)

# =========================
# WARNA AKTIVITAS
# =========================
def warna_aktivitas(label):
    if label == "Penanaman":
        return "#22c55e"
    if label == "Pemupukan":
        return "#3b82f6"
    if label == "Penyiraman":
        return "#06b6d4"
    if label == "Pembersihan Gulma":
        return "#eab308"
    if label == "Pemanenan":
        return "#f97316"
    if label == "Tunda Tanam":
        return "#ef4444"
    return "#9ca3af"

# =========================
# 3. CSS CUSTOM
# =========================
st.markdown("""
<style>
div[data-testid="stButton"] button {
    height: 105px !important;
    width: 100% !important;
    border-radius: 10px !important;
    border: 2px solid #e5e7eb !important;
    background-color: white !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 20px !important;
    font-weight: bold !important;
}

div[data-testid="stButton"] button:hover {
    transform: scale(1.03);
}
</style>
""", unsafe_allow_html=True)

# =========================
# 4. MAIN LAYOUT
# =========================
col1, col2 = st.columns([3, 1])

with col1:
    # NAVIGASI
    n1, n2, n3 = st.columns([1, 2, 1])
    with n1:
        if st.button("❮ Sebelumnya", key="prev_btn", use_container_width=True):
            st.session_state.view_date -= relativedelta(months=1)
            st.rerun()
    with n2:
        cv = st.session_state.view_date
        st.markdown(f"<h3 style='text-align:center'>{calendar.month_name[cv.month]} {cv.year}</h3>", unsafe_allow_html=True)
    with n3:
        if st.button("Selanjutnya ❯", key="next_btn", use_container_width=True):
            st.session_state.view_date += relativedelta(months=1)
            st.rerun()

    st.write("")

    # HEADER HARI
    h_cols = st.columns(7)
    for i, h in enumerate(["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]):
        h_cols[i].markdown(f"<p style='text-align:center; font-weight:bold; color:gray;'>{h}</p>", unsafe_allow_html=True)

    # GRID KALENDER
    cal_matrix = calendar.monthcalendar(cv.year, cv.month)

    for week in cal_matrix:
        w_cols = st.columns(7)
        for i, day in enumerate(week):

            if day == 0:
                w_cols[i].write("")
                continue

            curr_dt = date(cv.year, cv.month, day)
            hst = (curr_dt - tgl_tanam).days

            idx = min(max(0, day - 1), len(forecast_30) - 1)
            hujan_val = forecast_30[idx]

            rekom = rbs_singkong_final(hujan_val, hst)
            label = label_singkat(rekom)
            warna = warna_aktivitas(label)

            key_btn = f"day_{cv.month}_{day}"
            
            clicked = w_cols[i].button(
                str(day),
                key=key_btn,
                use_container_width=True
            )
            
            if clicked:
                st.session_state.selected_day = day
                st.rerun()
            
            # CSS TARGET BERDASARKAN KEY (WORKING)
            st.markdown(f"""
            <style>
            div[data-testid="stButton"]:has(button[data-testid="{key_btn}"]) button {{
                background-color: {warna}40 !important;
                border: 2px solid {warna} !important;
                color: black !important;
            }}
            </style>
            """, unsafe_allow_html=True)

# =========================
# 5. DETAIL PANEL
# =========================
with col2:
    st.markdown("### 📋 Detail Hari")

    sd = st.session_state.selected_day

    try:
        active_dt = date(cv.year, cv.month, sd)
    except:
        active_dt = date(cv.year, cv.month, 1)

    hst_active = (active_dt - tgl_tanam).days
    idx_a = min(max(0, active_dt.day - 1), len(forecast_30) - 1)
    h_a = forecast_30[idx_a]

    rekom_d = rbs_singkong_final(h_a, hst_active)

    st.info(f"""
    **Tanggal:** {active_dt.strftime('%d %B %Y')}

    **HST:** {hst_active} hari  
    **Hujan:** {h_a:.2f} mm  
    """)

    st.success(rekom_d)

    st.divider()
    st.line_chart(forecast_30)
