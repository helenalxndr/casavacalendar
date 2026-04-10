import streamlit as st
import pandas as pd
import numpy as np
import calendar
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# --- SETUP DATA (Asumsi import utils sudah benar di kode lo) ---
if "view_date" not in st.session_state:
    st.session_state.view_date = date(2026, 4, 1) # Menyesuaikan screenshot

# ==========================================
# JURUS PAMUNGKAS CSS (SUPER AGRESIF & SPESIFIK)
# ==========================================
st.markdown("""
<style>
    /* Styling Dasar Button agar konsisten putih di awal */
    div.stButton > button {
        height: 105px !important;
        width: 100% !important;
        border-radius: 10px !important;
        border: 1px solid #e2e8f0 !important;
        background-color: white !important;
        transition: all 0.2s ease !important;
    }

    /* Ukuran Font Tanggal & Label */
    div.stButton > button p { font-size: 20px !important; font-weight: 800 !important; margin: 0 !important; }
    div.stButton > button div { font-size: 9px !important; font-weight: 700 !important; color: #4b5563 !important; }

    /* DEFINISI WARNA FASE */
    .fase-tanam button { background-color: #C6F6D5 !important; border-color: #48BB78 !important; }
    .fase-siram button { background-color: #BEE3F8 !important; border-color: #4299E1 !important; }
    .fase-pupuk button { background-color: #FEF3C7 !important; border-color: #F6E05E !important; } /* Kuning Range */
    .fase-panen button { background-color: #FED7D7 !important; border-color: #F56565 !important; }

    /* Legend Box styling */
    .legend-card {
        padding: 12px; border-radius: 8px; text-align: center; font-size: 13px; font-weight: 600;
        border: 1px solid #CBD5E0; margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# MAIN LAYOUT
# ==========================================
col1, col2 = st.columns([3, 1])

with col1:
    # --- NAVIGASI BULAN (Gue skip agar hemat baris) ---
    cv = st.session_state.view_date
    st.markdown(f"<h2 style='text-align:center;'>{calendar.month_name[cv.month]} {cv.year}</h2>", unsafe_allow_html=True)

    # --- LEGENDA (Solusi Edukasi) ---
    st.write("")
    l1, l2, l3, l4 = st.columns(4)
    l1.markdown('<div class="legend-card" style="background-color:#C6F6D5">🌱 Tanam</div>', unsafe_allow_html=True)
    l2.markdown('<div class="legend-card" style="background-color:#BEE3F8">💧 Siram</div>', unsafe_allow_html=True)
    l3.markdown('<div class="legend-card" style="background-color:#FEF3C7">🧪 Rentang Pupuk</div>', unsafe_allow_html=True)
    l4.markdown('<div class="legend-card" style="background-color:#FED7D7">🚜 Panen</div>', unsafe_allow_html=True)
    
    st.caption("ℹ️ **Tips:** Warna kuning (Rentang Pupuk) berarti periode yang aman. Anda cukup memilih salah satu hari di rentang tersebut untuk pemupukan (tidak perlu setiap hari).")

    # --- GRID KALENDER ---
    h_cols = st.columns(7)
    for i, h in enumerate(["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]):
        h_cols[i].markdown(f"<p style='text-align:center; color:gray; font-size:12px;'>{h}</p>", unsafe_allow_html=True)

    cal_matrix = calendar.monthcalendar(cv.year, cv.month)
    
    # Asumsi data tanam & forecast (Sesuaikan dengan fungsi asli lo)
    tgl_tanam = date(2026, 3, 1)
    
    for week in cal_matrix:
        w_cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                w_cols[i].write("")
            else:
                curr_dt = date(cv.year, cv.month, day)
                hst = (curr_dt - tgl_tanam).days
                
                # --- LOGIKA PENENTUAN CLASS ---
                # Ganti ini dengan label_singkat(rbs_singkong_final(...)) lo
                label_txt = "NORMAL"
                phase_class = "phase-default"

                if hst <= 5: 
                    label_txt = "TANAM"; phase_class = "fase-tanam"
                elif 30 <= hst <= 55: # April 2026 (Range Kuning)
                    label_txt = "PUPUKAN"; phase_class = "fase-pupuk"
                elif hst > 270:
                    label_txt = "PANEN"; phase_class = "fase-panen"
                else:
                    label_txt = "SIRAM"; phase_class = "fase-siram"

                # --- TRICK: BUNGKUS DENGAN DIV CLASS ---
                with w_cols[i]:
                    st.markdown(f'<div class="{phase_class}">', unsafe_allow_html=True)
                    if st.button(f"{day}\n{label_txt}", key=f"btn_{day}_{cv.month}"):
                        st.session_state.selected_day = day
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
