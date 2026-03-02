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

# State untuk Navigasi Bulan & Hari Terpilih
if "view_date" not in st.session_state:
    st.session_state.view_date = date(2026, 3, 1)

if "selected_day" not in st.session_state:
    st.session_state.selected_day = date.today().day

# =========================
# 2. SIDEBAR (PENGATURAN)
# =========================
st.sidebar.title("⚙️ Pengaturan")
kec_list = sorted(data["kecamatan"].unique())
sel_kecamatan = st.sidebar.selectbox("Pilih Kecamatan", kec_list)
tgl_tanam = st.sidebar.date_input("Tanggal Tanam", value=date(2026, 3, 1))

# Jalankan Forecast (31 hari agar mencakup semua kemungkinan tgl di bulan)
kec_id = encoder.transform([sel_kecamatan])[0]
df_kec = data[data["kecamatan"] == sel_kecamatan].copy().sort_values("tanggal")
rain_last270 = df_kec["rain_mm"].values[-270:]
forecast_30 = recursive_forecast(model=model, scaler=scaler, rain_last270=rain_last270, kec_id=kec_id, days=31)

# =========================
# 3. CSS CUSTOM (Center Text & Blocks)
# =========================
st.markdown("""
<style>
    /* Kotak Kalender */
    div.stButton > button {
        height: 120px;
        width: 100%;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        background-color: white;
        display: flex;
        flex-direction: column;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        transition: 0.2s;
        padding: 10px !important;
        white-space: pre-wrap;
    }
    
    div.stButton > button:hover {
        border-color: #2563eb;
        background-color: #f9fafb;
    }

    div.stButton > button:focus {
        border: 2px solid #2563eb !important;
        background-color: #eff6ff !important;
    }

    /* Angka Tanggal Utama */
    div.stButton > button p {
        font-size: 24px !important;
        font-weight: bold !important;
        margin: 0 !important;
        line-height: 1.2 !important;
    }

    /* Status Text di bawah Angka */
    .status-subtext {
        font-size: 11px;
        font-weight: bold;
        margin-top: 5px;
        display: block;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# 4. MAIN LAYOUT
# =========================
col1, col2 = st.columns([3, 1])

with col1:
    # --- NAVIGASI BULAN ---
    n_col1, n_col2, n_col3 = st.columns([1, 2, 1])
    with n_col1:
        if st.button("⬅ Sebelumnya", key="prev_btn"):
            st.session_state.view_date -= relativedelta(months=1)
            st.rerun()
    with n_col2:
        cv = st.session_state.view_date
        st.markdown(f"<h2 style='text-align:center; margin-top:-5px;'>{calendar.month_name[cv.month]} {cv.year}</h2>", unsafe_allow_html=True)
    with n_col3:
        if st.button("Selanjutnya ➡️", key="next_btn"):
            st.session_state.view_date += relativedelta(months=1)
            st.rerun()

    # --- HEADER HARI ---
    h_cols = st.columns(7)
    for i, h in enumerate(["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]):
        h_cols[i].markdown(f"<p style='text-align:center; font-weight:bold; color:gray;'>{h}</p>", unsafe_allow_html=True)

    # --- GRID KALENDER ---
    cal_matrix = calendar.monthcalendar(cv.year, cv.month)
    for week in cal_matrix:
        w_cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                w_cols[i].write("")
            else:
                curr_dt = date(cv.year, cv.month, day)
                hst = (curr_dt - tgl_tanam).days
                
                # Ambil Prediksi Hujan & Logika RBS
                idx = min(max(0, day - 1), len(forecast_30) - 1)
                hujan_val = forecast_30[idx]
                
                # Memanggil fungsi dari utils/rbs.py
                rekom_full = rbs_singkong_final(hujan_val, hst)
                label_txt = label_singkat(rekom_full)

                # Visual Tombol: Angka di atas, Label di bawah (Center)
                btn_display = f"{day}\n{label_txt.upper()}"
                
                if w_cols[i].button(btn_display, key=f"day_{cv.month}_{day}", use_container_width=True):
                    st.session_state.selected_day = day
                    st.rerun()

# =========================
# 5. DETAIL PANEL
# =========================
with col2:
    st.markdown("### 📋 Detail Rekomendasi")
    
    sd = st.session_state.selected_day
    try:
        active_dt = date(cv.year, cv.month, sd)
    except:
        active_dt = date(cv.year, cv.month, 1)

    hst_active = (active_dt - tgl_tanam).days
    idx_active = min(max(0, active_dt.day - 1), len(forecast_30) - 1)
    h_active = forecast_30[idx_active]
    
    # Detail RBS dari utils
    detail_rekom = rbs_singkong_final(h_active, hst_active)

    st.info(f"""
    **📅 Tanggal:** {active_dt.strftime('%d %B %Y')}  
    **🌱 Usia (HST):** {hst_active} hari  
    **☔ Prediksi Hujan:** {h_active:.2f} mm
    """)

    st.success(f"**💡 Saran Aktivitas:**\n{detail_rekom}")

    st.divider()
    st.markdown("**Tren Curah Hujan (30 Hari)**")
    st.line_chart(forecast_30)
