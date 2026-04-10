import streamlit as st
import pandas as pd
import numpy as np
from datetime import date

from utils.loader import load_all
from utils.forecast import recursive_forecast

from components.sidebar import render_sidebar
from components.calendar_view import render_calendar
from components.detail_panel import render_detail
from components.styles import load_css

st.set_page_config(layout="wide", page_title="Dashboard Tanam Singkong")

# LOAD
model, encoder, scaler, data = load_all()
data["tanggal"] = pd.to_datetime(data["tanggal"])

if "view_date" not in st.session_state:
    st.session_state.view_date = date(2026, 3, 1)

# SIDEBAR
sel_kecamatan, kec_id, tgl_tanam = render_sidebar(data, encoder)

# FORECAST
df_kec = data[data["kecamatan"] == sel_kecamatan].copy().sort_values("tanggal")
rain_last270 = df_kec["rain_mm"].values[-270:]

forecast_30 = recursive_forecast(
    model=model,
    scaler=scaler,
    rain_last270=rain_last270,
    kec_id=kec_id,
    days=31
)

forecast_30 = np.clip(forecast_30, 0, 300)

# STYLE
load_css()

# LAYOUT
col1, col2 = st.columns([3,1])

with col1:
    selected_day, labels, ranges = render_calendar(
        st.session_state.view_date,
        tgl_tanam,
        forecast_30
    )

with col2:
    render_detail(
        st.session_state.view_date,
        selected_day,
        tgl_tanam,
        forecast_30
    )
