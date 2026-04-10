import streamlit as st

def render_sidebar(data, encoder):
    st.sidebar.title("⚙️ Pengaturan")

    kec_list = sorted(data["kecamatan"].unique())
    sel_kecamatan = st.sidebar.selectbox("Pilih Kecamatan", kec_list)

    tgl_tanam = st.sidebar.date_input("Tanggal Tanam")

    kec_id = encoder.transform([sel_kecamatan])[0]

    return sel_kecamatan, kec_id, tgl_tanam
