import streamlit as st
from datetime import date
from utils.rbs import rbs_singkong_final


def render_detail(cv, selected_day, tgl_tanam, forecast_30):

    st.markdown("### 📋 Detail Hari")

    # =========================
    # FIX ERROR (WAJIB)
    # =========================
    if selected_day is None:
        selected_day = st.session_state.get("selected_day", 1)

    # simpan ke session
    st.session_state.selected_day = selected_day

    # =========================
    # SAFE DATE
    # =========================
    try:
        active_dt = date(cv.year, cv.month, selected_day)
    except:
        active_dt = date(cv.year, cv.month, 1)
        selected_day = 1

    # =========================
    # HITUNG DATA
    # =========================
    hst = (active_dt - tgl_tanam).days
    idx = min(max(0, selected_day - 1), len(forecast_30) - 1)
    hujan = forecast_30[idx]

    rekom = rbs_singkong_final(hujan, hst)

    # =========================
    # TAMPILKAN
    # =========================
    st.info(f"""
    **Tanggal:** {active_dt.strftime('%d %B %Y')}

    **HST:** {hst} hari  
    **Curah Hujan:** {hujan:.2f} mm  
    """)

    st.success(rekom)

    st.divider()
    st.line_chart(forecast_30)
