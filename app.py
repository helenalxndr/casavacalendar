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
data["index"] = pd.to_datetime(data["index"])

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
df_kec = df_kec.sort_values("index")

rain_last270 = df_kec["curah_hujan_mm"].values[-270:]

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
col1, col2 = st.columns([3,1])

with col1:

    today = datetime.today()
    year = today.year
    month = today.month

    st.markdown(f"<h2 style='text-align:center'>{calendar.month_name[month]} {year}</h2>", unsafe_allow_html=True)

    cal = calendar.monthcalendar(year, month)

    st.markdown("<div class='calendar'>", unsafe_allow_html=True)

    for week in cal:
        for day in week:
            if day == 0:
                st.markdown("<div></div>", unsafe_allow_html=True)
            else:

                # HST
                current_date = datetime(year, month, day).date()
                hst = (current_date - tanggal_tanam).days

                # Tentukan label
                if hst < 0:
                    label = ""
                    label_class = ""
                elif hst < 5:
                    label = "Pemantauan"
                    label_class = "pemantauan"
                elif hst < 90:
                    label = "Pemupukan"
                    label_class = "pemupukan"
                else:
                    label = "Panen"
                    label_class = "panen"

                # Selected state
                selected_class = ""
                if st.session_state.selected_day == day:
                    selected_class = "selected"

                st.markdown(f"""
                <div class="day-card {selected_class}"
                     onclick="window.location.href='?day={day}'">
                    <div class="day-number">{day}</div>
                    {f"<div class='label {label_class}'>{label}</div>" if label else ""}
                </div>
                """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

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
