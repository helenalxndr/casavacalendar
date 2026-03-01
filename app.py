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
    page_title="Sistem Pakar Tanam Singkong",
    layout="wide"
)

# =====================================
# LOAD DATA & MODEL
# =====================================
@st.cache_resource
def init():
    return load_all()

model, encoder, scaler, data = init()

# Sinkronisasi nama kolom
if "index" in data.columns:
    data["tanggal"] = pd.to_datetime(data["index"])

if "curah_hujan_mm" in data.columns:
    data["rain_mm"] = data["curah_hujan_mm"]

# =====================================
# SIDEBAR
# =====================================
st.sidebar.title("Pengaturan")

kecamatan = st.sidebar.selectbox("Pilih Kecamatan", encoder.classes_)
tanggal_tanam = st.sidebar.date_input("Tanggal Tanam", value=datetime.today())

kec_id = encoder.transform([kecamatan])[0]

# =====================================
# PROSES FORECASTING
# =====================================
df_kec = data[data["kecamatan"] == kecamatan].sort_values("tanggal")

if len(df_kec) < 270:
    st.error("Data historis tidak mencukupi (min. 270 hari).")
    st.stop()

rain_last270 = df_kec["rain_mm"].values[-270:]
forecast = recursive_forecast(model, scaler, rain_last270, kec_id, days=31)

# =====================================
# STATE MANAGEMENT
# =====================================
if "month" not in st.session_state:
    st.session_state.month = datetime.today().month

if "year" not in st.session_state:
    st.session_state.year = datetime.today().year

if "selected_day" not in st.session_state:
    st.session_state.selected_day = datetime.today().day

# =====================================
# NAVIGASI KALENDER
# =====================================
col1, col2, col3 = st.columns([1,6,1])

with col1:
    if st.button("Sebelumnya"):
        if st.session_state.month == 1:
            st.session_state.month = 12
            st.session_state.year -= 1
        else:
            st.session_state.month -= 1

with col3:
    if st.button("Selanjutnya"):
        if st.session_state.month == 12:
            st.session_state.month = 1
            st.session_state.year += 1
        else:
            st.session_state.month += 1

month = st.session_state.month
year = st.session_state.year

with col2:
    st.markdown(
        f"<h2 style='text-align:center; color:#1F2937;'>{calendar.month_name[month]} {year}</h2>",
        unsafe_allow_html=True
    )

days_in_month = calendar.monthrange(year, month)[1]
predictions = forecast[:days_in_month]

# =====================================
# SKEMA WARNA (TANPA EMOJI)
# =====================================
# Menggunakan palet warna yang kontras namun profesional
style_config = {
    "Penanaman": {"bg": "#10B981", "text": "#FFFFFF"}, # Emerald
    "Pemupukan": {"bg": "#F59E0B", "text": "#FFFFFF"}, # Amber
    "Penyiraman": {"bg": "#3B82F6", "text": "#FFFFFF"}, # Blue
    "Pembersihan Gulma": {"bg": "#8B5CF6", "text": "#FFFFFF"}, # Violet
    "Pemanenan": {"bg": "#EF4444", "text": "#FFFFFF"}, # Red
    "Pemantauan": {"bg": "#F1F5F9", "text": "#475569"}  # Slate Light
}

# =====================================
# CSS AESTHETIC
# =====================================
st.markdown("""
<style>
div[data-testid="column"] { padding: 1px !important; }
div[data-testid="stHorizontalBlock"] { gap: 4px !important; }

div.stButton > button {
    height: 90px;
    border-radius: 8px;
    text-align: center;
    font-size: 12px;
    font-weight: 700;
    white-space: pre-line;
    border: none;
    transition: transform 0.1s ease;
}

div.stButton > button:hover {
    filter: brightness(0.9);
    transform: translateY(-2px);
}
</style>
""", unsafe_allow_html=True)

# =====================================
# TAMPILAN UTAMA
# =====================================
left, right = st.columns([2.6, 1.1])

with left:
    # Header Nama Hari
    header_cols = st.columns(7)
    names = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
    for i, name in enumerate(names):
        header_cols[i].markdown(f"<div style='text-align:center; font-weight:bold; color:#64748B;'>{name}</div>", unsafe_allow_html=True)

    cal = calendar.monthcalendar(year, month)
    today = datetime.today()

    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].write("")
            else:
                hujan = predictions[day-1]
                tgl_obj = datetime(year, month, day)
                hst = (tgl_obj.date() - tanggal_tanam).days

                # Penentuan Label via RBS
                akt_str = rbs_singkong_final(hujan, hst)
                label = label_singkat(akt_str)

                # Ambil Style
                cfg = style_config.get(label, {"bg": "#FFFFFF", "text": "#000000"})
                
                # Highlight hari ini
                is_today = (day == today.day and month == today.month and year == today.year)
                border = "3px solid #000000" if is_today else "none"

                # Label Tombol
                btn_label = f"{day}\n{label.upper()}"

                if cols[i].button(btn_label, key=f"day_{day}", use_container_width=True):
                    st.session_state.selected_day = day

                # Injeksi CSS Warna Blok
                st.markdown(f"""
                    <style>
                    button[key="day_{day}"] {{
                        background-color: {cfg['bg']} !important;
                        color: {cfg['text']} !important;
                        border: {border} !important;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    </style>
                """, unsafe_allow_html=True)

with right:
    # Pastikan index hari aman
    curr_day = min(st.session_state.selected_day, days_in_month)
    
    h_val = predictions[curr_day-1]
    hst_val = (datetime(year, month, curr_day).date() - tanggal_tanam).days
    rekomendasi_full = rbs_singkong_final(h_val, hst_val)

    st.markdown(f"""
    <div style="background:white; padding:20px; border-radius:12px; border:1px solid #E2E8F0;">
        <h3 style="margin-top:0; color:#1E293B;">Informasi Detail</h3>
        <p style="margin:0;"><b>Tanggal:</b> {curr_day} {calendar.month_name[month]} {year}</p>
        <p style="margin:0;"><b>Umur Tanaman:</b> {hst_val} HST</p>
        <hr style="margin:15px 0;">
        <p style="font-size:12px; color:#64748B; margin-bottom:0;">Estimasi Curah Hujan:</p>
        <h2 style="margin-top:0; color:#2563EB;">{h_val:.2f} mm</h2>
        <div style="background:#F8FAFC; padding:12px; border-radius:8px; border-left:4px solid #2563EB; font-size:14px;">
            {rekomendasi_full}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.subheader("Grafik Hujan Bulanan")
    st.line_chart(pd.DataFrame(predictions, columns=["mm"]), color="#3B82F6")
