import streamlit as st
import pandas as pd
import numpy as np
import calendar
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from utils.loader import load_all
from utils.forecast import recursive_forecast

st.set_page_config(layout="wide")

# =========================
# LOAD DATA
# =========================
model, encoder, scaler, data = load_all()
data["tanggal"] = pd.to_datetime(data["tanggal"])

# =========================
# SESSION STATE (Untuk Navigasi & Seleksi)
# =========================
if "current_month_view" not in st.session_state:
    st.session_state.current_month_view = datetime.today().replace(day=1)

if "selected_day" not in st.session_state:
    st.session_state.selected_day = datetime.today().day

# =========================
# SIDEBAR
# =========================
st.sidebar.title("⚙ Pengaturan")
kecamatan_list = sorted(data["kecamatan"].unique())
selected_kecamatan = st.sidebar.selectbox("Pilih Kecamatan", kecamatan_list)
tanggal_tanam = st.sidebar.date_input("Tanggal Tanam", value=date(2026, 3, 1))

# =========================
# FORECAST
# =========================
kec_id = encoder.transform([selected_kecamatan])[0]
df_kec = data[data["kecamatan"] == selected_kecamatan].copy().sort_values("tanggal")
rain_last270 = df_kec["rain_mm"].values[-270:]
forecast_30 = recursive_forecast(model=model, scaler=scaler, rain_last270=rain_last270, kec_id=kec_id, days=30)

# =========================
# CSS INJECTION (Kunci Utama)
# =========================
st.markdown("""
<style>
    /* Styling Dasar Tombol agar Jadi Kotak Kalender Center */
    div.stButton > button {
        height: 100px;
        width: 100%;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        background-color: white;
        display: flex;
        flex-direction: column;
        align-items: center;    /* Center Horizontal */
        justify-content: center; /* Center Vertical */
        padding: 8px;
        transition: 0.2s;
        white-space: pre-line;   /* Agar \n bekerja */
        line-height: 1.5;
    }
    
    /* Hover effect */
    div.stButton > button:hover {
        border-color: #2563eb;
        background-color: #f9fafb;
    }

    /* Fokus/Selected */
    div.stButton > button:focus {
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.3);
        border: 2px solid #2563eb !important;
    }

    /* Styling teks di dalam tombol */
    .stButton > button p {
        font-size: 18px !important;
        font-weight: bold !important;
        text-align: center !important;
    }

    /* Navigasi Month Styling */
    .month-nav-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# MAIN LAYOUT
# =========================
col1, col2 = st.columns([3, 1])

with col1:
    # 1. NAVIGASI BULAN (Previous, Month Name, Next)
    nav_col1, nav_col2, nav_col3 = st.columns([1, 3, 1])
    
    with nav_col1:
        if st.button("⬅️ Prev", key="prev_month"):
            st.session_state.current_month_view -= relativedelta(months=1)
            st.rerun()
            
    with nav_col2:
        view_date = st.session_state.current_month_view
        st.markdown(f"<h2 style='text-align:center; margin:0;'>{calendar.month_name[view_date.month]} {view_date.year}</h2>", unsafe_allow_html=True)
        
    with nav_col3:
        if st.button("Next ➡️", key="next_month"):
            st.session_state.current_month_view += relativedelta(months=1)
            st.rerun()

    # Header Hari (Sen - Min)
    cols_h = st.columns(7)
    days_name = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
    for i, h in enumerate(days_name):
        cols_h[i].markdown(f"<p style='text-align:center; font-weight:bold; color:gray;'>{h}</p>", unsafe_allow_html=True)

    # Isi Kalender
    cal = calendar.monthcalendar(view_date.year, view_date.month)
    
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].write("")
            else:
                current_date = date(view_date.year, view_date.month, day)
                hst = (current_date - tanggal_tanam).days
                
                # Menentukan Emoji Status
                status_emoji = ""
                if 0 <= hst < 5: status_emoji = "🌱"
                elif 5 <= hst < 90: status_emoji = "💊"
                elif hst >= 90: status_emoji = "🌾"

                # Label Tombol (Angka di atas, Emoji di bawah)
                button_label = f"{day}\n{status_emoji}"

                if cols[i].button(button_label, key=f"btn_{view_date.year}_{view_date.month}_{day}", use_container_width=True):
                    st.session_state.selected_day = day
                    st.session_state.selected_month = view_date.month
                    st.session_state.selected_year = view_date.year
                    st.rerun()

# =========================
# DETAIL PANEL
# =========================
with col2:
    sel_day = st.session_state.selected_day
    view_dt = st.session_state.current_month_view
    
    try:
        selected_date = date(view_dt.year, view_dt.month, sel_day)
    except:
        # Jika ganti bulan dan tanggal sebelumnya tidak ada (misal tgl 31), reset ke tgl 1
        selected_date = date(view_dt.year, view_dt.month, 1)

    hst = (selected_date - tanggal_tanam).days
    
    # Ambil index prediksi (hanya valid jika dalam rentang forecast)
    # Di sini kita asumsikan forecast_30 dimulai dari hari ini/tanggal tertentu
    # Untuk demo, kita pakai index sederhana berdasarkan tanggal
    idx = min(max(0, selected_date.day - 1), len(forecast_30) - 1)
    rain_pred = forecast_30[idx]

    st.markdown(f"### 📋 Detail Hari")
    st.info(f"📅 **{selected_date.strftime('%d %B %Y')}**\n\n🌱 **HST:** {hst} hari\n\n☔ **Hujan:** {rain_pred:.2f} mm")

    if hst < 0:
        st.write("Belum masa tanam.")
    elif hst < 5:
        st.write("Fase Pemantauan.")
    elif hst < 90:
        st.success("Waktunya pemberian pupuk.")
    else:
        st.warning("Mendekati masa panen.")

    st.divider()
    st.line_chart(forecast_30)
