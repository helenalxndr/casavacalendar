import streamlit as st
import pandas as pd
import numpy as np
import calendar
from datetime import datetime
from utils.loader import load_all
from utils.forecast import recursive_forecast

st.set_page_config(layout="wide", page_title="Kalender Tanam Pintar")

# =========================
# LOAD DATA
# =========================
model, encoder, scaler, data = load_all()
data["tanggal"] = pd.to_datetime(data["tanggal"])

# =========================
# SESSION STATE
# =========================
# Inisialisasi state hari yang dipilih agar tidak error
if "selected_day" not in st.session_state:
    st.session_state.selected_day = datetime.today().day

# =========================
# SIDEBAR
# =========================
st.sidebar.title("⚙ Pengaturan")

kecamatan_list = sorted(data["kecamatan"].unique())
selected_kecamatan = st.sidebar.selectbox("Pilih Kecamatan", kecamatan_list)

tanggal_tanam = st.sidebar.date_input("Tanggal Tanam", value=datetime.today())

# =========================
# FILTER DATA & FORECAST
# =========================
kec_id = encoder.transform([selected_kecamatan])[0]
df_kec = data[data["kecamatan"] == selected_kecamatan].copy().sort_values("tanggal")
rain_last270 = df_kec["rain_mm"].values[-270:]

# Prediksi 30 hari ke depan
forecast_30 = recursive_forecast(
    model=model,
    scaler=scaler,
    rain_last270=rain_last270,
    kec_id=kec_id,
    days=30
)

# =========================
# CSS UNTUK CUSTOM BUTTON (KALENDER)
# =========================
st.markdown("""
<style>
/* Membuat tombol native Streamlit berbentuk kotak seperti Day Card */
div.stButton > button {
    height: 100px;
    width: 100%;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    background-color: white;
    color: #1f2937;
    transition: all 0.2s ease;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: flex-start;
    padding: 10px;
    text-align: left;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

/* Hover effect */
div.stButton > button:hover {
    border-color: #2563eb;
    background-color: #f9fafb;
    transform: translateY(-2px);
}

/* Style saat tombol aktif/terpilih */
div.stButton > button:focus, div.stButton > button:active {
    border: 2px solid #2563eb !important;
    background-color: #eff6ff !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2);
}

/* Styling teks di dalam tombol */
.btn-date {
    font-size: 16px;
    font-weight: bold;
}
.btn-label {
    font-size: 11px;
    margin-top: 4px;
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: 600;
}
.lbl-pemantauan { background-color: #e0f2fe; color: #0369a1; }
.lbl-pemupukan { background-color: #ede9fe; color: #6d28d9; }
.lbl-panen { background-color: #dcfce7; color: #166534; }
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

    st.markdown(f"<h2 style='text-align:center; margin-bottom:20px;'>{calendar.month_name[month]} {year}</h2>", unsafe_allow_html=True)

    # Header Nama Hari (7 Kolom)
    cols_header = st.columns(7)
    nama_hari = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
    for i, nh in enumerate(nama_hari):
        cols_header[i].markdown(f"<p style='text-align:center; font-weight:bold; color:#6b7280;'>{nh}</p>", unsafe_allow_html=True)

    # Ambil struktur minggu dari calendar
    cal = calendar.monthcalendar(year, month)

    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].write("") # Kotak kosong di luar bulan
            else:
                # Logika HST & Label
                current_date = datetime(year, month, day).date()
                hst = (current_date - tanggal_tanam).days
                
                label_html = ""
                label_class = ""
                
                if hst >= 0:
                    if hst < 5:
                        label_html = "🌱 Pantau"
                        label_class = "lbl-pemantauan"
                    elif hst < 90:
                        label_html = "💊 Pupuk"
                        label_class = "lbl-pemupukan"
                    else:
                        label_html = "🌾 Panen"
                        label_class = "lbl-panen"

                # Render tombol sebagai kotak kalender
                # Menggunakan st.markdown di dalam tombol tidak bisa, maka kita pakai teks biasa
                # Tapi kita beri gaya melalui CSS global di atas
                button_content = f"{day}\n{label_html}"
                
                if cols[i].button(button_content, key=f"day_btn_{day}", use_container_width=True):
                    st.session_state.selected_day = day
                    st.rerun()

# =========================
# DETAIL PANEL (KOLOM KANAN)
# =========================
with col2:
    selected_day = st.session_state.selected_day
    
    # Proteksi error tanggal
    try:
        selected_date = datetime(year, month, selected_day).date()
    except:
        selected_day = 1
        selected_date = datetime(year, month, selected_day).date()

    hst = (selected_date - tanggal_tanam).days
    
    # Ambil index prediksi (asumsi forecast_30 adalah list/array 30 hari)
    idx = min(max(0, selected_day - 1), len(forecast_30) - 1)
    rain_pred = forecast_30[idx]

    st.markdown("### 📋 Detail Rekomendasi")
    st.markdown(f"""
    **Tanggal:** {selected_date.strftime('%d %B %Y')}  
    **Usia Tanaman:** {hst} Hari Setelah Tanam (HST)  
    **Prediksi Curah Hujan:** `{rain_pred:.2f} mm`
    """)

    if hst < 0:
        st.info("Belum memasuki masa tanam.")
    elif hst < 5:
        st.info("💡 **Fase Pemantauan**: Pastikan kelembapan tanah terjaga untuk tunas baru.")
    elif hst < 90:
        st.success("✅ **Fase Pemupukan**: Kondisi vegetatif aktif. Lakukan pemupukan sesuai dosis.")
    else:
        st.warning("⚠️ **Fase Panen**: Perhatikan cuaca saat melakukan pemanenan agar kualitas terjaga.")

    st.markdown("---")
    st.markdown("**Tren Curah Hujan (30 Hari)**")
    # Menampilkan chart tren hujan
    chart_data = pd.DataFrame(forecast_30, columns=["Hujan (mm)"])
    st.line_chart(chart_data)
