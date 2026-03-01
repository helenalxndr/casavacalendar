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
# SIDEBAR
# =========================
st.sidebar.title("⚙ Pengaturan")

kecamatan_list = sorted(data["kecamatan"].unique())
selected_kecamatan = st.sidebar.selectbox("Pilih Kecamatan", kecamatan_list)

tanggal_tanam = st.sidebar.date_input("Tanggal Tanam")

# =========================
# FILTER DATA
# =========================
kec_id = encoder.transform([selected_kecamatan])[0]

df_kec = data[data["kecamatan"] == selected_kecamatan].copy()
df_kec = df_kec.sort_values("tanggal")

rain_last270 = df_kec["rain_mm"].values[-270:]

forecast_30 = recursive_forecast(
    model=model,
    scaler=scaler,
    rain_last270=rain_last270,
    kec_id=kec_id,
    days=30
)

# =========================
# SESSION STATE
# =========================
if "selected_day" not in st.session_state:
    st.session_state.selected_day = 1

# =========================
# CSS
# =========================
st.markdown("""
<style>

/* Kalender Grid */
.calendar {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 6px;
}

/* Day Card */
.day-card {
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    padding: 10px 6px;
    min-height: 70px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    cursor: pointer;
    transition: 0.2s;
}

.day-card:hover {
    background-color: #f3f4f6;
}

/* Day Number */
.day-number {
    font-weight: 600;
    font-size: 14px;
    color: #1f2937;
}

/* Label */
.label {
    font-size: 11px;
    margin-top: 4px;
    font-weight: 600;
}

/* Highlight warna hanya pada label */
.label.pemupukan {
    background-color: #ede9fe;
    color: #6d28d9;
    padding: 2px 6px;
    border-radius: 6px;
    display: inline-block;
}

.label.pemantauan {
    background-color: #e0f2fe;
    color: #0369a1;
    padding: 2px 6px;
    border-radius: 6px;
    display: inline-block;
}

.label.panen {
    background-color: #dcfce7;
    color: #166534;
    padding: 2px 6px;
    border-radius: 6px;
    display: inline-block;
}

/* Selected Day */
.selected {
    border: 2px solid #2563eb;
    background-color: #eff6ff;
}

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

    # Header Nama Hari
    cols_header = st.columns(7)
    nama_hari = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
    for i, nh in enumerate(nama_hari):
        cols_header[i].markdown(f"<p style='text-align:center; font-weight:bold; color:gray;'>{nh}</p>", unsafe_allow_html=True)

    # Ambil data kalender
    cal = calendar.monthcalendar(year, month)

    for week in cal:
        cols = st.columns(7) # Buat 7 kolom untuk tiap baris minggu
        for i, day in enumerate(week):
            if day == 0:
                cols[i].write("") # Kosongkan jika bukan tanggal bulan ini
            else:
                # Logika HST & Label
                current_date = datetime(year, month, day).date()
                hst = (current_date - tanggal_tanam).days
                
                label = ""
                if hst >= 0:
                    if hst < 5: label = "🌱 Pantau"
                    elif hst < 90: label = "💊 Pupuk"
                    else: label = "🌾 Panen"

                # Membuat Button sebagai pengganti kotak kalender
                # Button akan mengisi session_state saat diklik
                if cols[i].button(f"{day}\n{label}", key=f"btn_{day}", use_container_width=True):
                    st.session_state.selected_day = day
                    st.rerun() # Memaksa aplikasi update panel kanan segera

# =========================
# DETAIL PANEL (KOLOM KANAN)
# =========================
with col2:
    selected_day = st.session_state.selected_day
    
    # Validasi tanggal agar tidak error saat ganti bulan
    try:
        selected_date = datetime(year, month, selected_day).date()
    except ValueError:
        selected_day = 1
        selected_date = datetime(year, month, selected_day).date()

    hst = (selected_date - tanggal_tanam).days
    
    # Ambil prediksi hujan (index 0-29)
    idx = min(max(0, selected_day - 1), len(forecast_30) - 1)
    rain_pred = forecast_30[idx]

    st.markdown("### Detail Rekomendasi")
    st.info(f"📅 **{selected_date}**\n\n🌱 **HST:** {hst} hari\n\n☔ **Hujan:** {rain_pred:.2f} mm")

    if hst < 5:
        st.write("Kelembapan cukup untuk pertumbuhan awal.")
    elif hst < 90:
        st.success("Kondisi mendukung untuk pemupukan.")
    else:
        st.warning("Perhatikan kematangan tanaman untuk panen.")

    st.markdown("---")
    st.line_chart(forecast_30)
