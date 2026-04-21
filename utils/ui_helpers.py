def render_day_button(col, day, label, color, key, selected=False):
    border = "3px solid #000" if selected else "1px solid #ddd"
    shadow = "0 4px 12px rgba(0,0,0,0.15)" if selected else "0 2px 6px rgba(0,0,0,0.08)"

    clicked = col.button("", key=f"btn_{key}", use_container_width=True)

    col.markdown(f"""
    <div style="
        margin-top: -95px;
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
        pointer-events: none;
    ">
        <div style="font-size:40px; font-weight:700;">
            {day}
        </div>
        <div style="font-size:20px; font-weight:700;">
            {label}
        </div>
    </div>
    """, unsafe_allow_html=True)

    return clicked
