def render_day_button(col, day, label, color, key, selected=False):
    border = "3px solid #000" if selected else "1px solid #ddd"
    shadow = "0 4px 12px rgba(0,0,0,0.15)" if selected else "0 2px 6px rgba(0,0,0,0.08)"

    # CSS: bikin button jadi overlay full
    st.markdown(f"""
    <style>
    div[data-testid="stElementContainer"]:has(button[key="btn_{key}"]) {{
        position: relative;
        height: 95px;
    }}

    div[data-testid="stElementContainer"]:has(button[key="btn_{key}"]) button {{
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 95px;
        opacity: 0;
        z-index: 10;
        cursor: pointer;
    }}
    </style>
    """, unsafe_allow_html=True)

    # BUTTON (area klik)
    clicked = col.button("", key=f"btn_{key}", use_container_width=True)

    # VISUAL (di bawah button)
    col.markdown(f"""
    <div style="
        height: 95px;
        border-radius: 14px;
        border: {border};
        background-color: {color};
        color: white;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: {shadow};
        margin-top: -95px;
        pointer-events: none;
    ">
        <div style="font-size:22px; font-weight:700;">
            {day}
        </div>
        <div style="font-size:11px; opacity:0.9;">
            {label}
        </div>
    </div>
    """, unsafe_allow_html=True)

    return clicked
