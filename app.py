import streamlit as st
import pandas as pd
import numpy as np
import calendar
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from utils.loader import load_all
from utils.forecast import recursive_forecast

st.set_page_config(layout="wide", page_title="Dashboard Kalender Tanam")

# =========================
# 1. LOAD DATA & INITIAL STATE
# =========================
model, encoder, scaler, data = load_all()
data["tanggal"] = pd.to_datetime(data["tanggal"])

# Inisialisasi State agar tidak hilang saat rerun
if "view_date" not in st.session_state:
    st.session_state.view_date = date(2026, 3, 1) # Default ke Maret 2026 sesuai gambar Anda

if "selected_day" not in st.session_state:
    st.session_state.selected_day = 1

# =========================
# 2. SIDEBAR & LOGIC
# =========================
st.sidebar.title("⚙ Pengaturan")
kecamatan_list = sorted(data["kecamatan"].unique())
selected_kecamatan = st.sidebar.selectbox("Pilih Kecamatan", kecamatan_list)
tanggal_tanam = st.sidebar.date_input("Tanggal Tanam", value=date(2026, 3, 1))

# Kalkulasi Forecast
kec_id = encoder.transform([selected_kecamatan])[0]
df_kec = data[data["kecamatan"] == selected_kecamatan].copy().sort_values("tanggal")
rain_last270 = df_kec["rain_mm"].values[-270:]
forecast_30 = recursive_forecast(model=model, scaler=scaler, rain_last270=rain_last270, kec_id=kec_id, days=30)

# =========================
# 3. CSS CUSTOM (Center Text & Square Buttons)
# =========================
st.markdown("""
<style>
    /* Paksa tombol menjadi kotak dan teks di tengah */
    div.stButton > button {
        height: 100px;
        width: 100%;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        background-color: white;
        display: flex;
        flex-direction: column;
        align-items: center !important;    /* Center Horizontal */
        justify-content: center !important; /* Center Vertical */
        text-align: center !important;
        transition: 0.2s;
    }
    
    div.stButton > button:hover {
        border-color: #2563eb;
        background-color: #f9fafb;
    }

    /* Indikator Terpilih (Border Biru) */
    div.stButton > button:focus {
        border: 2px solid #2563eb !important;
        background-color: #eff6ff !important;
    }

    /* Ukuran teks tanggal di dalam tombol */
    div.stButton > button p {
        font-size: 20px !important;
        font-weight: bold !important;
        margin: 0 !important;
    }

    /* Label status kecil di bawah angka */
    .status-text {
        font-size: 11px;
        font-weight: normal;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# 4. MAIN LAYOUT
# =========================
col1, col2 = st.columns([3, 1])

with col1:
    # --- HEADER NAVIGASI BULAN ---
    nav_left, nav_mid, nav_right = st.columns([1, 2, 1])
    
    with nav_left:
        if st.button("⬅️ Sebelumnya", key="btn_prev"):
            st.session_state.view_date -= relativedelta(months=1)
            st.rerun()
            
    with nav_mid:
        current_view = st.session_state.view_date
        nama_bulan = calendar.month_name[current_view.month]
        st.markdown(f"<h2 style='text-align:center; margin-top:-10px;'>{nama_bulan} {current_view.year}</h2>", unsafe_allow_html=True)
        
    with nav_right:
        if st.button("Selanjutnya ➡️", key="btn_next"):
            st.session_state.view_date += relativedelta(months=1)
            st.rerun()

    # --- GRID KALENDER ---
    cols_header = st.columns(7)
    for i, hari in enumerate(["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]):
        cols_header[i].markdown(f"<p style='text-align:center; font-weight:bold; color:gray;'>{hari}</p>", unsafe_allow_html=True)

    cal_matrix = calendar.monthcalendar(current_view.year, current_view.month)
    
    for week in cal_matrix:
        week_cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                week_cols[i].write("")
            else:
                # Logika HST untuk Label
                this_date = date(current_view.year, current_view.month, day)
                hst = (this_date - tanggal_tanam).days
                
                label = ""
                if 0 <= hst < 5: label = "🌱 Pantau"
                elif 5 <= hst < 90: label = "💊 Pupuk"
                elif hst >= 90: label = "🌾 Panen"

                # Render Tombol (Teks otomatis Center karena CSS di atas)
                btn_label = f"{day}\n{label}"
                if week_cols[i].button(btn_label, key=f"day_{current_view.month}_{day}", use_container_width=True):
                    st.session_state.selected_day = day
                    st.rerun()

# =========================
# 5. DETAIL PANEL (KOLOM KANAN)
# =========================
with col2:
    st.markdown("### 📋 Detail Rekomendasi")
    
    sel_day = st.session_state.selected_day
    try:
        active_date = date(current_view.year, current_view.month, sel_day)
    except:
        active_date = date(current_view.year, current_view.month, 1)

    hst_active = (active_date - tanggal_tanam).days
    
    # Prediksi Hujan (Sesuai index hari)
    idx_rain = min(max(0, active_date.day - 1), len(forecast_30) - 1)
    rain_val = forecast_30[idx_rain]

    # Card Detail
    st.info(f"""
    **Tanggal:** {active_date.strftime('%d %B %Y')}  
    **HST:** {hst_active} hari  
    **Prediksi Hujan:** {rain_val:.2f} mm
    """)

    if hst_active < 5:
        st.write("Pemantauan awal – kelembapan cukup untuk pertumbuhan awal.")
    elif hst_active < 90:
        st.success("Fase pemupukan – kondisi mendukung.")
    else:
        st.warning("Mendekati panen – perhatikan kondisi lahan.")

    st.divider()
    st.line_chart(forecast_30)
