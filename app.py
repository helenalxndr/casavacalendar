import streamlit as st
import pandas as pd
import numpy as np
import calendar
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# --- IMPORT UTILS (Pastikan file ini ada di folder lo) ---
try:
    from utils.loader import load_all
    from utils.forecast import recursive_forecast
    from utils.rbs import rbs_singkong_final, label_singkat
except Exception as e:
    st.error(f"Error loading utils: {e}")
    st.stop()

st.set_page_config(layout="wide", page_title="Dashboard Tanam Singkong")

# Fungsi Load CSS Eksternal
def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("File style.css tidak ditemukan!")

local_css("style.css")

# =========================
# 1. LOAD DATA & SESSION STATE
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
# 2. SIDEBAR LOGIC
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
# 3. MAIN DASHBOARD
# =========================
col1, col2 = st.columns([3, 1])

with col1:
    # Navigasi Bulan
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

    # Legenda untuk User Non-Teknis
    st.write("")
    l1, l2, l3, l4 = st.columns(4)
    l1.markdown('<div style="background-color:#C6F6D5; padding:10px; border-radius:8px; text-align:center; font-size:12px; font-weight:bold;">🌱 Tanam</div>', unsafe_allow_html=True)
    l2.markdown('<div style="background-color:#BEE3F8; padding:10px; border-radius:8px; text-align:center; font-size:12px; font-weight:bold;">💧 Siram</div>', unsafe_allow_html=True)
    l3.markdown('<div style="background-color:#FEF3C7; padding:10px; border-radius:8px; text-align:center; font-size:12px; font-weight:bold;">🧪 Jendela Pupuk</div>', unsafe_allow_html=True)
    l4.markdown('<div style="background-color:#FED7D7; padding:10px; border-radius:8px; text-align:center; font-size:12px; font-weight:bold;">🚜 Panen</div>', unsafe_allow_html=True)
    st.caption("ℹ️ **Catatan:** Warna kuning menunjukkan rentang waktu terbaik untuk pemupukan, bukan kewajiban setiap hari.")

    # Grid Kalender
    h_cols = st.columns(7)
    for i, d in enumerate(["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]):
        h_cols[i].markdown(f"<p style='text-align:center; color:gray; font-size:12px;'>{d}</p>", unsafe_allow_html=True)

    cal_matrix = calendar.monthcalendar(cv.year, cv.month)
    for week in cal_matrix:
        w_cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                w_cols[i].write("")
            else:
                curr_dt = date(cv.year, cv.month, day)
                hst = (curr_dt - tgl_tanam).days
                
                # Logic Prediksi & Label
                idx = min(max(0, day - 1), len(forecast_30) - 1)
                hujan_val = forecast_30[idx]
                label_txt = label_singkat(rbs_singkong_final(hujan_val, hst)).upper()
                
                # Penentuan Class Warna
                phase_class = "fase-default"
                if "TANAM" in label_txt: phase_class = "fase-tanam"
                elif "SIRAM" in label_txt: phase_class = "fase-siram"
                elif "PUPUK" in label_txt or "SIANG" in label_txt: phase_class = "fase-pupuk"
                elif "PANEN" in label_txt: phase_class = "fase-panen"

                with w_cols[i]:
                    # WRAPPER CSS
                    st.markdown(f'<div class="{phase_class}">', unsafe_allow_html=True)
                    if st.button(f"{day}\n{label_txt}", key=f"d_{cv.month}_{day}"):
                        st.session_state.selected_day = day
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# 4. DETAIL PANEL
# =========================
with col2:
    st.markdown("### 📋 Detail")
    sd = st.session_state.selected_day
    active_dt = date(cv.year, cv.month, sd)
    hst_active = (active_dt - tgl_tanam).days
    idx_a = min(max(0, sd - 1), len(forecast_30) - 1)
    h_a = forecast_30[idx_a]
    rekom_d = rbs_singkong_final(h_a, hst_active)

    st.info(f"**{active_dt.strftime('%d %B %Y')}**\n\nHST: {hst_active} Hari\n\nHujan: {h_a:.2f} mm")
    st.success(f"**Rekomendasi:**\n{rekom_d}")
    st.divider()
    st.line_chart(forecast_30)
