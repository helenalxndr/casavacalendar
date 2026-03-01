import streamlit as st
import pandas as pd
import numpy as np
import calendar
from datetime import datetime
from utils.loader import load_all
from utils.forecast import recursive_forecast

st.set_page_config(layout="wide")

# =========================
# LOAD DATA
# =========================
model, encoder, scaler, data = load_all()
data["tanggal"] = pd.to_datetime(data["tanggal"])

# =========================
# SESSION STATE
# =========================
if "selected_day" not in st.session_state:
    st.session_state.selected_day = datetime.today().day

# =========================
# SIDEBAR
# =========================
st.sidebar.title("⚙ Pengaturan")
kecamatan_list = sorted(data["kecamatan"].unique())
selected_kecamatan = st.sidebar.selectbox("Pilih Kecamatan", kecamatan_list)
tanggal_tanam = st.sidebar.date_input("Tanggal Tanam", value=datetime.today())

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
    /* Styling Dasar Tombol agar Jadi Kotak Kalender */
    div.stButton > button {
        height: 100px;
        width: 100%;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        background-color: white;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        padding: 8px;
        transition: 0.2s;
    }
    
    /* Efek Hover */
    div.stButton > button:hover {
        border-color: #2563eb;
        background-color: #f9fafb;
    }

    /* Hilangkan border default saat diklik agar tidak jelek */
    div.stButton > button:focus {
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.3);
        border: 2px solid #2563eb !important;
    }

    /* Styling Teks di dalam Tombol (Markdown-like) */
    .btn-text-container { text-align: left; width: 100%; }
    .day-num { font-size: 16px; font-weight: bold; color: #1f2937; }
    .label-mini { 
        font-size: 10px; font-weight: bold; margin-top: 10px;
        padding: 2px 6px; border-radius: 4px; display: inline-block;
    }
    .lbl-pantau { background-color: #e0f2fe; color: #0369a1; }
    .lbl-pupuk { background-color: #ede9fe; color: #6d28d9; }
    .lbl-panen { background-color: #dcfce7; color: #166534; }
</style>
""", unsafe_allow_html=True)

# =========================
# MAIN LAYOUT
# =========================
col1, col2 = st.columns([3, 1])

with col1:
    today = datetime.today()
    year = today.year
    month = today.month

    st.markdown(f"<h2 style='text-align:center'>{calendar.month_name[month]} {year}</h2>", unsafe_allow_html=True)
    
    # Header Hari
    cols_h = st.columns(7)
    for i, h in enumerate(["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]):
        cols_h[i].markdown(f"<p style='text-align:center; font-weight:bold; color:gray;'>{h}</p>", unsafe_allow_html=True)

    cal = calendar.monthcalendar(year, month)
    
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].write("")
            else:
                current_date = datetime(year, month, day).date()
                hst = (current_date - tanggal_tanam).days
                
                # Menentukan Label untuk disisipkan ke dalam Tombol
                label_html = ""
                if 0 <= hst < 5:
                    label_html = f'<div class="label-mini lbl-pantau">🌱 Pantau</div>'
                elif 5 <= hst < 90:
                    label_html = f'<div class="label-mini lbl-pupuk">💊 Pupuk</div>'
                elif hst >= 90:
                    label_html = f'<div class="label-mini lbl-panen">🌾 Panen</div>'

                # Render Tombol dengan HTML di dalamnya (Trick: unsafe_allow_html tidak jalan di label button, 
                # tapi kita bisa pakai emoji dan teks biasa)
                button_label = f"{day}"
                if hst >= 0:
                    status = "🌱" if hst < 5 else "💊" if hst < 90 else "🌾"
                    button_label = f"{day}\n{status}"

                # Eksekusi Klik: HANYA update session state, tanpa refresh page URL
                if cols[i].button(button_label, key=f"d_{day}", use_container_width=True):
                    st.session_state.selected_day = day
                    # Ini akan trigger rerun internal Streamlit (cepat, tanpa reload browser)
                    st.rerun()

# =========================
# DETAIL PANEL (Update Instan)
# =========================
with col2:
    selected_day = st.session_state.selected_day
    try:
        selected_date = datetime(year, month, selected_day).date()
    except:
        selected_date = datetime(year, month, 1).date()

    hst = (selected_date - tanggal_tanam).days
    idx = min(max(0, selected_day - 1), len(forecast_30) - 1)
    rain_pred = forecast_30[idx]

    st.markdown(f"### 📋 Detail Hari ke-{selected_day}")
    st.info(f"📅 **{selected_date.strftime('%d %B %Y')}**\n\n🌱 **HST:** {hst} hari\n\n☔ **Hujan:** {rain_pred:.2f} mm")

    if hst < 5:
        st.write("Fase Pemantauan.")
    elif hst < 90:
        st.success("Fase Pemupukan.")
    else:
        st.warning("Fase Panen.")

    st.divider()
    st.line_chart(forecast_30)
