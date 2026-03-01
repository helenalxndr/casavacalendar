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

    # Ambil struktur minggu dan hari dari library calendar
    cal = calendar.monthcalendar(year, month)

    # MEMBUAT STRING HTML KALENDER
    calendar_html = "<div class='calendar'>"

    # 1. Tambahkan Header Nama Hari
    nama_hari = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
    for nh in nama_hari:
        calendar_html += f"<div style='text-align:center; font-weight:bold; color:#6b7280; font-size:13px;'>{nh}</div>"

    # 2. Tambahkan Tanggal-tanggal
    for week in cal:
        for day in week:
            if day == 0:
                # Kolom kosong untuk hari di luar bulan berjalan
                calendar_html += "<div></div>"
            else:
                # Hitung HST (Hari Setelah Tanam)
                current_date = datetime(year, month, day).date()
                hst = (current_date - tanggal_tanam).days

                # Tentukan label dan class CSS berdasarkan HST
                if hst < 0:
                    label, label_class = "", ""
                elif hst < 5:
                    label, label_class = "Pemantauan", "pemantauan"
                elif hst < 90:
                    label, label_class = "Pemupukan", "pemupukan"
                else:
                    label, label_class = "Panen", "panen"

                # Cek apakah hari ini sedang dipilih (Selected)
                selected_class = "selected" if st.session_state.selected_day == day else ""

                # Gabungkan ke dalam string HTML
                calendar_html += f"""
                <div class="day-card {selected_class}" 
                     onclick="window.location.href='?day={day}'">
                    <div class="day-number">{day}</div>
                    {f"<div class='label {label_class}'>{label}</div>" if label else ""}
                </div>
                """

    calendar_html += "</div>" # Tutup div class 'calendar'

    # Tampilkan seluruh kalender dalam satu kali panggil
    st.markdown(calendar_html, unsafe_allow_html=True)
# =========================
# HANDLE CLICK
# =========================
query_params = st.query_params
if "day" in query_params:
    st.session_state.selected_day = int(query_params["day"])

# =========================
# DETAIL PANEL
# =========================
with col2:

    selected_day = st.session_state.selected_day
    selected_date = datetime(year, month, selected_day).date()
    hst = (selected_date - tanggal_tanam).days

    rain_pred = forecast_30[selected_day-1]

    st.markdown("### Detail Rekomendasi")
    st.write(f"📅 {selected_date}")
    st.write(f"🌱 HST: {hst} hari")
    st.write(f"☔ Prediksi Hujan: **{rain_pred:.2f} mm**")

    if hst < 5:
        st.info("Pemantauan awal – kelembapan cukup untuk pertumbuhan awal.")
    elif hst < 90:
        st.success("Fase pemupukan – kondisi mendukung.")
    else:
        st.warning("Mendekati panen – perhatikan kondisi lahan.")

    st.markdown("---")
    st.line_chart(forecast_30)
