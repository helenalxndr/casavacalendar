import streamlit as st

import streamlit as st

def render_day_button(col, day, label, color, key, selected=False):

    border = "3px solid black" if selected else "1px solid #ddd"

    # CSS hanya untuk BUTTON INI saja (bukan global)
    html = f"""
    <style>
    div[data-testid="stButton"][key="{key}"] > button {{
        height: 65px;
        border-radius: 10px;
        border: {border};
        background-color: {color} !important;
        color: white !important;
        font-weight: 600;
        padding: 2px;
        line-height: 1.1;
        display: flex;
        flex-direction: column;
        justify-content: center;
        white-space: normal;
    }}
    </style>
    """

    st.markdown(html, unsafe_allow_html=True)

    return col.button(
        f"{day}\n{label}",
        key=key,
        use_container_width=True
    )
