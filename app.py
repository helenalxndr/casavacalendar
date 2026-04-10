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
df_kec = data[data[ "kecamatan" ] == sel_kecamatan].copy().sort_values("tanggal")
rain_last270 = df_kec["rain_mm"].values[-270:]
forecast_30 = recursive_forecast(model=model, scaler=scaler, rain_last270=rain_last270, kec_id=kec_id, days=31)

# =========================
# 3. CSS CUSTOM (Center, Small Font, Uniform Nav)
# =========================
st.markdown("""
<style>
    /* Styling Navigasi Bulan */
    .stButton > button[key="prev_btn"], .stButton > button[key="next_btn"] {
        background-color: #f3f4f6 !important;
        border: 1px solid #d1d5db !important;
        font-weight: bold !important;
        color: #374151 !important;
    }

    /* Kotak Kalender */
    div.stButton > button {
        height: 105px !important;
        width: 100% !important;
        border-radius: 10px !important;
        border: 1px solid #e5e7eb !important;
        background-color: white !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        padding: 5px !important;
        white-space: pre-wrap !important; /* Menjaga baris baru */
    }
    
    /* Angka Tanggal (Besar & Center) */
    div.stButton > button p {
        font-size: 18px !important;
        font-weight: 800 !important;
        margin: 0 !important;
        color: #111827 !important;
    }

    /* Teks Label (Kecil agar tidak patah) */
    div.stButton > button div {
        font-size: 9px !important;
        margin-top: 5px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        line-height: 1 !important;
        color: #6b7280 !important;
    }

    div.stButton > button:hover { border-color: #2563eb !important; background-color: #f9fafb !important; }
    div.stButton > button:focus { border: 2px solid #2563eb !important; background-color: #eff6ff !important; }
</style>
""", unsafe_allow_html=True)

# =========================
# 4. MAIN LAYOUT
# =========================
col1, col2 = st.columns([3, 1])

with col1:
    # --- NAVIGASI BULAN (Ikon Seragam: Panah Modern) ---
    n1, n2, n3 = st.columns([1, 2, 1])
    with n1:
        if st.button("❮ Sebelumnya", key="prev_btn", use_container_width=True):
            st.session_state.view_date -= relativedelta(months=1)
            st.rerun()
    with n2:
        cv = st.session_state.view_date
        st.markdown(f"<h3 style='text-align:center; margin:0;'>{calendar.month_name[cv.month]} {cv.year}</h3>", unsafe_allow_html=True)
    with n3:
        if st.button("Selanjutnya ❯", key="next_btn", use_container_width=True):
            st.session_state.view_date += relativedelta(months=1)
            st.rerun()

    st.write("") 

    # Header Hari
    h_cols = st.columns(7)
    for i, h in enumerate(["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]):
        h_cols[i].markdown(f"<p style='text-align:center; font-weight:bold; color:gray; font-size:12px;'>{h}</p>", unsafe_allow_html=True)

    # Grid Kalender
    cal_matrix = calendar.monthcalendar(cv.year, cv.month)
    for week in cal_matrix:
        w_cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                w_cols[i].write("")
            else:
                curr_dt = date(cv.year, cv.month, day)
                hst = (curr_dt - tgl_tanam).days
                
                # Prediksi & RBS
                idx = min(max(0, day - 1), len(forecast_30) - 1)
                hujan_val = forecast_30[idx]
                
                rekom_full = rbs_singkong_final(hujan_val, hst)
                label_txt = label_singkat(rekom_full)

                # Format Teks: Angka Tanggal \n Nama Aktivitas
                # CSS di atas akan otomatis membuat angka jadi besar dan teks jadi kecil
                display_btn = f"{day}\n{label_txt}"
                
                if w_cols[i].button(display_btn, key=f"day_{cv.month}_{day}", use_container_width=True):
                    st.session_state.selected_day = day
                    st.rerun()

# =========================
# 5. DETAIL PANEL
# =========================
with col2:
    st.markdown("### 📋 Detail Hari")
    sd = st.session_state.selected_day
    try: active_dt = date(cv.year, cv.month, sd)
    except: active_dt = date(cv.year, cv.month, 1)

    hst_active = (active_dt - tgl_tanam).days
    idx_a = min(max(0, active_dt.day - 1), len(forecast_30) - 1)
    h_a = forecast_30[idx_a]
    rekom_d = rbs_singkong_final(h_a, hst_active)

    st.info(f"**Tanggal:** {active_dt.strftime('%d %B %Y')}\n\n**HST:** {hst_active} hari\n\n**Hujan:** {h_a:.2f} mm")
    st.success(f"**Rekomendasi:**\n{rekom_d}")
    st.divider()
    st.line_chart(forecast_30)
