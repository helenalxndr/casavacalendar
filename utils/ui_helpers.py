import streamlit as st

def render_day_button(col, day, label, color, key, selected=False):

    border = "3px solid black" if selected else "1px solid #ddd"

    btn_html = f"""
    <div style="
        height:100px;
        border-radius:10px;
        border:{border};
        background-color:{color};
        display:flex;
        flex-direction:column;
        justify-content:center;
        align-items:center;
        color:white;
        font-weight:bold;
    ">
        <div style="font-size:18px">{day}</div>
        <div style="font-size:10px">{label}</div>
    </div>
    """

    return col.button(btn_html, key=key, use_container_width=True)
