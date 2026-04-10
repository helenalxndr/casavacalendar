import streamlit as st
import pandas as pd
import numpy as np
import calendar
from datetime import date
from dateutil.relativedelta import relativedelta

# Import modular
from utils.loader import load_all
from utils.forecast import recursive_forecast
from utils.rbs import rbs_singkong_final
from utils.calendar_logic import get_forecast_index, get_hst, get_color
from utils.ui_helpers import render_day_button

st.set_page_config(layout="wide", page_title="Dashboard Tanam Singkong")
st.markdown("""
<style>

/* NAV BUTTON ONLY (prev & next) */
button[data-testid="baseButton-secondary"][key="prev_btn"],
button[data-testid="baseButton-secondary"][key="next_btn"] {
    background-color: white !important;
    color: #111827 !important;
    border: 1px solid #d1d5db !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
}

/* hover nav only */
button[data-testid="baseButton-secondary"][key="prev_btn"]:hover,
button[data-testid="baseButton-secondary"][key="next_btn"]:hover {
    background-color: #f3f4f6 !important;
}

</style>
""", unsafe_allow_html=True)

# =========================
# 1. LOAD DATA
# =========================
try:
    model, encoder, scaler, data = load_all()
    data["tanggal"] = pd.to_datetime(data["tanggal"])
except Exception as e:
    st.error(f"Gagal memuat resource: {e}")
    st.stop()

# =========================
# 2. SESSION STATE
# =========================
if "view_date" not in st.session_state:
    st.session_state.view_date = date.today().replace(day=1)

if "selected_day" not in st.session_state:
    st.session_state.selected_day = date.today().day

# =========================
# 3. SIDEBAR
# =========================
st.sidebar.title("⚙️ Pengaturan")

kec_list = sorted(data["kecamatan"].unique())
sel_kecamatan = st.sidebar.selectbox("Pilih Kecamatan", kec_list)

tgl_tanam = st.sidebar.date_input(
    "Tanggal Tanam",
    value=date.today()
)

# Encode kecamatan
try:
    kec_id = encoder.transform([sel_kecamatan])[0]
except:
    st.error("Kecamatan tidak dikenali oleh model")
    st.stop()

# Filter data kecamatan
df_kec = data[data["kecamatan"] == sel_kecamatan].copy().sort_values("tanggal")

if len(df_kec) < 270:
    st.error("Data tidak cukup (minimal 270 hari)")
    st.stop()

rain_last270 = df_kec["rain_mm"].values[-270:]

# Forecast
forecast_30 = recursive_forecast(
    model=model,
    scaler=scaler,
    rain_last270=rain_last270,
    kec_id=kec_id,
    days=31
)

start_pred_date = df_kec["tanggal"].max().date()

# =========================
# 4. LAYOUT
# =========================
col1, col2 = st.columns([3, 1])

# =========================
# 5. KALENDER
# =========================
with col1:

    # Navigasi bulan
    n1, n2, n3 = st.columns([1, 2, 1])

    with n1:
        if st.button("❮", key="prev_btn", use_container_width=True):
            st.session_state.view_date -= relativedelta(months=1)
            st.rerun()

    with n2:
        cv = st.session_state.view_date
        st.markdown(
            f"<h3 style='text-align:center'>{calendar.month_name[cv.month]} {cv.year}</h3>",
            unsafe_allow_html=True
        )

    with n3:
        if st.button("❯", key="next_btn", use_container_width=True):
            st.session_state.view_date += relativedelta(months=1)
            st.rerun()

    # Header hari
    hari = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
    cols = st.columns(7)
    for i, h in enumerate(hari):
        cols[i].markdown(f"<center><b>{h}</b></center>", unsafe_allow_html=True)

    # Grid kalender
    cal_matrix = calendar.monthcalendar(cv.year, cv.month)

    for week in cal_matrix:
        w_cols = st.columns(7)

        for i, day in enumerate(week):
            if day == 0:
                w_cols[i].write("")
            else:
                curr_dt = date(cv.year, cv.month, day)

                # HST & forecast index
                hst = get_hst(curr_dt, tgl_tanam)
                idx = get_forecast_index(curr_dt, start_pred_date, len(forecast_30))

                hujan_val = forecast_30[idx]

                # RBS
                fase, detail, kode = rbs_singkong_final(hujan_val, hst)
                
                rekom_full = detail
                label_txt = fase

                # Warna aktivitas
                color = get_color(kode)

                # Render tombol
                if render_day_button(
                    w_cols[i],
                    day,
                    label_txt,
                    color,
                    key=f"{cv.month}_{day}",
                    selected=(day == st.session_state.selected_day)
                ):
                    st.session_state.selected_day = day
                    st.rerun()

# =========================
# 6. DETAIL PANEL
# =========================
with col2:

    st.markdown("### 📋 Detail Hari")

    last_day = calendar.monthrange(cv.year, cv.month)[1]
    sd = min(st.session_state.selected_day, last_day)

    active_dt = date(cv.year, cv.month, sd)

    hst = get_hst(active_dt, tgl_tanam)
    idx = get_forecast_index(active_dt, start_pred_date, len(forecast_30))
    hujan_val = forecast_30[idx]

    fase, detail, kode= rbs_singkong_final(hujan_val, hst)

    st.info(
        f"**Tanggal:** {active_dt.strftime('%d %B %Y')}\n\n"
        f"**HST:** {hst} hari\n\n"
        f"**Prediksi Hujan:** {hujan_val:.2f} mm"
    )

    st.success(f"**Rekomendasi Fase:**\n{fase}\n{detail}")

    st.caption("⚠️ Aktivitas menunjukkan rentang waktu optimal, bukan harus dilakukan setiap hari.")

    st.divider()

    st.line_chart(forecast_30)

    # =========================
    # LEGENDA WARNA
    # =========================
    st.markdown("### 🎨 Keterangan Warna")

    st.markdown("""
    🟢 Penanaman  
    🔵 Penyiraman  
    🟡 Pemupukan  
    🟣 Penyiangan  
    🔴 Pemanenan  
    ⚪ Pemantauan  
    """)
