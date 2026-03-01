import streamlit as st
import calendar
from datetime import datetime
import pandas as pd

from utils.loader import load_all
from utils.forecast import recursive_forecast
from utils.rbs import rbs_singkong_final, label_singkat

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="Kalender Tanam Singkong", layout="wide")

# =====================================================
# LOAD
# =====================================================
@st.cache_resource
def init():
    return load_all()

model, encoder, scaler, data = init()

if "index" in data.columns:
    data["tanggal"] = pd.to_datetime(data["index"])

if "curah_hujan_mm" in data.columns:
    data["rain_mm"] = data["curah_hujan_mm"]

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.title("⚙ Pengaturan")
kecamatan = st.sidebar.selectbox("Pilih Kecamatan", encoder.classes_)
tanggal_tanam = st.sidebar.date_input("Tanggal Tanam", value=datetime.today())
kec_id = encoder.transform([kecamatan])[0]

df_kec = data[data["kecamatan"] == kecamatan].sort_values("tanggal")

if len(df_kec) < 270:
    st.error("Data historis kurang dari 270 hari.")
    st.stop()

rain_last270 = df_kec["rain_mm"].values[-270:]
forecast = recursive_forecast(model, scaler, rain_last270, kec_id, days=31)

# =====================================================
# STATE
# =====================================================
if "month" not in st.session_state:
    st.session_state.month = datetime.today().month
if "year" not in st.session_state:
    st.session_state.year = datetime.today().year
if "selected_day" not in st.session_state:
    st.session_state.selected_day = datetime.today().day

month = st.session_state.month
year = st.session_state.year

days_in_month = calendar.monthrange(year, month)[1]
predictions = forecast[:days_in_month]

# =====================================================
# COLOR PALETTE (BLOCK STYLE)
# =====================================================
label_block_color = {
    "Penanaman": "#DCFCE7",
    "Pemupukan": "#EDE9FE",
    "Penyiraman": "#DBEAFE",
    "Pembersihan Gulma": "#FEF3C7",
    "Pemanenan": "#FEE2E2",
    "Pemantauan": "#F3F4F6"
}

label_text_color = {
    "Penanaman": "#15803D",
    "Pemupukan": "#6D28D9",
    "Penyiraman": "#1D4ED8",
    "Pembersihan Gulma": "#B45309",
    "Pemanenan": "#B91C1C",
    "Pemantauan": "#374151"
}

# =====================================================
# CSS
# =====================================================
st.markdown("""
<style>
.calendar-grid {
    display:grid;
    grid-template-columns: repeat(7, 1fr);
    gap:6px;
}

.day-box {
    background:white;
    border:1px solid #E5E7EB;
    border-radius:12px;
    height:100px;
    padding:8px;
    cursor:pointer;
    transition:0.2s;
}

.day-box:hover {
    background:#F9FAFB;
}

.day-number {
    font-weight:600;
    font-size:14px;
}

.label-pill {
    margin-top:6px;
    padding:4px 6px;
    border-radius:6px;
    font-size:11px;
    display:inline-block;
}
.selected {
    border:2px solid #059669 !important;
}
.today {
    border:2px solid #10B981 !important;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# LAYOUT
# =====================================================
left, right = st.columns([2.5,1])

with left:

    st.markdown(
        f"<h2 style='text-align:center;color:#1F2937;'>"
        f"{calendar.month_name[month]} {year}</h2>",
        unsafe_allow_html=True
    )

    cal = calendar.monthcalendar(year, month)
    today = datetime.today()

    st.markdown("<div class='calendar-grid'>", unsafe_allow_html=True)

    for week in cal:
        for day in week:
            if day == 0:
                st.markdown("<div></div>", unsafe_allow_html=True)
            else:
                hujan = predictions[day-1]
                tanggal_prediksi = datetime(year, month, day)
                hst = (tanggal_prediksi.date() - tanggal_tanam).days

                aktivitas = rbs_singkong_final(hujan, hst)
                label = label_singkat(aktivitas)

                block_color = label_block_color.get(label, "#F3F4F6")
                text_color = label_text_color.get(label, "#374151")

                selected_class = ""
                if day == st.session_state.selected_day:
                    selected_class = "selected"
                if (
                    day == today.day and
                    month == today.month and
                    year == today.year
                ):
                    selected_class += " today"

                box_html = f"""
                <div class="day-box {selected_class}"
                     onclick="window.location.href='?day={day}'">
                    <div class="day-number">{day}</div>
                    <div class="label-pill"
                         style="background:{block_color};color:{text_color};">
                        {label}
                    </div>
                </div>
                """

                st.markdown(box_html, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# Handle click via query param
query = st.query_params
if "day" in query:
    st.session_state.selected_day = int(query["day"])

# =====================================================
# DETAIL
# =====================================================
with right:

    selected_day = st.session_state.selected_day
    hujan = predictions[selected_day-1]
    tanggal_selected = datetime(year, month, selected_day)
    hst_selected = (tanggal_selected.date() - tanggal_tanam).days
    aktivitas_full = rbs_singkong_final(hujan, hst_selected)

    st.subheader("Detail Rekomendasi")
    st.write(f"📅 {selected_day} {calendar.month_name[month]} {year}")
    st.write(f"🌱 HST: {hst_selected} hari")
    st.metric("🌧 Prediksi Hujan", f"{hujan:.2f} mm")
    st.info(aktivitas_full)

    st.divider()
    st.subheader("Grafik Prediksi Hujan")

    df_chart = pd.DataFrame({
        "Hari": list(range(1, days_in_month+1)),
        "Curah Hujan (mm)": predictions
    })

    st.line_chart(df_chart.set_index("Hari"))
