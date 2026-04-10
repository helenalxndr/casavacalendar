import streamlit as st
import calendar
from datetime import date
from dateutil.relativedelta import relativedelta
from utils.rbs import rbs_singkong_final, label_singkat


# =========================
# WARNA BERDASARKAN LABEL
# =========================
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


# =========================
# GROUP RANGE (INTI LOGIC)
# =========================
def group_ranges(labels):
    ranges = []
    start = 0

    for i in range(1, len(labels)):
        if labels[i] != labels[start]:
            ranges.append((start, i - 1, labels[start]))
            start = i

    ranges.append((start, len(labels) - 1, labels[start]))
    return ranges


# =========================
# MAIN CALENDAR
# =========================
def render_calendar(cv, tgl_tanam, forecast_30):

    selected_day = None

    # =========================
    # NAVIGASI BULAN
    # =========================
    n1, n2, n3 = st.columns([1, 2, 1])

    with n1:
        if st.button("❮ Sebelumnya"):
            st.session_state.view_date = cv - relativedelta(months=1)
            st.rerun()

    with n2:
        st.markdown(
            f"<h3 style='text-align:center'>{calendar.month_name[cv.month]} {cv.year}</h3>",
            unsafe_allow_html=True
        )

    with n3:
        if st.button("Selanjutnya ❯"):
            st.session_state.view_date = cv + relativedelta(months=1)
            st.rerun()

    st.write("")

    # =========================
    # HEADER HARI
    # =========================
    h_cols = st.columns(7)
    for i, h in enumerate(["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]):
        h_cols[i].markdown(
            f"<p style='text-align:center;font-weight:bold'>{h}</p>",
            unsafe_allow_html=True
        )

    # =========================
    # HITUNG LABEL PER HARI
    # =========================
    cal_matrix = calendar.monthcalendar(cv.year, cv.month)
    days_in_month = max([max(week) for week in cal_matrix])

    labels = []

    for day in range(1, days_in_month + 1):
        curr_dt = date(cv.year, cv.month, day)
        hst = (curr_dt - tgl_tanam).days

        idx = min(max(0, day - 1), len(forecast_30) - 1)

        label = label_singkat(
            rbs_singkong_final(forecast_30[idx], hst)
        )

        labels.append(label)

    # =========================
    # GROUP RANGE
    # =========================
    ranges = group_ranges(labels)

    # mapping day → info range
    day_info = {}

    for start, end, label in ranges:
        bg, border = get_color(label)

        for d in range(start + 1, end + 2):
            day_info[d] = {
                "bg": bg,
                "border": border,
                "start": start + 1,
                "end": end + 1,
                "label": label
            }

    # =========================
    # LEGEND (WAJIB UNTUK USER)
    # =========================
    st.write("")
    l1, l2, l3, l4 = st.columns(4)
    l1.success("🌱 Tanam")
    l2.info("💧 Siram")
    l3.warning("🧪 Pemupukan (range)")
    l4.error("🚜 Panen")

    st.caption("⚠️ Warna menunjukkan RENTANG waktu terbaik, bukan aktivitas harian")

    st.write("---")

    # =========================
    # GRID KALENDER
    # =========================
    for week in cal_matrix:
        cols = st.columns(7)

        for i, day in enumerate(week):

            if day == 0:
                cols[i].write("")
                continue

            info = day_info.get(day, None)

            if info:
                bg = info["bg"]
                border = info["border"]
                start = info["start"]
                end = info["end"]
            else:
                bg, border = "#f3f4f6", "#d1d5db"
                start, end = day, day

            # =========================
            # BORDER RADIUS (BIAR JADI BLOK)
            # =========================
            if day == start:
                radius = "12px 0 0 12px"
            elif day == end:
                radius = "0 12px 12px 0"
            else:
                radius = "0"

            # =========================
            # HIGHLIGHT SELECTED
            # =========================
            selected = st.session_state.get("selected_day", None)

            if day == selected:
                border_style = "3px solid black"
            else:
                border_style = f"2px solid {border}"

            # =========================
            # RENDER BUTTON (SEBAGAI BOX)
            # =========================
            btn = cols[i].button(
                str(day),
                key=f"day_{cv.month}_{day}",
                use_container_width=True
            )

            st.markdown(f"""
            <style>
            button[key="day_{cv.month}_{day}"] {{
                background-color: {bg} !important;
                border: {border_style} !important;
                border-radius: {radius} !important;
                height: 105px !important;
                font-size: 18px !important;
                font-weight: bold !important;
            }}
            </style>
            """, unsafe_allow_html=True)

            if btn:
                selected_day = day

    return selected_day, labels, ranges
