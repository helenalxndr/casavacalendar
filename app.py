import streamlit as st
import pandas as pd
import numpy as np
import calendar
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# --- MOCK / UTILS (Pastikan fungsi ini ada di file lo) ---
from utils.loader import load_all
from utils.forecast import recursive_forecast
from utils.rbs import rbs_singkong_final, label_singkat

st.set_page_config(layout="wide", page_title="Dashboard Tanam Singkong")

# =========================
# 1. LOAD DATA & STATE
# =========================
try:
    model, encoder, scaler, data = load_all()
except:
    st.error("Gagal load data.")
    st.stop()

if "view_date" not in st.session_state:
    st.session_state.view_date = date(2026, 4, 1)

if "selected_day" not in st.session_state:
    st.session_state.selected_day = 10

# =========================
# 2. CSS "BULLETPROOF"
# =========================
# Kita pakai selector yang sangat spesifik untuk menembus proteksi Streamlit
st.markdown("""
<style>
    /* Reset & Dasar Button */
    div.stButton > button {
        height: 110px !important;
        width: 100% !important;
        border-radius: 12px !important;
        border: 2px solid #E2E8F0 !important;
        background-color: white !important; /* Default */
        transition: all 0.2s ease !important;
    }

    /* Penekanan teks dalam button */
    div.stButton > button p { font-size: 22px !important; font-weight: 800 !important; margin: 0 !important; }
    div.stButton > button div { font-size: 10px !important; font-weight: 700 !important; }

    /* PEWARNAAN BERDASARKAN WRAPPER */
    /* Hijau: Tanam */
    .fase-tanam button { background-color: #C6F6D5 !important; border-color: #48BB78 !important; }
    /* Biru: Siram */
    .fase-siram button { background-color: #BEE3F8 !important; border-color: #4299E1 !important; }
    /* Kuning: Pupuk / Penyiangan (INI RANGE) */
    .fase-pupuk button { background-color: #FEF3C7 !important; border-color: #F6E05E !important; }
    /* Merah: Panen */
    .fase-panen button { background-color: #FED7D7 !important; border-color: #F56565 !important; }

    /* Legend Box */
    .legend-card {
        padding: 15px; border-radius: 10px; text-align: center; 
        font-weight: bold; border: 1px solid #CBD5E0;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# 3. SIDEBAR & LOGIC
# =========================
st.sidebar.title("⚙️ Pengaturan")
kec_list = sorted(data["kecamatan"].unique())
sel_kecamatan = st.sidebar.selectbox("Pilih Kecamatan", kec_list)
tgl_tanam = st.sidebar.date_input("Tanggal Tanam", value=date(2026, 3, 1))

kec_id = encoder.transform([sel_kecamatan])[0]
df_kec = data[data["kecamatan"] == sel_kecamatan].copy().sort_values("tanggal")
rain_last270 = df_kec["rain_mm"].values[-270:]
forecast_30 = recursive_forecast(model=model, scaler=scaler, rain_last270=rain_last270, kec_id=kec_id, days=31)

# =========================
# 4. MAIN LAYOUT
# =========================
col1, col2 = st.columns([3, 1])

with col1:
    # --- NAVIGASI BULAN ---
    n1, n2, n3 = st.columns([1, 2, 1])
    with n1:
        if st.button("❮ Sebelumnya", key="prev_btn"):
            st.session_state.view_date -= relativedelta(months=1); st.rerun()
    with n2:
        cv = st.session_state.view_date
        st.markdown(f"<h2 style='text-align:center;'>{calendar.month_name[cv.month]} {cv.year}</h2>", unsafe_allow_html=True)
    with n3:
        if st.button("Selanjutnya ❯", key="next_btn"):
            st.session_state.view_date += relativedelta(months=1); st.rerun()

    # --- LEGENDA & EDUKASI (Solusi buat user non-teknis) ---
    st.write("---")
    l1, l2, l3, l4 = st.columns(4)
    l1.markdown('<div class="legend-card" style="background-color:#C6F6D5">🌱 Tanam</div>', unsafe_allow_html=True)
    l2.markdown('<div class="legend-card" style="background-color:#BEE3F8">💧 Siram</div>', unsafe_allow_html=True)
    l3.markdown('<div class="legend-card" style="background-color:#FEF3C7">🧪 Rentang Pupuk</div>', unsafe_allow_html=True)
    l4.markdown('<div class="legend-card" style="background-color:#FED7D7">🚜 Panen</div>', unsafe_allow_html=True)
    
    st.info("💡 **Tips untuk Petani:** Hari yang berwarna **Kuning** adalah **rentang waktu** yang cocok untuk pemupukan. Anda tidak harus memupuk setiap hari, cukup pilih salah satu hari yang cuacanya mendukung di dalam rentang tersebut.")

    # --- GRID KALENDER ---
    cal_matrix = calendar.monthcalendar(cv.year, cv.month)
    cols = st.columns(7)
    for i, d in enumerate(["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]):
        cols[i].markdown(f"<p style='text-align:center; font-weight:bold; color:#718096;'>{d}</p>", unsafe_allow_html=True)

    for week in cal_matrix:
        w_cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                w_cols[i].write("")
            else:
                curr_dt = date(cv.year, cv.month, day)
                
                # Perhitungan HST (Hari Setelah Tanam)
                # Formula: $HST = t_{current} - t_{planting}$
                hst = (curr_dt - tgl_tanam).days
                
                idx = min(max(0, day - 1), len(forecast_30) - 1)
                hujan_val = forecast_30[idx]
                
                # Ambil rekomendasi
                rekom_full = rbs_singkong_final(hujan_val, hst)
                label_txt = label_singkat(rekom_full).upper()
                
                # Tentukan Fase untuk Class CSS
                phase_class = "fase-default"
                if "TANAM" in label_txt: phase_class = "fase-tanam"
                elif "SIRAM" in label_txt: phase_class = "fase-siram"
                elif "PUPUK" in label_txt or "SIANG" in label_txt: phase_class = "fase-pupuk"
                elif "PANEN" in label_txt: phase_class = "fase-panen"

                # RENDER BUTTON DENGAN WRAPPER
                with w_cols[i]:
                    st.markdown(f'<div class="{phase_class}">', unsafe_allow_html=True)
                    if st.button(f"{day}\n{label_txt}", key=f"d_{cv.month}_{day}"):
                        st.session_state.selected_day = day
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# 5. DETAIL PANEL
# =========================
with col2:
    st.markdown("### 📋 Detail Hari")
    sd = st.session_state.selected_day
    try: active_dt = date(cv.year, cv.month, sd)
    except: active_dt = date(cv.year, cv.month, 1)

    hst_active = (active_dt - tgl_tanam).days
    idx_a = min(max(0, sd - 1), len(forecast_30) - 1)
    h_a = forecast_30[idx_a]
    rekom_d = rbs_singkong_final(h_a, hst_active)

    st.markdown(f"""
    <div style="background-color:#EDF2F7; padding:15px; border-radius:10px;">
        <b>Tanggal:</b> {active_dt.strftime('%d %B %Y')}<br>
        <b>Umur Tanaman:</b> {hst_active} Hari<br>
        <b>Prediksi Hujan:</b> {h_a:.2f} mm
    </div>
    """, unsafe_allow_html=True)

    st.success(f"**Saran Tindakan:**\n\n{rekom_d}")
    st.divider()
    st.line_chart(forecast_30)
