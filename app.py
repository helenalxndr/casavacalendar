import streamlit as st
import pandas as pd
import numpy as np
import calendar
from datetime import date
from dateutil.relativedelta import relativedelta

from utils.loader import load_all
from utils.forecast import recursive_forecast
from utils.rbs import rbs_singkong_final, label_singkat, kategori_hujan

st.set_page_config(layout="wide", page_title="Dashboard Tanam Singkong")

# =========================
# LOAD DATA
# =========================
try:
    model, encoder, scaler, data = load_all()
    data["tanggal"] = pd.to_datetime(data["tanggal"])
    data = data.sort_values("tanggal")
except Exception as e:
    st.error(f"Gagal memuat resource: {e}")
    st.stop()

# =========================
# SESSION STATE
# =========================
if "view_date" not in st.session_state:
    st.session_state.view_date = date.today().replace(day=1)

if "selected_day" not in st.session_state:
    st.session_state.selected_day = date.today().day

# =========================
# SIDEBAR
# =========================
st.sidebar.title("⚙️ Pengaturan")

kec_list = sorted(data["kecamatan"].unique())
sel_kecamatan = st.sidebar.selectbox("Pilih Kecamatan", kec_list)

tgl_tanam = st.sidebar.date_input(
    "Tanggal Tanam", value=date.today()
)

# =========================
# PREP DATA
# =========================
kec_id = encoder.transform([sel_kecamatan])[0]
df_kec = data[data["kecamatan"] == sel_kecamatan].copy()

if len(df_kec) < 270:
    st.error("Data historis kurang dari 270 hari")
    st.stop()

rain_last270 = df_kec["rain_mm"].values[-270:]

forecast_30 = recursive_forecast(
    model=model,
    scaler=scaler,
    rain_last270=rain_last270,
    kec_id=kec_id,
    days=31
)

# Hindari nilai negatif
forecast_30 = np.clip(forecast_30, 0, 300)

# =========================
# WARNA AKTIVITAS
# =========================
def warna_aktivitas(label):

    if label == "Penanaman":
        return "#22c55e"
    if label == "Pemupukan":
        return "#3b82f6"
    if label == "Penyiraman":
        return "#06b6d4"
    if label == "Pembersihan Gulma":
        return "#eab308"
    if label == "Pemanenan":
        return "#f97316"
    if label == "Tunda Tanam":
        return "#ef4444"

    return "#9ca3af"

# =========================
# LAYOUT
# =========================
col1, col2 = st.columns([3, 1])

with col1:

    # NAVIGASI BULAN
    n1, n2, n3 = st.columns([1, 2, 1])

    with n1:
        if st.button("❮ Sebelumnya"):
            st.session_state.view_date -= relativedelta(months=1)
            st.rerun()

    with n2:
        cv = st.session_state.view_date
        st.markdown(
            f"<h3 style='text-align:center'>{calendar.month_name[cv.month]} {cv.year}</h3>",
            unsafe_allow_html=True
        )

    with n3:
        if st.button("Selanjutnya ❯"):
            st.session_state.view_date += relativedelta(months=1)
            st.rerun()

    # HEADER HARI
    headers = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
    cols = st.columns(7)
    for i, h in enumerate(headers):
        cols[i].markdown(f"<b>{h}</b>", unsafe_allow_html=True)

    # KALENDER
    cal_matrix = calendar.monthcalendar(cv.year, cv.month)

    for week in cal_matrix:
        w_cols = st.columns(7)

        for i, day in enumerate(week):
            if day == 0:
                w_cols[i].write("")
                continue

            curr_dt = date(cv.year, cv.month, day)
            hst = (curr_dt - tgl_tanam).days

            idx = min(max(0, (curr_dt - tgl_tanam).days), len(forecast_30) - 1)
            hujan_val = forecast_30[idx]

            rekom = rbs_singkong_final(hujan_val, hst)
            label = label_singkat(rekom)

            warna = warna_aktivitas(label)

            # BUTTON CLICK AREA
            if w_cols[i].button(" ", key=f"day_{cv.month}_{day}"):
                st.session_state.selected_day = day
                st.rerun()

            # BOX VISUAL
            w_cols[i].markdown(
                f"""
                <div style="
                    height:100px;
                    border-radius:10px;
                    border:2px solid {warna};
                    background-color:{warna}20;
                    display:flex;
                    flex-direction:column;
                    align-items:center;
                    justify-content:center;
                    text-align:center;
                ">
                    <div style="font-size:18px;font-weight:bold;">{day}</div>
                    <div style="font-size:10px;">{label}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # =========================
    # LEGENDA
    # =========================
    st.markdown("### 🎨 Keterangan Warna")
    st.markdown("""
    - 🟢 Penanaman → Waktu optimal tanam (range)
    - 🔵 Pemupukan → Rentang ideal pemupukan
    - 🔷 Penyiraman → Perlu tambahan air
    - 🟡 Penyiangan → Risiko gulma
    - 🟠 Panen → Waktu panen terbaik
    - 🔴 Tunda → Tidak disarankan
    """)

# =========================
# DETAIL PANEL
# =========================
with col2:
    st.markdown("### 📋 Detail Hari")

    sd = st.session_state.selected_day

    try:
        active_dt = date(cv.year, cv.month, sd)
    except:
        active_dt = date(cv.year, cv.month, 1)

    hst_active = (active_dt - tgl_tanam).days
    idx = min(max(0, hst_active), len(forecast_30) - 1)
    hujan = forecast_30[idx]

    kategori = kategori_hujan(hujan)
    rekom = rbs_singkong_final(hujan, hst_active)

    st.info(
        f"""
        **Tanggal:** {active_dt.strftime('%d %B %Y')}

        **HST:** {hst_active} hari  
        **Curah Hujan:** {hujan:.2f} mm  
        **Kategori:** {kategori}
        """
    )

    st.success(rekom)

    st.divider()

    df_chart = pd.DataFrame({
        "Hari": range(len(forecast_30)),
        "Curah Hujan": forecast_30
    })

    st.line_chart(df_chart)
