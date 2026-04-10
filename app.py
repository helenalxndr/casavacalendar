import streamlit as st
import pandas as pd
import numpy as np
import calendar
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# --- SETUP & DATA (Asumsi fungsi loader & rbs sudah benar) ---
if "view_date" not in st.session_state:
    st.session_state.view_date = date(2026, 4, 1)

# --- CSS SUPER AGRESIF ---
# Kita pakai selector yang lebih luas agar pasti kena ke tombolnya
st.markdown("""
<style>
    /* Styling dasar semua tombol kalender */
    .stButton > button {
        height: 100px !important;
        width: 100% !important;
        border-radius: 10px !important;
        border: 2px solid #f0f2f6 !important;
        display: flex !important;
        flex-direction: column !important;
        transition: 0.2s !important;
    }

    /* Warna Hijau: Tanam */
    .tanam-style button { background-color: #d1fae5 !important; border-color: #10b981 !important; }
    
    /* Warna Biru: Siram */
    .siram-style button { background-color: #dbeafe !important; border-color: #3b82f6 !important; }
    
    /* Warna Kuning: Pupuk/Siang (Range Waktu) */
    .pupuk-style button { background-color: #fef3c7 !important; border-color: #f59e0b !important; }
    
    /* Warna Merah: Panen */
    .panen-style button { background-color: #fee2e2 !important; border-color: #ef4444 !important; }

    /* Efek hover agar tetap interaktif */
    .stButton > button:hover { transform: scale(1.02); filter: brightness(0.95); }
    
    /* Legenda Box */
    .legend-item {
        padding: 10px; border-radius: 5px; font-weight: bold; font-size: 12px;
        text-align: center; border: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER & NAVIGASI ---
col_n1, col_n2, col_n3 = st.columns([1, 2, 1])
with col_n1:
    if st.button("❮ Sebelumnya", use_container_width=True):
        st.session_state.view_date -= relativedelta(months=1)
        st.rerun()
with col_n2:
    cv = st.session_state.view_date
    st.markdown(f"<h2 style='text-align:center;'>{calendar.month_name[cv.month]} {cv.year}</h2>", unsafe_allow_html=True)
with col_n3:
    if st.button("Selanjutnya ❯", use_container_width=True):
        st.session_state.view_date += relativedelta(months=1)
        st.rerun()

# --- LEGENDA (PENTING: Edukasi User) ---
st.markdown("### 💡 Panduan Warna")
l1, l2, l3, l4 = st.columns(4)
l1.markdown('<div class="legend-item" style="background-color:#d1fae5">🌱 Penanaman</div>', unsafe_allow_html=True)
l2.markdown('<div class="legend-item" style="background-color:#dbeafe">💧 Penyiraman</div>', unsafe_allow_html=True)
l3.markdown('<div class="legend-item" style="background-color:#fef3c7">⚠️ Rentang Pemupukan</div>', unsafe_allow_html=True)
l4.markdown('<div class="legend-item" style="background-color:#fee2e2">🚜 Panen</div>', unsafe_allow_html=True)

st.caption("*(Warna kuning berarti periode yang disarankan. Anda tidak perlu memupuk setiap hari, cukup pilih hari yang cuacanya pas di dalam rentang tersebut)*")

# --- GRID KALENDER ---
cal_matrix = calendar.monthcalendar(cv.year, cv.month)
days_header = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
h_cols = st.columns(7)
for i, d in enumerate(days_header):
    h_cols[i].markdown(f"<p style='text-align:center; font-weight:bold; color:gray;'>{d}</p>", unsafe_allow_html=True)

# Logic Rendering
tgl_tanam = date(2026, 3, 1) # Contoh tanggal tanam

for week in cal_matrix:
    w_cols = st.columns(7)
    for i, day in enumerate(week):
        if day == 0:
            w_cols[i].write("")
        else:
            # Contoh sederhana penentuan fase (Ganti dengan fungsi rbs_singkong_final Anda)
            curr_date = date(cv.year, cv.month, day)
            hst = (curr_date - tgl_tanam).days
            
            # --- LOGIKA PENENTUAN CLASS ---
            phase_class = ""
            label = "NORMAL"
            
            if 0 <= hst <= 5: 
                phase_class = "tanam-style"; label = "TANAM"
            elif 30 <= hst <= 45: # Range pemupukan (April 2026 jika tanam Maret)
                phase_class = "pupuk-style"; label = "PUPUK"
            elif hst > 270:
                phase_class = "panen-style"; label = "PANEN"
            else:
                phase_class = "siram-style"; label = "SIRAM"

            # --- TRICK: BUNGKUS DENGAN DIV CLASS ---
            with w_cols[i]:
                st.markdown(f'<div class="{phase_class}">', unsafe_allow_html=True)
                if st.button(f"{day}\n{label}", key=f"btn_{day}_{cv.month}"):
                    st.write(f"Klik tanggal {day}")
                st.markdown('</div>', unsafe_allow_html=True)
