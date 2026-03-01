import streamlit as st
import calendar
from datetime import datetime
import pandas as pd

from utils.loader import load_all
from utils.forecast import recursive_forecast
from utils.rbs import rbs_singkong_final, label_singkat

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="Kalender Tanam Singkong", layout="wide")

# =========================================================
# LOAD RESOURCE
# =========================================================
@st.cache_resource
def init():
    return load_all()

model, encoder, scaler, data = init()

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("Pengaturan")

kecamatan = st.sidebar.selectbox("Pilih Kecamatan", encoder.classes_)
tanggal_tanam = st.sidebar.date_input("Tanggal Tanam", value=datetime.today())
kec_id = encoder.transform([kecamatan])[0]

# =========================================================
# DATA PREP
# =========================================================
data["tanggal"] = pd.to_datetime(data["tanggal"])
df_kec = data[data["kecamatan"] == kecamatan].sort_values("tanggal")

rain_last270 = df_kec["rain_mm"].values[-270:]

forecast = recursive_forecast(model, scaler, rain_last270, kec_id, days=31)

# =========================================================
# NAVIGASI BULAN (SEBARIS)
# =========================================================
if "month" not in st.session_state:
    st.session_state.month = datetime.today().month

if "year" not in st.session_state:
    st.session_state.year = datetime.today().year

nav1, nav2, nav3 = st.columns([1,6,1])

with nav1:
    if st.button("◀"):
        if st.session_state.month == 1:
            st.session_state.month = 12
            st.session_state.year -= 1
        else:
            st.session_state.month -= 1

with nav3:
    if st.button("▶"):
        if st.session_state.month == 12:
            st.session_state.month = 1
            st.session_state.year += 1
        else:
            st.session_state.month += 1

month = st.session_state.month
year = st.session_state.year

with nav2:
    st.markdown(
        f"<h2 style='text-align:center;'>{calendar.month_name[month]} {year}</h2>",
        unsafe_allow_html=True
    )

days_in_month = calendar.monthrange(year, month)[1]
predictions = forecast[:days_in_month]

# =========================================================
# WARNA SOFT
# =========================================================
def warna_soft(label):
    mapping = {
        "Penanaman": "#2E7D32",
        "Pemupukan": "#EF6C00",
        "Penyiraman": "#1565C0",
        "Pembersihan Gulma": "#6A1B9A",
        "Pemanenan": "#F9A825",
        "Pemantauan": "#455A64"
    }
    return mapping.get(label, "#455A64")

# =========================================================
# LAYOUT RESPONSIVE
# =========================================================
left, right = st.columns([2.3,1])

# =========================================================
# KALENDER
# =========================================================
with left:

    # Header hari
    header = st.columns(7)
    for i, d in enumerate(["Sen","Sel","Rab","Kam","Jum","Sab","Min"]):
        header[i].markdown(f"**{d}**")

    cal = calendar.monthcalendar(year, month)
    today = datetime.today()

    # CSS
    st.markdown("""
    <style>
    .calendar-box {
        padding:12px;
        border-radius:14px;
        text-align:center;
        font-size:13px;
        min-height:95px;
        display:flex;
        flex-direction:column;
        justify-content:center;
    }
    .day-number {
        font-size:18px;
        font-weight:bold;
        margin-bottom:6px;
    }
    </style>
    """, unsafe_allow_html=True)

    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):

            if day == 0:
                cols[i].write("")
            else:
                hujan = predictions[day-1]
                tanggal_prediksi = datetime(year, month, day)
                hst = (tanggal_prediksi.date() - tanggal_tanam).days

                aktivitas_full = rbs_singkong_final(hujan, hst)
                label = label_singkat(aktivitas_full)

                color = warna_soft(label)

                border = ""
                if (day == today.day and month == today.month and year == today.year):
                    border = "border:3px solid #000;"

                box_html = f"""
                <div class="calendar-box"
                     style="background:{color}; color:white; {border}">
                    <div class="day-number">{day}</div>
                    {label}
                </div>
                """

                if cols[i].button(" ", key=f"day_{day}"):
                    st.session_state.selected_day = day

                cols[i].markdown(box_html, unsafe_allow_html=True)

# =========================================================
# DETAIL PANEL
# =========================================================
with right:

    if "selected_day" not in st.session_state:
        st.session_state.selected_day = 1

    selected = st.session_state.selected_day

    hujan = predictions[selected-1]
    tanggal_selected = datetime(year, month, selected)
    hst_selected = (tanggal_selected.date() - tanggal_tanam).days

    aktivitas_full = rbs_singkong_final(hujan, hst_selected)

    st.markdown("### Detail Rekomendasi")
    st.write(f"📅 {selected} {calendar.month_name[month]} {year}")
    st.write(f"🌱 HST: {hst_selected} hari")
    st.metric("🌧 Prediksi Hujan", f"{hujan:.2f} mm")

    st.info(aktivitas_full)

    st.markdown("---")

    # ===============================
    # GRAFIK DI BAWAH DETAIL
    # ===============================
    st.markdown("### Grafik Prediksi Hujan")

    df_chart = pd.DataFrame({
        "Hari": list(range(1, days_in_month+1)),
        "Hujan": predictions
    })

    st.line_chart(df_chart.set_index("Hari"))
