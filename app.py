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

if "view_date" not in st.session_state:
    st.session_state.view_date = date(2026, 3, 1)

if "selected_day" not in st.session_state:
    st.session_state.selected_day = 1

# =========================
# 2. SIDEBAR & LOGIC
# =========================
st.sidebar.title("⚙ Pengaturan")
kecamatan_list = sorted(data["kecamatan"].unique())
selected_kecamatan = st.sidebar.selectbox("Pilih Kecamatan", kecamatan_list)
tanggal_tanam = st.sidebar.date_input("Tanggal Tanam", value=date(2026, 3, 1))

kec_id = encoder.transform([selected_kecamatan])[0]
df_kec = data[data["kecamatan"] == selected_kecamatan].copy().sort_values("tanggal")
rain_last270 = df_kec["rain_mm"].values[-270:]
forecast_30 = recursive_forecast(model=model, scaler=scaler, rain_last270=rain_last270, kec_id=kec_id, days=30)

# =========================
# 3. CSS CUSTOM (Center & Block Labels)
# =========================
st.markdown("""
<style>
    /* Styling Tombol Kalender */
    div.stButton > button {
        height: 110px;
        width: 100%;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        background-color: white;
        display: flex;
        flex-direction: column;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        transition: 0.2s;
        padding: 5px !important;
    }
    
    div.stButton > button:hover {
        border-color: #2563eb;
        background-color: #f9fafb;
    }

    div.stButton > button:focus {
        border: 2px solid #2563eb !important;
        background-color: #eff6ff !important;
    }

    /* Ukuran Angka Tanggal */
    div.stButton > button p {
        font-size: 22px !important;
        font-weight: bold !important;
        margin: 0 !important;
        line-height: 1.2 !important;
    }

    /* Container untuk Label Blok Warna di dalam Button */
    .status-badge {
        font-size: 10px;
        font-weight: bold;
        text-transform: uppercase;
        padding: 2px 8px;
        border-radius: 6px;
        margin-top: 8px;
        display: inline-block;
    }
    .bg-pantau { background-color: #e0f2fe; color: #0369a1; }
    .bg-pupuk { background-color: #ede9fe; color: #6d28d9; }
    .bg-panen { background-color: #dcfce7; color: #166534; }
</style>
""", unsafe_allow_html=True)

# =========================
# 4. MAIN LAYOUT
# =========================
col1, col2 = st.columns([3, 1])

with col1:
    # --- NAVIGASI BULAN ---
    nav_left, nav_mid, nav_right = st.columns([1, 2, 1])
    with nav_left:
        if st.button("⬅️ Prev", key="btn_prev"):
            st.session_state.view_date -= relativedelta(months=1)
            st.rerun()
    with nav_mid:
        current_view = st.session_state.view_date
        st.markdown(f"<h2 style='text-align:center; margin:0;'>{calendar.month_name[current_view.month]} {current_view.year}</h2>", unsafe_allow_html=True)
    with nav_right:
        if st.button("Next ➡️", key="btn_next"):
            st.session_state.view_date += relativedelta(months=1)
            st.rerun()

    # --- GRID HEADER ---
    cols_header = st.columns(7)
    for i, hari in enumerate(["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]):
        cols_header[i].markdown(f"<p style='text-align:center; font-weight:bold; color:gray; font-size:14px;'>{hari}</p>", unsafe_allow_html=True)

    # --- GRID KALENDER ---
    cal_matrix = calendar.monthcalendar(current_view.year, current_view.month)
    for week in cal_matrix:
        week_cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                week_cols[i].write("")
            else:
                this_date = date(current_view.year, current_view.month, day)
                hst = (this_date - tanggal_tanam).days
                
                # Menentukan Label & Class CSS (Tanpa Emoji)
                status_label = ""
                bg_class = ""
                if 0 <= hst < 5:
                    status_label = "Pemantauan"
                    bg_class = "bg-pantau"
                elif 5 <= hst < 90:
                    status_label = "Pemupukan"
                    bg_class = "bg-pupuk"
                elif hst >= 90:
                    status_label = "Panen"
                    bg_class = "bg-panen"

                # Trick: Karena st.button tidak mendukung HTML di labelnya, 
                # kita gunakan st.markdown untuk menggambar visualnya, 
                # tapi tetap menggunakan tombol transparan atau tombol standar dengan label teks.
                # Agar Center & Berwarna, kita gunakan format string dengan spasi/newline.
                
                display_text = f"{day}\n{status_label}" if status_label else f"{day}"
                
                if week_cols[i].button(display_text, key=f"day_{current_view.month}_{day}", use_container_width=True):
                    st.session_state.selected_day = day
                    st.rerun()

# =========================
# 5. DETAIL PANEL
# =========================
with col2:
    st.markdown("### 📋 Detail Hari")
    sel_day = st.session_state.selected_day
    try:
        active_date = date(current_view.year, current_view.month, sel_day)
    except:
        active_date = date(current_view.year, current_view.month, 1)

    hst_active = (active_date - tanggal_tanam).days
    idx_rain = min(max(0, active_date.day - 1), len(forecast_30) - 1)
    rain_val = forecast_30[idx_rain]

    st.info(f"📅 **{active_date.strftime('%d %B %Y')}**\n\n🌱 **HST:** {hst_active} hari\n\n☔ **Hujan:** {rain_val:.2f} mm")

    if hst_active < 0:
        st.write("Belum masa tanam.")
    elif hst_active < 5:
        st.write("Fase Pemantauan Awal.")
    elif hst_active < 90:
        st.success("Kondisi mendukung untuk pemupukan.")
    else:
        st.warning("Perhatikan kesiapan lahan untuk panen.")

    st.divider()
    st.line_chart(forecast_30)
