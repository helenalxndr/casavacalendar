import streamlit as st
import pandas as pd
import numpy as np
import calendar
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# Import dari folder utils (Pastikan file ini ada)
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
    st.session_state.view_date = date(2026, 4, 1) # Set ke April sesuai screenshot Anda

if "selected_day" not in st.session_state:
    st.session_state.selected_day = 10

# =========================
# 2. HELPER: WARNA FASE
# =========================
def get_phase_class(label):
    """Menentukan nama class CSS berdasarkan label"""
    label = label.upper()
    if "TANAM" in label: return "phase-tanam"
    if "SIRAM" in label: return "phase-siram"
    if "PUPUK" in label: return "phase-pupuk"
    if "SIANG" in label: return "phase-siang"
    if "PANEN" in label: return "phase-panen"
    return "phase-default"

# =========================
# 3. SIDEBAR
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
# 4. CSS CUSTOM (FIXED SELECTOR)
# =========================
st.markdown("""
<style>
    /* Styling Dasar Tombol Kalender */
    div.stButton > button {
        height: 100px !important;
        width: 100% !important;
        border-radius: 12px !important;
        border: 1px solid #e5e7eb !important;
        background-color: white !important;
        transition: all 0.2s ease;
    }

    /* Ukuran Font Tanggal & Label */
    div.stButton > button p { font-size: 20px !important; font-weight: 800 !important; margin: 0; }
    div.stButton > button div { font-size: 10px !important; font-weight: 700 !important; color: #4b5563 !important; }

    /* PEWARNAAN BERDASARKAN CLASS WRAPPER */
    .phase-tanam button { background-color: #C6F6D5 !important; border-color: #9AE6B4 !important; }
    .phase-siram button { background-color: #BEE3F8 !important; border-color: #90CDF4 !important; }
    .phase-pupuk button { background-color: #FEF3C7 !important; border-color: #FDE68A !important; } /* Kuning Lembut */
    .phase-siang button { background-color: #E9D8FD !important; border-color: #D6BCFA !important; }
    .phase-panen button { background-color: #FED7D7 !important; border-color: #FEB2B2 !important; }

    /* Hover effect */
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }

    /* Legend Box */
    .legend-card {
        padding: 12px; border-radius: 10px; text-align: center; font-size: 13px; font-weight: 600;
        border: 1px solid #e5e7eb; margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# 5. MAIN LAYOUT
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

    # --- LEGENDA (Penting untuk User Non-Teknis) ---
    st.write("")
    l1, l2, l3, l4 = st.columns(4)
    l1.markdown('<div class="legend-card" style="background-color:#C6F6D5">🌱 Penanaman</div>', unsafe_allow_html=True)
    l2.markdown('<div class="legend-card" style="background-color:#BEE3F8">💧 Penyiraman</div>', unsafe_allow_html=True)
    l3.markdown('<div class="legend-card" style="background-color:#FEF3C7">💊 Pupuk (Rentang Waktu)</div>', unsafe_allow_html=True)
    l4.markdown('<div class="legend-card" style="background-color:#FED7D7">🚜 Pemanenan</div>', unsafe_allow_html=True)
    
    st.warning("💡 **Tips:** Warna kuning menunjukkan **rentang waktu**. Pilih salah satu hari di dalam rentang tersebut untuk memupuk (tidak perlu setiap hari).")

    # Grid Kalender
    h_cols = st.columns(7)
    for i, h in enumerate(["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]):
        h_cols[i].markdown(f"<p style='text-align:center; color:gray; font-size:12px;'>{h}</p>", unsafe_allow_html=True)

    cal_matrix = calendar.monthcalendar(cv.year, cv.month)
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
                
                rekom_full = rbs_singkong_final(hujan_val, hst)
                label_txt = label_singkat(rekom_full)
                phase_class = get_phase_class(label_txt)

                # PEMBUNGKUS TOMBOL (Ini kunci agar CSS bekerja)
                with w_cols[i]:
                    st.markdown(f'<div class="{phase_class}">', unsafe_allow_html=True)
                    if st.button(f"{day}\n{label_txt}", key=f"d_{cv.month}_{day}", use_container_width=True):
                        st.session_state.selected_day = day
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# 6. DETAIL PANEL
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

    st.info(f"**Tanggal:** {active_dt.strftime('%d %B %Y')}\n\n**HST:** {hst_active} hari")
    
    # Penjelasan Khusus Pupuk di Detail
    if "PUPUK" in rekom_d.upper():
        st.success(f"**Rekomendasi:**\n{rekom_d}\n\n*Pilih hari dengan ramalan hujan rendah di antara rentang warna kuning.*")
    else:
        st.success(f"**Rekomendasi:**\n{rekom_d}")

    st.divider()
    st.caption("Prediksi Curah Hujan (30 Hari ke Depan)")
    st.line_chart(forecast_30)
