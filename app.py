import streamlit as st
import pandas as pd
import numpy as np
import calendar
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# Import dari folder utils (Pastikan modul ini tersedia di folder Anda)
try:
    from utils.loader import load_all
    from utils.forecast import recursive_forecast
    from utils.rbs import rbs_singkong_final, label_singkat
except ImportWarning:
    st.error("Pastikan folder 'utils' tersedia.")

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
    st.session_state.view_date = date(2026, 4, 1) # Menyesuaikan screenshot Anda

if "selected_day" not in st.session_state:
    st.session_state.selected_day = 10

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
forecast_30 = recursive_forecast(model=model, scaler=scaler, rain_last270=rain_last270, kec_id=kec_id, days=31)

# =========================
# 3. CSS "BULLETPROOF" (Lebih Kuat)
# =========================
# Kita gunakan teknik penargetan data-testid jika class standar gagal
st.markdown("""
<style>
    /* 1. Reset Dasar Tombol */
    div.stButton > button {
        height: 110px !important;
        width: 100% !important;
        border-radius: 12px !important;
        border: 1px solid #e5e7eb !important;
        background-color: white !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.3s ease !important;
    }

    /* 2. Ukuran Font */
    div.stButton > button p { font-size: 22px !important; font-weight: 800 !important; color: #111827 !important; }
    div.stButton > button div { font-size: 10px !important; font-weight: 700 !important; color: #374151 !important; }

    /* 3. Definisi Warna Berdasarkan Class */
    /* Hijau: Tanam */
    .tanam-box button { background-color: #d1fae5 !important; border-color: #10b981 !important; }
    /* Biru: Siram */
    .siram-box button { background-color: #dbeafe !important; border-color: #3b82f6 !important; }
    /* Kuning: Pupuk (Rentang Waktu) */
    .pupuk-box button { background-color: #fef3c7 !important; border-color: #f59e0b !important; }
    /* Merah: Panen */
    .panen-box button { background-color: #fee2e2 !important; border-color: #ef4444 !important; }

    /* Legend Styling */
    .legend-container {
        display: flex; gap: 10px; margin-bottom: 20px; justify-content: center;
    }
    .legend-item {
        padding: 10px 15px; border-radius: 8px; font-size: 13px; font-weight: bold; border: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# 4. MAIN LAYOUT
# =========================
col1, col2 = st.columns([3, 1])

with col1:
    # --- NAVIGASI ---
    n1, n2, n3 = st.columns([1, 2, 1])
    with n1:
        if st.button("❮ Sebelumnya", key="prev_btn", use_container_width=True):
            st.session_state.view_date -= relativedelta(months=1); st.rerun()
    with n2:
        cv = st.session_state.view_date
        st.markdown(f"<h2 style='text-align:center; margin:0;'>{calendar.month_name[cv.month]} {cv.year}</h2>", unsafe_allow_html=True)
    with n3:
        if st.button("Selanjutnya ❯", key="next_btn", use_container_width=True):
            st.session_state.view_date += relativedelta(months=1); st.rerun()

    # --- LEGEND (Untuk User Non-Teknis) ---
    st.markdown("""
    <div class="legend-container">
        <div class="legend-item" style="background-color: #d1fae5;">🌱 Tanam</div>
        <div class="legend-item" style="background-color: #dbeafe;">💧 Siram</div>
        <div class="legend-item" style="background-color: #fef3c7;">⏳ Rentang Pemupukan</div>
        <div class="legend-item" style="background-color: #fee2e2;">🚜 Panen</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 **Petunjuk:** Warna **Kuning (Rentang Pemupukan)** berarti Anda bisa memilih salah satu hari di rentang tersebut. Tidak perlu memupuk setiap hari.")

    # --- GRID KALENDER ---
    cal_matrix = calendar.monthcalendar(cv.year, cv.month)
    cols = st.columns(7)
    days_abbr = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
    for i, d in enumerate(days_abbr):
        cols[i].markdown(f"<p style='text-align:center; font-weight:bold; color:#6b7280;'>{d}</p>", unsafe_allow_html=True)

    for week in cal_matrix:
        w_cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                w_cols[i].write("")
            else:
                curr_dt = date(cv.year, cv.month, day)
                hst = (curr_dt - tgl_tanam).days
                idx = min(max(0, day - 1), len(forecast_30) - 1)
                hujan_val = forecast_30[idx]
                
                # Logika Rekomendasi
                rekom_full = rbs_singkong_final(hujan_val, hst)
                label_txt = label_singkat(rekom_full).upper()
                
                # Tentukan Class Warna
                css_class = ""
                if "TANAM" in label_txt: css_class = "tanam-box"
                elif "SIRAM" in label_txt: css_class = "siram-box"
                elif "PUPUK" in label_txt or "SIANG" in label_txt: css_class = "pupuk-box"
                elif "PANEN" in label_txt: css_class = "panen-box"

                # Render Tombol dengan Wrapper
                with w_cols[i]:
                    st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
                    if st.button(f"{day}\n{label_txt}", key=f"btn_{day}_{cv.month}", use_container_width=True):
                        st.session_state.selected_day = day
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# 5. DETAIL PANEL
# =========================
with col2:
    st.markdown("### 📋 Detail Hari")
    sd = st.session_state.selected_day
    active_dt = date(cv.year, cv.month, sd)
    hst_active = (active_dt - tgl_tanam).days
    idx_a = min(max(0, sd - 1), len(forecast_30) - 1)
    h_a = forecast_30[idx_a]
    rekom_d = rbs_singkong_final(h_a, hst_active)

    st.markdown(f"""
    <div style="background-color:#f9fafb; padding:15px; border-radius:10px; border:1px solid #e5e7eb;">
        <p style="margin:0; color:#6b7280;">Tanggal:</p>
        <p style="font-size:18px; font-weight:bold; margin-bottom:10px;">{active_dt.strftime('%d %B %Y')}</p>
        <p style="margin:0; color:#6b7280;">HST:</p>
        <p style="font-size:18px; font-weight:bold; margin-bottom:10px;">{hst_active} Hari</p>
        <p style="margin:0; color:#6b7280;">Prediksi Hujan:</p>
        <p style="font-size:18px; font-weight:bold;">{h_a:.2f} mm</p>
    </div>
    """, unsafe_allow_html=True)

    st.success(f"**Rekomendasi:**\n\n{rekom_d}")
    st.line_chart(forecast_30)
