import streamlit as st
from datetime import date
from utils.rbs import rbs_singkong_final

def render_detail(cv, selected_day, tgl_tanam, forecast_30):
    st.markdown("### 📋 Detail Hari")

    if selected_day is None:
        selected_day = 1

    active_dt = date(cv.year, cv.month, selected_day)

    hst = (active_dt - tgl_tanam).days
    idx = min(max(0, selected_day-1), len(forecast_30)-1)
    hujan = forecast_30[idx]

    rekom = rbs_singkong_final(hujan, hst)

    st.info(f"""
    **Tanggal:** {active_dt.strftime('%d %B %Y')}

    **HST:** {hst} hari  
    **Hujan:** {hujan:.2f} mm  
    """)

    st.success(rekom)
    st.line_chart(forecast_30)
