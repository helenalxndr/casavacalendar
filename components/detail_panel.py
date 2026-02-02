import streamlit as st
import pandas as pd

def render_detail_panel(df_dashboard, calendar_state):
    st.subheader("📌 Detail Aktivitas")

    if not calendar_state:
        st.info("Klik tanggal atau aktivitas di kalender.")
        return

    st.write("DEBUG callback:", calendar_state.get("callback"))

    selected_date = None
    callback = calendar_state.get("callback")

    if callback == "eventClick":
        selected_date = pd.to_datetime(
            calendar_state["eventClick"]["event"]["start"]
        ).date()

    elif callback == "dateClick":
        selected_date = pd.to_datetime(
            calendar_state["dateClick"]["date"]
        ).date()

    elif callback == "select":
        selected_date = (
            pd.to_datetime(calendar_state["select"]["start"], utc=True)
            .tz_convert("Asia/Jakarta")
            .date()
        )

    if not selected_date:
        st.warning("Tanggal tidak terdeteksi dari kalender.")
        return

    data_hari = df_dashboard[
        df_dashboard["Tanggal"].dt.date == selected_date
    ]

    if data_hari.empty:
        st.warning(f"Tidak ada data aktivitas untuk {selected_date}")
        return

    row = data_hari.iloc[0]

    st.markdown(f"""
    **🗓️ Tanggal:** {row['Tanggal'].strftime('%d %B %Y')}  
    **🌧️ Prediksi Hujan:** {row['Prediksi Hujan (mm)']:.2f} mm  
    **🌱 HST:** {row['HST']}  
    **📋 Aktivitas:** **{row['Aktivitas']}**
    """)
