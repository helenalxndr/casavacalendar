import streamlit as st

def load_css():
    st.markdown("""
    <style>
    div.stButton > button {
        height: 105px !important;
        width: 100% !important;
        border-radius: 10px !important;
        border: 2px solid #e5e7eb !important;
        background-color: white !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 18px !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)
