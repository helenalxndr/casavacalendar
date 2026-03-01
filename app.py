import streamlit as st
import pandas as pd
import numpy as np
import calendar
from datetime import datetime
from utils.loader import load_all
from utils.forecast import recursive_forecast

st.set_page_config(layout="wide", page_title="Sistem Kalender Tanam")

# =========================
# LOAD DATA & LOGIC
# =========================
model, encoder, scaler, data = load_all()
data["tanggal"] = pd.to_datetime(data["tanggal"])

# Ambil parameter hari dari URL (Handle Click)
query_params = st.query_params
if "day" in query_params:
    st.session_state.selected_day = int(query_params["day"])

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

forecast_30 = recursive_forecast(
    model=model, scaler=scaler, rain_last270=rain_last270, 
    kec_id=kec_id, days=30
)

# =========================
# CSS (Grid & Label)
# =========================
st.markdown("""
<style>
.calendar-container {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 10px;
    width: 100%;
}
.day-card {
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    padding: 12px 8px;
    min-height: 90px;
    display: flex;
    flex-direction: column;
    cursor: pointer;
    transition: 0.2s;
    background: white;
    text-decoration: none !important;
    color: inherit !important;
}
.day-card:hover {
    background-color: #f9fafb;
    border-color: #2563eb;
}
.selected {
    border: 2px solid #2563eb;
    background-color: #eff6ff;
}
.day-number {
    font-weight: bold;
    font-size: 16px;
    margin-bottom: 5px;
}
.label {
    font-size: 10px;
    font-weight: 700;
    padding: 3px 6px;
    border-radius: 5px;
    width: fit-content;
}
.pemupukan { background-color: #ede9fe; color: #6d28d9; }
.pemantauan { background-color: #e0f2fe; color: #0369a1; }
.panen { background-color: #dcfce7; color: #166534; }
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
    
    cal = calendar.monthcalendar(year, month)
    
    # Header Hari
    nama_hari = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
    header_html = "".join([f"<div style='text-align:center; font-weight:bold; color:gray;'>{h}</div>" for h in nama_hari])

    # Isi Tanggal
    body_html = ""
    for week in cal:
        for day in week:
            if day == 0:
                body_html += "<div></div>"
            else:
                current_date = datetime(year, month, day).date()
                hst = (current_date - tanggal_tanam).days
                
                # Logika Label
                label_tag = ""
                if 0 <= hst < 5:
                    label_tag = '<div class="label pemantauan">Pemantauan</div>'
                elif 5 <= hst < 90:
                    label_tag = '<div class="label pemupukan">Pemupukan</div>'
                elif hst >= 90:
                    label_tag = '<div class="label panen">Panen</div>'

                selected_class = "selected" if st.session_state.selected_day == day else ""
                
                # PENTING: Tulis HTML dalam satu baris tanpa spasi awal (indent) untuk menghindari bug Markdown
                body_html += f'<a href="?day={day}" target="_self" class="day-card {selected_class}"><div class="day-number">{day}</div>{label_tag}</a>'

    # Gabungkan semua dalam satu container grid
    st.markdown(f'<div class="calendar-container">{header_html}{body_html}</div>', unsafe_allow_html=True)

# =========================
# DETAIL PANEL (Kolom Kanan)
# =========================
with col2:
    selected_day = st.session_state.selected_day
    try:
        selected_date = datetime(year, month, selected_day).date()
    except:
        selected_day = 1
        selected_date = datetime(year, month, 1).date()

    hst = (selected_date - tanggal_tanam).days
    idx = min(max(0, selected_day - 1), len(forecast_30) - 1)
    rain_pred = forecast_30[idx]

    st.subheader("📋 Detail Hari")
    st.info(f"📅 **{selected_date.strftime('%d %B %Y')}**\n\n🌱 **HST:** {hst} hari\n\n☔ **Hujan:** {rain_pred:.2f} mm")

    if hst < 5:
        st.write("Fase awal pertumbuhan.")
    elif hst < 90:
        st.success("Waktunya pemberian pupuk.")
    else:
        st.warning("Siap untuk masa panen.")

    st.divider()
    st.line_chart(forecast_30)
