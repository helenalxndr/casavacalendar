
import streamlit as st

def render_header(df):
    st.markdown("## 🌱 Kalender Tanam Singkong")
    st.caption(
        "Rekomendasi aktivitas pertanian berbasis prediksi hujan harian (LSTM)."
    )

    c1, c2 = st.columns([2, 1])

    with c1:
        kecamatan = st.selectbox(
            "📍 Kecamatan",
            sorted(df["kecamatan"].unique())
        )

    with c2:
        tanggal = st.date_input(
            "🗓️ Bulan Kalender",
            value=st.session_state.get("tanggal_acuan")
        )

    return kecamatan, tanggal
