import streamlit as st
import pandas as pd
import numpy as np
import calendar
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# --- 1. IMPORT UTILS ---
try:
    from utils.loader import load_all
    from utils.forecast import recursive_forecast
    from utils.rbs import rbs_singkong_final, label_singkat
except Exception as e:
    st.error(f"Error loading utils: {e}")
    st.stop()

st.set_page_config(layout="wide", page_title="Dashboard Tanam Singkong")

# --- 2. JURUS PAMUNGKAS CSS (Inject Langsung) ---
# Menggunakan selector [data-testid] agar warna "tembus" ke tombol
st.markdown("""
    <style>
    /* Styling Dasar Button */
    div.stButton > button {
        height: 105px !important;
        width: 100% !important;
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
        background-color: white !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.2s ease !important;
    }

    /* PAKSA WARNA BERDASARKAN FASE */
    [data-testid="stHorizontalBlock"] .fase-tanam button { background-color: #C6F6D5 !important; border: 2px solid #48BB78 !important; }
    [data-testid="stHorizontalBlock"] .fase-siram button { background-color: #BEE3F8 !important; border: 2px solid #4299E1 !important; }
    [data-testid="stHorizontalBlock"] .fase-pupuk button { background-color: #FEF3C7 !important; border: 2px solid #F6E05E !important; }
    [data-testid="stHorizontalBlock"] .fase-panen button { background-color: #FED7D7 !important; border: 2px solid #F56565 !important; }

    /* Atur Teks dalam Button */
    div.stButton button p { font-size: 22px !important; font-weight: 800 !important; color: #1a202c !important; margin: 0 !important; }
    div.stButton button div { font-size: 10px !important; font-weight: 700 !important; color: #4a5568 !important; text-transform: uppercase !important; }

    /* Hover Effect */
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# =========================
# 3. LOAD DATA & SESSION STATE
# =========================
try:
    model, encoder, scaler, data = load_all()
    data["tanggal"] = pd.to_datetime(data["tanggal"])
except Exception as e:
    st.error(f"Gagal memuat resource: {e}")
    st.stop()

if "view_date" not in st.session_state:
    st.session_state.view_date = date(2026, 4, 1)

if "selected_day" not in st.session_state:
    st.session_state.selected_day = 1

# =========================
# 4. SIDEBAR LOGIC
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
# 5. MAIN DASHBOARD
# =========================
col1, col2 = st.columns([3, 1])

with col1:
    # --- NAVIGASI BULAN ---
    n1, n2, n3 = st.columns([1, 2, 1])
    with n1:
        if st.button("❮ Sebelumnya", key="prev"):
            st.session_state.view_date -= relativedelta(months=1)
            st.rerun()
    with n2:
        cv = st.session_state.view_date
        st.markdown(f"<h2 style='text-align:center;'>{calendar.month_name[cv.month]} {cv.year}</h2>", unsafe_allow_html=True)
    with n3:
        if st.button("Selanjutnya ❯", key="next"):
            st.session_state.view_date += relativedelta(months=1)
            st.rerun()

    # --- LEGENDA ---
    st.write("")
    l1, l2, l3, l4 = st.columns(4)
    l1.markdown('<div style="background-color:#C6F6D5; padding:10px; border-radius:8px; text-align:center; font-size:12px; font-weight:bold; border:1px solid #48BB78;">🌱 Tanam</div>', unsafe_allow_html=True)
    l2.markdown('<div style="background-color:#BEE3F8; padding:10px; border-radius:8px; text-align:center; font-size:12px; font-weight:bold; border:1px solid #4299E1;">💧 Siram</div>', unsafe_allow_html=True)
    l3.markdown('<div style="background-color:#FEF3C7; padding:10px; border-radius:8px; text-align:center; font-size:12px; font-weight:bold; border:1px solid #F6E05E;">🧪 Jendela Pupuk</div>', unsafe_allow_html=True)
    l4.markdown('<div style="background-color:#FED7D7; padding:10px; border-radius:8px; text-align:center; font-size:12px; font-weight:bold; border:1px solid #F56565;">🚜 Panen</div>', unsafe_allow_html=True)
    st.caption("ℹ️ **Catatan:** Warna kuning (Jendela Pupuk) adalah rentang waktu terbaik. Anda cukup pilih salah satu hari di rentang tersebut.")

    # --- GRID KALENDER ---
    h_cols = st.columns(7)
    days_abbr = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
    for i, d in enumerate(days_abbr):
        h_cols[i].markdown(f"<p style='text-align:center; color:gray; font-weight:bold;'>{d}</p>", unsafe_allow_html=True)

    cal_matrix = calendar.monthcalendar(cv.year, cv.month)
    for week in cal_matrix:
        w_cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                w_cols[i].write("")
            else:
                curr_dt = date(cv.year, cv.month, day)
                hst = (curr_dt - tgl_tanam).days
                
                # Get Recommendation Logic
                idx = min(max(0, day - 1), len(forecast_30) - 1)
                hujan_val = forecast_30[idx]
                label_txt = label_singkat(rbs_singkong_final(hujan_val, hst)).upper()
                
                # Mapping CSS Class
                phase_class = "fase-default"
                if "TANAM" in label_txt: phase_class = "fase-tanam"
                elif "SIRAM" in label_txt: phase_class = "fase-siram"
                elif "PUPUK" in label_txt or "SIANG" in label_txt: phase_class = "fase-pupuk"
                elif "PANEN" in label_txt: phase_class = "fase-panen"

                with w_cols[i]:
                    # BUNGKUS DENGAN DIV UNTUK CSS
                    st.markdown(f'<div class="{phase_class}">', unsafe_allow_html=True)
                    if st.button(f"{day}\n{label_txt}", key=f"btn_{cv.month}_{day}"):
                        st.session_state.selected_day = day
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# 6. DETAIL PANEL
# =========================
with col2:
    st.markdown("### 📋 Detail Hari")
    sd = st.session_state.selected_day
    try:
        active_dt = date(cv.year, cv.month, sd)
    except:
        active_dt = date(cv.year, cv.month, 1)

    hst_active = (active_dt - tgl_tanam).days
    idx_a = min(max(0, sd - 1), len(forecast_30) - 1)
    h_a = forecast_30[idx_a]
    rekom_d = rbs_singkong_final(h_a, hst_active)

    st.info(f"**{active_dt.strftime('%d %B %Y')}**\n\nHST: {hst_active} Hari\n\nPrediksi Hujan: {h_a:.2f} mm")
    st.success(f"**Rekomendasi:**\n\n{rekom_d}")
    st.divider()
    st.line_chart(forecast_30)
