import streamlit as st
import pandas as pd
import numpy as np
import calendar
import os
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# Import dari folder utils (Asumsi fungsi sudah ada)
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
# 2. HELPER: WARNA FASE
# =========================
def get_phase_color(label):
    """Mengembalikan kode warna hex berdasarkan aktivitas"""
    label = label.upper()
    if "TANAM" in label:
        return "#C6F6D5"  # Hijau Muda
    elif "SIRAM" in label:
        return "#BEE3F8"  # Biru Muda
    elif "PUPUK" in label or "SIANG" in label:
        return "#FEEBC8"  # Oranye/Kuning Muda (Fase Perawatan/Range)
    elif "PANEN" in label:
        return "#FED7D7"  # Merah Muda
    return "white" # Default

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
# 4. CSS CUSTOM (Updated with Dynamic Support)
# =========================
st.markdown("""
<style>
    .stButton > button[key="prev_btn"], .stButton > button[key="next_btn"] {
        background-color: #f3f4f6 !important;
        border: 1px solid #d1d5db !important;
        font-weight: bold !important;
    }

    /* Base Styling for Calendar Buttons */
    div.stButton > button {
        height: 105px !important;
        width: 100% !important;
        border-radius: 10px !important;
        border: 1px solid #e5e7eb !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        padding: 5px !important;
        white-space: pre-wrap !important;
    }
    
    div.stButton > button p {
        font-size: 18px !important;
        font-weight: 800 !important;
        margin: 0 !important;
        color: #111827 !important;
    }

    div.stButton > button div {
        font-size: 9px !important;
        margin-top: 5px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        line-height: 1.1 !important;
        color: #374151 !important;
    }

    /* Legend Box Styling */
    .legend-box {
        padding: 10px;
        border-radius: 8px;
        font-size: 12px;
        margin-bottom: 5px;
        border: 1px solid #e5e7eb;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# 5. MAIN LAYOUT
# =========================
col1, col2 = st.columns([3, 1])

with col1:
    # --- NAVIGASI BULAN ---
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

    # --- LEGENDA UNTUK USER NON-TEKNIS ---
    st.write("")
    l1, l2, l3, l4 = st.columns(4)
    l1.markdown(f'<div class="legend-box" style="background-color:#C6F6D5">🌱 <b>Tanam</b></div>', unsafe_allow_html=True)
    l2.markdown(f'<div class="legend-box" style="background-color:#BEE3F8">💧 <b>Penyiraman</b></div>', unsafe_allow_html=True)
    l3.markdown(f'<div class="legend-box" style="background-color:#FEEBC8">🧪 <b>Pupuk/Siang</b><br>(Rentang Waktu)</div>', unsafe_allow_html=True)
    l4.markdown(f'<div class="legend-box" style="background-color:#FED7D7">🚜 <b>Panen</b></div>', unsafe_allow_html=True)
    
    st.caption("ℹ️ *Warna kuning/oranye menunjukkan **rentang waktu** yang cocok. Anda tidak perlu memupuk setiap hari di warna tersebut, cukup pilih salah satu hari yang paling memungkinkan.*")

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
                
                # Logika RBS & Label
                idx = min(max(0, day - 1), len(forecast_30) - 1)
                hujan_val = forecast_30[idx]
                rekom_full = rbs_singkong_final(hujan_val, hst)
                label_txt = label_singkat(rekom_full)

                # Ambil warna berdasarkan label
                bg_color = get_phase_color(label_txt)
                btn_key = f"day_{cv.month}_{day}"

                # Inject CSS spesifik untuk tombol ini agar warnanya berubah
                st.markdown(f"""
                    <style>
                    div.stButton > button[key="{btn_key}"] {{
                        background-color: {bg_color} !important;
                    }}
                    </style>
                """, unsafe_allow_html=True)

                display_btn = f"{day}\n{label_txt}"
                if w_cols[i].button(display_btn, key=btn_key, use_container_width=True):
                    st.session_state.selected_day = day
                    st.rerun()

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

    st.info(f"**Tanggal:** {active_dt.strftime('%d %B %Y')}\n\n**HST:** {hst_active} hari\n\n**Hujan:** {h_a:.2f} mm")
    st.success(f"**Rekomendasi:**\n{rekom_d}")
    st.divider()
    st.line_chart(forecast_30)
