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

# =========================
# 2. LOAD DATA & SESSION STATE
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
# 3. SIDEBAR LOGIC
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
# 4. PRE-CALCULATE COLORS (Kunci Perbaikan)
# =========================
# Kita buat list CSS dinamis berdasarkan label agar tidak merusak struktur HTML Streamlit
cv = st.session_state.view_date
cal_matrix = calendar.monthcalendar(cv.year, cv.month)
dynamic_styles = []

for week in cal_matrix:
    for day in week:
        if day != 0:
            curr_dt = date(cv.year, cv.month, day)
            hst = (curr_dt - tgl_tanam).days
            idx = min(max(0, day - 1), len(forecast_30) - 1)
            hujan_val = forecast_30[idx]
            label = label_singkat(rbs_singkong_final(hujan_val, hst)).upper()
            
            # Tentukan warna
            bg_color = "white"
            border_color = "#e2e8f0"
            if "TANAM" in label: bg_color, border_color = "#C6F6D5", "#48BB78"
            elif "SIRAM" in label: bg_color, border_color = "#BEE3F8", "#4299E1"
            elif "PUPUK" in label or "SIANG" in label: bg_color, border_color = "#FEF3C7", "#F6E05E"
            elif "PANEN" in label: bg_color, border_color = "#FED7D7", "#F56565"
            
            # Buat selector spesifik untuk tombol ini berdasarkan KEY-nya
            # Streamlit menggunakan key sebagai bagian dari ID DOM
            dynamic_styles.append(f'button[key="btn_{cv.month}_{day}"] {{ background-color: {bg_color} !important; border: 2px solid {border_color} !important; }}')

# Inject CSS
st.markdown(f"""
    <style>
    div.stButton > button {{
        height: 105px !important; width: 100% !important;
        border-radius: 12px !important; display: flex !important;
        flex-direction: column !important; align-items: center !important;
        justify-content: center !important;
    }}
    div.stButton button p {{ font-size: 20px !important; font-weight: 800 !important; color: #1a202c !important; }}
    div.stButton button div {{ font-size: 10px !important; font-weight: 700 !important; color: #4a5568 !important; }}
    {" ".join(dynamic_styles)}
    </style>
    """, unsafe_allow_html=True)

# =========================
# 5. MAIN DASHBOARD
# =========================
col1, col2 = st.columns([3, 1])

with col1:
    # Navigasi
    n1, n2, n3 = st.columns([1, 2, 1])
    with n1:
        if st.button("❮ Sebelumnya", key="prev_nav"):
            st.session_state.view_date -= relativedelta(months=1); st.rerun()
    with n2:
        st.markdown(f"<h2 style='text-align:center;'>{calendar.month_name[cv.month]} {cv.year}</h2>", unsafe_allow_html=True)
    with n3:
        if st.button("Selanjutnya ❯", key="next_nav"):
            st.session_state.view_date += relativedelta(months=1); st.rerun()

    # Legenda
    st.write("")
    l1, l2, l3, l4 = st.columns(4)
    l1.info("🌱 Tanam")
    l2.info("💧 Siram")
    l3.warning("🧪 Jendela Pupuk")
    l4.error("🚜 Panen")
    st.caption("ℹ️ **Kuning** adalah rentang waktu. Pilih salah satu hari saja.")

    # Grid Kalender
    st.write("---")
    h_cols = st.columns(7)
    for i, d in enumerate(["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]):
        h_cols[i].markdown(f"<p style='text-align:center; font-weight:bold;'>{d}</p>", unsafe_allow_html=True)

    for week in cal_matrix:
        w_cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                w_cols[i].write("")
            else:
                curr_dt = date(cv.year, cv.month, day)
                hst = (curr_dt - tgl_tanam).days
                idx = min(max(0, day - 1), len(forecast_30) - 1)
                label_txt = label_singkat(rbs_singkong_final(forecast_30[idx], hst)).upper()

                # JANGAN PAKAI WRAPPER DIV LAGI
                with w_cols[i]:
                    if st.button(f"{day}\n{label_txt}", key=f"btn_{cv.month}_{day}", use_container_width=True):
                        st.session_state.selected_day = day
                        st.rerun()

# =========================
# 6. DETAIL PANEL (Panel Rekomendasi)
# =========================
with col2:
    st.markdown("### 📋 Detail Hari")
    sd = st.session_state.selected_day
    active_dt = date(cv.year, cv.month, sd)
    hst_active = (active_dt - tgl_tanam).days
    idx_a = min(max(0, sd - 1), len(forecast_30) - 1)
    h_a = forecast_30[idx_a]
    rekom_d = rbs_singkong_final(h_a, hst_active)

    st.info(f"**{active_dt.strftime('%d %B %Y')}**\nHST: {hst_active}\nHujan: {h_a:.2f} mm")
    st.success(f"**Rekomendasi:**\n\n{rekom_d}")
    st.line_chart(forecast_30)
