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
st.set_page_config(
    page_title="Kalender Tanam Singkong",
    layout="wide"
)

# =====================================================
# LOAD DATA
# =====================================================
@st.cache_resource
def init():
    return load_all()

model, encoder, scaler, data = init()

# Aman rename kolom
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

# =====================================================
# FILTER DATA
# =====================================================
df_kec = data[data["kecamatan"] == kecamatan].sort_values("tanggal")

if len(df_kec) < 270:
    st.error("Data historis kurang dari 270 hari.")
    st.stop()

rain_last270 = df_kec["rain_mm"].values[-270:]
forecast = recursive_forecast(model, scaler, rain_last270, kec_id, days=31)

# =====================================================
# STATE BULAN
# =====================================================
if "month" not in st.session_state:
    st.session_state.month = datetime.today().month

if "year" not in st.session_state:
    st.session_state.year = datetime.today().year

if "selected_day" not in st.session_state:
    st.session_state.selected_day = datetime.today().day

# =====================================================
# NAVIGASI
# =====================================================
col1, col2, col3 = st.columns([1,6,1])

with col1:
    if st.button("◀"):
        if st.session_state.month == 1:
            st.session_state.month = 12
            st.session_state.year -= 1
        else:
            st.session_state.month -= 1

with col3:
    if st.button("▶"):
        if st.session_state.month == 12:
            st.session_state.month = 1
            st.session_state.year += 1
        else:
            st.session_state.month += 1

month = st.session_state.month
year = st.session_state.year

with col2:
    st.markdown(
        f"<h2 style='text-align:center;color:#1F2937;'>"
        f"{calendar.month_name[month]} {year}</h2>",
        unsafe_allow_html=True
    )

days_in_month = calendar.monthrange(year, month)[1]
predictions = forecast[:days_in_month]

# =====================================================
# CSS AESTHETIC
# =====================================================
st.markdown("""
<style>

.main {
    background-color:#F8FAFC;
}

div[data-testid="column"] {
    padding:2px !important;
}

div[data-testid="stHorizontalBlock"] {
    gap:6px !important;
}

div.stButton > button {
    height:95px;
    border-radius:12px;
    border:1px solid #E5E7EB;
    background:#FFFFFF;
    text-align:left;
    padding:10px;
    font-size:13px;
    font-weight:500;
    white-space:pre-line;
    transition:all 0.2s ease;
}

div.stButton > button:hover {
    background:#F1F5F9;
    transform:scale(1.02);
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# COLOR MAP
# =====================================================

# =====================================================
# LAYOUT
# =====================================================
left, right = st.columns([2.5,1])

# =====================================================
# KALENDER
# =====================================================
with left:

    header = st.columns(7)
    for i, d in enumerate(["Sen","Sel","Rab","Kam","Jum","Sab","Min"]):
        header[i].markdown(
            f"<div style='text-align:center;font-size:13px;color:#6B7280;'>{d}</div>",
            unsafe_allow_html=True
        )

    cal = calendar.monthcalendar(year, month)
    today = datetime.today()

    for week in cal:
        cols = st.columns(7)

        for i, day in enumerate(week):

            if day == 0:
                cols[i].markdown("<div style='height:95px;text-align:center;'></div>", unsafe_allow_html=True)
            else:
                hujan = predictions[day-1]
                tanggal_prediksi = datetime(year, month, day)
                hst = (tanggal_prediksi.date() - tanggal_tanam).days

                aktivitas = rbs_singkong_final(hujan, hst)
                label = label_singkat(aktivitas)

                is_today = (
                    day == today.day and
                    month == today.month and
                    year == today.year
                )

                is_selected = day == st.session_state.selected_day

                text = f"{day}\n{label}"

                if cols[i].button(text, key=f"day_{day}", use_container_width=True):
                    st.session_state.selected_day = day

                # highlight visual fix
                if is_today:
                    cols[i].markdown(
                        "<style>button[kind='secondary'] {background:#ECFDF5 !important;}</style>",
                        unsafe_allow_html=True
                    )

# =====================================================
# DETAIL PANEL
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
