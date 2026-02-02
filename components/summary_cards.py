import streamlit as st

def render_summary(df):
    st.markdown("---")
    st.subheader("Ringkasan Bulanan")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Hari Tanam", (df["Aktivitas"] == "Penanaman").sum())
    c2.metric("Hari Pupuk", df["Aktivitas"].str.contains("Pemupukan").sum())
    c3.metric("Hari Hama", df["Aktivitas"].str.contains("Hama").sum())
    c4.metric("Hari Panen", (df["Aktivitas"] == "Panen").sum())
