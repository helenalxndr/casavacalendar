import streamlit as st
import calendar
from datetime import datetime
import pandas as pd
import numpy as np

from utils.loader import load_all
from utils.forecast import recursive_forecast
from utils.rbs import rbs_singkong_final, label_singkat

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Dashboard Kalender Tanam Singkong",
    layout="wide"
)

# =========================================================
# LOAD MODEL & DATA
# =========================================================
@st.cache_resource
def init():
    # Pastikan utils.loader sudah menggunakan load_model(..., compile=False)
    return load_all()

model, encoder, scaler, data = init()

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("⚙ Pengaturan")

kecamatan = st.sidebar.selectbox("Pilih Kecamatan", encoder.classes_)
tanggal_tanam = st.sidebar.date_input(
    "Tanggal Tanam",
    value=datetime.today()
)

kec_id = encoder.transform([kecamatan])[0]

# =========================================================
# DATA PREPARATION
# =========================================================
data["tanggal"] = pd.to_datetime(data["tanggal"])
df_kec = data[data["kecamatan"] == kecamatan].sort_values("tanggal")

# Mengambil data historis terakhir untuk input model
rain_last270 = df_kec["rain_mm"].values[-270:]
forecast = recursive_forecast(model, scaler, rain_last270, kec_id, days=31)

# =========================================================
# NAVIGASI BULAN
# =========================================================
if "month" not in st.session_state:
    st.session_state.month = datetime.today().month

if "year" not in st.session_state:
    st.session_state.year = datetime.today().year

if "selected_day" not in st.session_state:
    st.session_state.selected_day = datetime.today().day

col_prev, col_title, col_next = st.columns([1,6,1])

with col_prev:
    if st.button("◀", key="prev_btn"):
        if st.session_state.month == 1:
            st.session_state.month = 12
            st.session_state.year -= 1
        else:
            st.session_state.month -= 1

with col_next:
    if st.button("▶", key="next_btn"):
        if st.session_state.month == 12:
            st.session_state.month = 1
            st.session_state.year += 1
        else:
            st.session_state.month += 1

month = st.session_state.month
year = st.session_state.year

with col_title:
    st.markdown(
        f"<h2 style='text-align:center; margin-bottom:0;'>{calendar.month_name[month]} {year}</h2>",
        unsafe_allow_html=True
    )

days_in_month = calendar.monthrange(year, month)[1]
# Prediksi hujan disesuaikan dengan jumlah hari dalam bulan terpilih
predictions = forecast[:days_in_month]

# =========================================================
# COLOR MAP PROFESSIONAL
# =========================================================
color_map = {
    "Penanaman": "#2E7D32",         # Hijau
    "Pemupukan": "#EF6C00",         # Oranye
    "Penyiraman": "#1565C0",        # Biru
    "Pembersihan Gulma": "#6A1B9A", # Ungu
    "Pemanenan": "#C62828",         # Merah
    "Pemantauan": "#455A64"         # Abu-abu
}

# =========================================================
# CUSTOM CSS (COMPACT & HIGH CONTRAST)
# =========================================================
st.markdown("""
<style>
/* Merapatkan Grid Kalender */
div[data-testid="column"] {
    padding: 1px !important;
    margin: 0px !important;
}

div[data-testid="stHorizontalBlock"] {
    gap: 2px !important;
}

/* Styling Tombol Kalender */
div.stButton > button {
    height: 75px;
    border-radius: 8px;
    border: 1px solid rgba(0,0,0,0.05);
    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    transition: 0.1s;
    padding: 4px !important;
}

/* Membedakan Warna Angka Tanggal dan Label Aktivitas */
div.stButton > button p {
    line-height: 1.1 !important;
}

/* Ukuran Angka Tanggal */
div.stButton > button::first-line {
    font-size: 16px !important;
    font-weight: bold !important;
    color: #FFFFFF !important;
}

div.stButton > button:hover {
    filter: brightness(1.1);
    transform: translateY(-1px);
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# LAYOUT UTAMA
# =========================================================
left, right = st.columns([2.5, 1.2])

# =========================================================
# CALENDAR GRID (Sisi Kiri)
# =========================================================
with left:
    # Header Hari
    cols_header = st.columns(7)
    days_abbr = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
    for i, d in enumerate(days_abbr):
        color_text = "#C62828" if i >= 5 else "#333" # Merah untuk weekend
        cols_header[i].markdown(f"<center><b style='color:{color_text}'>{d}</b></center>", unsafe_allow_html=True)

    cal = calendar.monthcalendar(year, month)
    
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].empty()
            else:
                hujan = predictions[day-1]
                tanggal_prediksi = datetime(year, month, day)
                hst = (tanggal_prediksi.date() - tanggal_tanam).days
                
                # Mendapatkan rekomendasi RBS
                aktivitas_full = rbs_singkong_final(hujan, hst)
                label = label_singkat(aktivitas_full)
                
                bg_color = color_map.get(label, "#546E7A")
                
                # Warna teks label (Kuning cerah agar kontras dengan background gelap)
                text_label_color = "#FFEB3B" if label != "Pemantauan" else "#CFD8DC"

                # Label tombol: Baris 1 Angka, Baris 2 Aktivitas
                button_display = f"{day}\n{label}"

                if cols[i].button(button_display, key=f"day_{day}", use_container_width=True):
                    st.session_state.selected_day = day

                # CSS Injeksi per Tombol untuk Warna Dinamis
                st.markdown(f"""
                <style>
                button[key="day_{day}"] {{
                    background-color: {bg_color} !important;
                    color: white !important;
                }}
                /* Memberikan warna khusus pada teks aktivitas di bawah angka */
                button[key="day_{day}"] span {{
                    display: block;
                }}
                button[key="day_{day}"] p {{
                    color: {text_label_color} !important;
                    font-size: 10px !important;
                    font-weight: 600;
                }}
                </style>
                """, unsafe_allow_html=True)

# =========================================================
# DETAIL PANEL (Sisi Kanan)
# =========================================================
with right:
    selected_day = st.session_state.selected_day
    # Pastikan day tidak out of range jika bulan berganti
    selected_day = min(selected_day, days_in_month)
    
    hujan_sel = predictions[selected_day-1]
    tgl_sel = datetime(year, month, selected_day)
    hst_sel = (tgl_sel.date() - tanggal_tanam).days
    akt_full = rbs_singkong_final(hujan_sel, hst_sel)

    st.markdown(f"""
    <div style="background:#f8f9fa; padding:20px; border-radius:15px; border-left:5px solid #2E7D32">
        <h3 style="margin-top:0">📋 Detail Rekomendasi</h3>
        <p><b>📅 Tanggal:</b> {selected_day} {calendar.month_name[month]} {year}</p>
        <p><b>🌱 HST:</b> {hst_sel} Hari</p>
        <hr>
        <p style="font-size:0.9rem; color:#555;">Prediksi Hujan:</p>
        <h2 style="color:#1565C0; margin-top:0;">{hujan_sel:.2f} <span style="font-size:15px">mm</span></h2>
    </div>
    """, unsafe_allow_html=True)

    st.success(f"**Saran:** {akt_full}")

    st.divider()

    st.subheader("📈 Tren Hujan 30 Hari")
    df_chart = pd.DataFrame({
        "Hari": list(range(1, days_in_month+1)),
        "Hujan": predictions
    }).set_index("Hari")
    st.area_chart(df_chart, color="#1565C0")
