import streamlit as st

def render_day_button(col, day, label, color, key, selected=False):

    border = "3px solid black" if selected else "1px solid #ddd"

    st.markdown(f"""
    <style>
    div[data-testid="stButton"] > button {{
        height: 100px;
        border-radius: 10px;
        border: {border};
        background-color: {color} !important;
        color: white;
        font-weight: bold;
        white-space: pre-line;
    }}
    </style>
    """, unsafe_allow_html=True)

    return col.button(
        f"{day}\n{label}",
        key=key,
        use_container_width=True
    )
