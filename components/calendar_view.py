import streamlit as st
import calendar
from datetime import date
from dateutil.relativedelta import relativedelta
from utils.rbs import rbs_singkong_final, label_singkat

def get_color(label):
    label = label.upper()

    if "TANAM" in label:
        return "#bbf7d0", "#22c55e"
    elif "SIRAM" in label:
        return "#bae6fd", "#0ea5e9"
    elif "PUPUK" in label or "GULMA" in label:
        return "#fef08a", "#eab308"
    elif "PANEN" in label:
        return "#fecaca", "#ef4444"

    return "#f3f4f6", "#d1d5db"


def render_calendar(cv, tgl_tanam, forecast_30):
    selected_day = None

    # =========================
    # NAVIGASI BULAN
    # =========================
    n1, n2, n3 = st.columns([1,2,1])

    with n1:
        if st.button("❮ Sebelumnya"):
            st.session_state.view_date = cv - relativedelta(months=1)
            st.rerun()

    with n2:
        st.markdown(f"<h3 style='text-align:center'>{calendar.month_name[cv.month]} {cv.year}</h3>", unsafe_allow_html=True)

    with n3:
        if st.button("Selanjutnya ❯"):
            st.session_state.view_date = cv + relativedelta(months=1)
            st.rerun()

    st.write("")

    # =========================
    # HEADER HARI
    # =========================
    h_cols = st.columns(7)
    for i, h in enumerate(["Sen","Sel","Rab","Kam","Jum","Sab","Min"]):
        h_cols[i].markdown(f"<p style='text-align:center;font-weight:bold'>{h}</p>", unsafe_allow_html=True)

    # =========================
    # PREPARE CSS DINAMIS
    # =========================
    cal_matrix = calendar.monthcalendar(cv.year, cv.month)
    css_rules = []

    for week in cal_matrix:
        for day in week:
            if day == 0:
                continue

            curr_dt = date(cv.year, cv.month, day)
            hst = (curr_dt - tgl_tanam).days
            idx = min(max(0, day-1), len(forecast_30)-1)

            label = label_singkat(
                rbs_singkong_final(forecast_30[idx], hst)
            )

            bg, border = get_color(label)

            key = f"day_{cv.month}_{day}"

            css_rules.append(f"""
            button[key="{key}"] {{
                background-color: {bg} !important;
                border: 2px solid {border} !important;
                height: 105px !important;
                width: 100% !important;
                border-radius: 10px !important;
                font-size: 18px !important;
                font-weight: bold !important;
                color: black !important;
            }}
            """)

    # INJECT CSS
    st.markdown(f"<style>{''.join(css_rules)}</style>", unsafe_allow_html=True)

    # =========================
    # GRID KALENDER (FULL CLICKABLE)
    # =========================
    for week in cal_matrix:
        cols = st.columns(7)

        for i, day in enumerate(week):
            if day == 0:
                cols[i].write("")
                continue

            key = f"day_{cv.month}_{day}"

            if cols[i].button(str(day), key=key, use_container_width=True):
                selected_day = day

    return selected_day
