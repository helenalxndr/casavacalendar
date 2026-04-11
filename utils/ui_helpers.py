import streamlit as st

def render_day_button(col, day, label, color, key, selected=False):

    border = "3px solid black" if selected else "1px solid #ddd"

    return col.button(
        f"{day}\n{label}",
        key=key,
        use_container_width=True
    )
