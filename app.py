import streamlit as st
import pandas as pd
import numpy as np
import calendar
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# --- IMPORT UTILS ---
from utils.loader import load_all
from utils.forecast import recursive_forecast
from utils.rbs import rbs_singkong_final, label_singkat

st.set_page_config(layout="wide", page_title="Dashboard Tanam Singkong")

# =========================
# LOAD DATA
# =========================
try:
    model, encoder, scaler, data = load_all()
    data["tanggal"] = pd.to_datetime(data["tanggal"])
except Exception as e:
    st.error(f"Gagal memuat resource: {e}")
    st.stop()

# =========================
# SESSION
# =========================
if "view_date" not in st.session_state:
    st.session_state.view_date = date(2026, 4, 1)

if "selected_day" not in st.session_state:
    st.session_state.selected_day = 1

# =========================
# SIDEBAR
# =========================
st.sidebar.title("⚙️ Pengaturan")
kec_list = sorted(data["kecamatan"].unique())
sel_kecamatan = st.sidebar.selectbox("Pilih Kecamatan", kec_list)
tgl_tanam = st.sidebar.date_input("Tanggal Tanam", value=date(2026, 3, 1))

kec_id = encoder.transform([sel_kecamatan])[0]
df_kec = data[data["kecamatan"] == sel_kecamatan].copy().sort_values("tanggal")

rain_last270 = df_kec["rain_mm"].values[-270:]

forecast_30 = recursive_forecast(
    model=model,
    scaler=scaler,
    rain_last270=rain_last270,
    kec_id=kec_id,
    days=31
)

forecast_30 = np.clip(forecast_30, 0, 300)

# =========================
# PRE-CALCULATE WARNA
# =========================
cv = st.session_state.view_date
cal_matrix = calendar.monthcalendar(cv.year, cv.month)
dynamic_styles = []

for week in cal_matrix:
    for day in week:
        if day != 0:
            curr_dt = date(cv.year, cv.month, day)
            hst = (curr_dt - tgl_tanam).days
            idx = min(max(0, day - 1), len(forecast_30) - 1)

            label = label_singkat(
                rbs_singkong_final(forecast_30[idx], hst)
            ).upper()

            # WARNA
            bg_color = "#ffffff"
            border_color = "#e5e7eb"

            if "TANAM" in label:
                bg_color, border_color = "#bbf7d0", "#22c55e"
            elif "SIRAM" in label:
                bg_color, border_color = "#bae6fd", "#0ea5e9"
            elif "PUPUK" in label or "GULMA" in label:
                bg_color, border_color = "#fef08a", "#eab308"
            elif "PANEN" in label:
                bg_color, border_color = "#fecaca", "#ef4444"

            # CSS FIX (WORKING)
            dynamic_styles.append(f"""
            div[data-testid="stButton"]:has(button[data-testid="btn_{cv.month}_{day}"]) button {{
                background-color: {bg_color} !important;
                border: 2px solid {border_color} !important;
                color: black !important;
            }}
            """)

# =========================
# CSS GLOBAL
# =========================
st.markdown(f"""
<style>
div[data-testid="stButton"] button {{
    height: 105px !important;
    width: 100% !important;
    border-radius: 12px !important;
    font-size: 20px !important;
    font-weight: bold !important;
}}

div[data-testid="stButton"] button:hover {{
    transform: scale(1.03);
}}

{" ".join(dynamic_styles)}
</style>
""", unsafe_allow_html=True)

# =========================
# LAYOUT
# =========================
col1, col2 = st.columns([3, 1])

with col1:
    # NAVIGASI
    n1, n2, n3 = st.columns([1, 2, 1])

    with n1:
        if st.button("❮ Sebelumnya"):
            st.session_state.view_date -= relativedelta(months=1)
            st.rerun()

    with n2:
        st.markdown(
            f"<h2 style='text-align:center'>{calendar.month_name[cv.month]} {cv.year}</h2>",
            unsafe_allow_html=True
        )

    with n3:
        if st.button("Selanjutnya ❯"):
            st.session_state.view_date += relativedelta(months=1)
            st.rerun()

    # LEGENDA
    st.write("")
    l1, l2, l3, l4 = st.columns(4)
    l1.success("🌱 Tanam")
    l2.info("💧 Siram")
    l3.warning("🧪 Jendela Pupuk")
    l4.error("🚜 Panen")
    st.caption("Warna menunjukkan rentang waktu optimal (bukan aktivitas harian).")

    st.write("---")

    # HEADER HARI
    h_cols = st.columns(7)
    for i, d in enumerate(["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]):
        h_cols[i].markdown(f"<p style='text-align:center; font-weight:bold'>{d}</p>", unsafe_allow_html=True)

    # GRID
    for week in cal_matrix:
        w_cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                w_cols[i].write("")
            else:
                with w_cols[i]:
                    if st.button(str(day), key=f"btn_{cv.month}_{day}", use_container_width=True):
                        st.session_state.selected_day = day
                        st.rerun()

# =========================
# DETAIL PANEL
# =========================
with col2:
    st.markdown("### 📋 Detail Hari")

    sd = st.session_state.selected_day
    active_dt = date(cv.year, cv.month, sd)

    hst_active = (active_dt - tgl_tanam).days
    idx = min(max(0, sd - 1), len(forecast_30) - 1)
    hujan = forecast_30[idx]

    rekom = rbs_singkong_final(hujan, hst_active)

    st.info(f"""
    **Tanggal:** {active_dt.strftime('%d %B %Y')}

    **HST:** {hst_active} hari  
    **Curah Hujan:** {hujan:.2f} mm  
    """)

    st.success(rekom)

    st.line_chart(forecast_30)
