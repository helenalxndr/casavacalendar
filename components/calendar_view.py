import streamlit as st
from streamlit_calendar import calendar

def render_calendar(df_dashboard, tanggal_acuan):
    events = [
        {
            "title": row["Aktivitas"],
            "start": row["Tanggal"].strftime("%Y-%m-%d"),
            "color": "#2ecc71" if row["Aktivitas"] == "Penanaman" else "#f1c40f"
        }
        for _, row in df_dashboard.iterrows()
    ]

    state = calendar(
        events=events,
        options={
            "initialView": "dayGridMonth",
            "initialDate": tanggal_acuan.strftime("%Y-%m-%d"),
            "locale": "id",
            "height": 650,
            "selectable": True,     # 🔥 WAJIB
            "dateClick": True,      # 🔥 WAJIB
            "headerToolbar": {
                "left": "",
                "center": "title",
                "right": ""
            }
        },
        key="kalender"
    )

    return state
