import streamlit as st

def render_day_button(col, day, label, color, key):
    btn_html = f"""
    <div style="
        height:105px;
        border-radius:10px;
        border:1px solid #e5e7eb;
        background-color:{color};
        display:flex;
        flex-direction:column;
        justify-content:center;
        align-items:center;
        color:white;
        font-weight:bold;
    ">
        <div style="font-size:18px;">{day}</div>
        <div style="font-size:10px;">{label}</div>
    </div>
    """

    return col.button(
        btn_html,
        key=key,
        use_container_width=True
    )
