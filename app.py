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

# Aman rename kolom agar sinkron dengan sisa kode
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
# FILTER DATA & FORECASTING
# =====================================================
df_kec = data[data["kecamatan"] == kecamatan].sort_values("tanggal")

if len(df_kec) < 270:
    st.error("Data historis kurang dari 270 hari.")
    st.stop()

rain_last270 = df_kec["rain_mm"].values[-270:]
forecast = recursive_forecast(model, scaler, rain_last270, kec_id, days=31)

# =====================================================
# STATE BULAN & SELEKSI
# =====================================================
if "month" not in st.session_state:
    st.session_state.month = datetime.today().month

if "year" not in st.session_state:
    st.session_state.year = datetime.today().year

if "selected_day" not in st.session_state:
    st.session_state.selected_day = datetime.today().day

# =====================================================
# NAVIGASI KALENDER
# =====================================================
col1, col2, col3 = st.columns([1,6,1])

with col1:
    if st.button("◀", key="prev"):
        if st.session_state.month == 1:
            st.session_state.month = 12
            st.session_state.year -= 1
        else:
            st.session_state.month -= 1

with col3:
    if st.button("▶", key="next"):
        if st.session_state.month == 12:
            st.session_state.month = 1
            st.session_state.year += 1
        else:
            st.session_state.month += 1

month = st.session_state.month
year = st.session_state.year

with col2:
    st.markdown(
        f"<h2 style='text-align:center;color:#1F2937; margin-bottom:0;'>"
        f"{calendar.month_name[month]} {year}</h2>",
        unsafe_allow_html=True
    )

days_in_month = calendar.monthrange(year, month)[1]
predictions = forecast[:days_in_month]

# =====================================================
# COLOR MAP UNTUK BLOK & TEKS
# =====================================================
label_info = {
    "Penanaman": {"emoji": "🌱", "bg": "#D1FAE5", "text": "#065F46"}, # Hijau
    "Pemupukan": {"emoji": "🧪", "bg": "#FFEDD5", "text": "#9A3412"}, # Oranye
    "Penyiraman": {"emoji": "💧", "bg": "#DBEAFE", "text": "#1E40AF"}, # Biru
    "Pembersihan Gulma": {"emoji": "🌾", "bg": "#F3E8FF", "text": "#6B21A8"}, # Ungu
    "Pemanenan": {"emoji": "🌽", "bg": "#FEE2E2", "text": "#991B1B"}, # Merah
    "Pemantauan": {"emoji": "🔍", "bg": "#F1F5F9", "text": "#475569"}  # Abu
}

# =====================================================
# CSS AESTHETIC (STRUKTUR DASAR)
# =====================================================
st.markdown("""
<style>
.main { background-color:#F8FAFC; }
div[data-testid="column"] { padding:2px !important; }
div[data-testid="stHorizontalBlock"] { gap:6px !important; }

div.stButton > button {
    height:95px;
    border-radius:12px;
    text-align:left;
    padding:10px;
    font-size:13px;
    font-weight:600;
    white-space:pre-line;
    transition:all 0.2s ease;
    border: 1px solid #E5E7EB;
}
div.stButton > button:hover {
    filter: brightness(0.95);
    transform: scale(1.02);
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# LAYOUT UTAMA
# =====================================================
left, right = st.columns([2.5,1])

# =====================================================
# KALENDER (GRID & DYNAMIC STYLING)
# =====================================================
with left:
    # Header Hari
    header = st.columns(7)
    for i, d in enumerate(["Sen","Sel","Rab","Kam","Jum","Sab","Min"]):
        header[i].markdown(
            f"<div style='text-align:center;font-size:13px;color:#6B7280;font-weight:bold;'>{d}</div>",
            unsafe_allow_html=True
        )

    cal = calendar.monthcalendar(year, month)
    today = datetime.today()

    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].markdown("<div style='height:95px;'></div>", unsafe_allow_html=True)
            else:
                hujan = predictions[day-1]
                tgl_pred = datetime(year, month, day)
                hst = (tgl_pred.date() - tanggal_tanam).days

                # Logika RBS
                aktivitas = rbs_singkong_final(hujan, hst)
                label = label_singkat(aktivitas)

                # Ambil styling berdasarkan label
                style = label_info.get(label, {"emoji": "•", "bg": "#FFFFFF", "text": "#1F2937"})
                
                # Highlight jika hari ini
                is_today = (day == today.day and month == today.month and year == today.year)
                border_style = "2px solid #10B981" if is_today else f"1px solid {style['text']}30"

                button_text = f"{day} {style['emoji']}\n{label}"

                # Render Tombol
                if cols[i].button(button_text, key=f"day_{day}", use_container_width=True):
                    st.session_state.selected_day = day

                # INJEKSI WARNA BLOK (Hanya untuk tombol ini)
                st.markdown(f"""
                    <style>
                    button[key="day_{day}"] {{
                        background-color: {style['bg']} !important;
                        color: {style['text']} !important;
                        border: {border_style} !important;
                    }}
                    </style>
                """, unsafe_allow_html=True)

# =====================================================
# DETAIL PANEL (SISI KANAN)
# =====================================================
with right:
    # Proteksi jika hari terpilih melebihi jumlah hari di bulan baru
    sel_day = min(st.session_state.selected_day, days_in_month)
    
    hujan_val = predictions[sel_day-1]
    tgl_sel = datetime(year, month, sel_day)
    hst_sel = (tgl_sel.date() - tanggal_tanam).days
    akt_full = rbs_singkong_final(hujan_val, hst_sel)

    st.markdown(f"""
    <div style="background:white; padding:15px; border-radius:12px; border:1px solid #E5E7EB;">
        <h4 style="margin-top:0; color:#1F2937;">📋 Rekomendasi</h4>
        <p style="margin-bottom:5px; font-size:14px;"><b>Tanggal:</b> {sel_day} {calendar.month_name[month]}</p>
        <p style="margin-bottom:5px; font-size:14px;"><b>HST:</b> {hst_sel} hari</p>
        <hr style="margin:10px 0;">
        <p style="font-size:12px; color:#6B7280; margin-bottom:0;">Prediksi Hujan:</p>
        <h3 style="margin-top:0; color:#2563EB;">{hujan_val:.2f} mm</h3>
        <div style="background:#F1F5F9; padding:10px; border-radius:8px; font-size:13px; color:#374151;">
            {akt_full}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.subheader("📊 Grafik Hujan")
    df_chart = pd.DataFrame({
        "Hari": list(range(1, days_in_month+1)),
        "Curah Hujan (mm)": predictions
    })
    st.line_chart(df_chart.set_index("Hari"))
