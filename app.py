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
# HANDLE CLICK (BEFORE UI)
# =========================
query_params = st.query_params
if "day" in query_params:
    st.session_state.selected_day = int(query_params["day"])

# =========================
# CSS (GRID FIXED)
# =========================
st.markdown("""
<style>

.calendar-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 8px;
    margin-top: 20px;
}

.day-header {
    text-align: center;
    font-weight: 600;
    color: #6b7280;
    font-size: 13px;
}

.day-card {
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    padding: 8px;
    min-height: 75px;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    cursor: pointer;
    transition: 0.2s ease;
}

.day-card:hover {
    background-color: #f3f4f6;
}

.day-number {
    font-weight: 600;
    font-size: 14px;
    color: #1f2937;
}

.label {
    font-size: 11px;
    margin-top: 6px;
    font-weight: 600;
    padding: 2px 6px;
    border-radius: 6px;
    display: inline-block;
}

.pemupukan {
    background-color: #ede9fe;
    color: #6d28d9;
}

.pemantauan {
    background-color: #e0f2fe;
    color: #0369a1;
}

.panen {
    background-color: #dcfce7;
    color: #166534;
}

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

    st.markdown(
        f"<h2 style='text-align:center'>{calendar.month_name[month]} {year}</h2>",
        unsafe_allow_html=True
    )

    # HEADER HARI
    days_name = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]

    st.markdown("<div class='calendar-grid'>", unsafe_allow_html=True)

    for d in days_name:
        st.markdown(f"<div class='day-header'>{d}</div>", unsafe_allow_html=True)

    cal = calendar.monthcalendar(year, month)

    for week in cal:
        for day in week:

            if day == 0:
                st.markdown("<div></div>", unsafe_allow_html=True)
            else:
                current_date = datetime(year, month, day).date()
                hst = (current_date - tanggal_tanam).days

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
# DETAIL PANEL
# =========================
with col2:

    selected_day = st.session_state.selected_day
    selected_date = datetime(year, month, selected_day).date()
    hst = (selected_date - tanggal_tanam).days

    rain_pred = forecast_30[selected_day - 1]

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
