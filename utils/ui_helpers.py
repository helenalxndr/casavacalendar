def render_day_button(col, day, label, color, key, selected=False):
    border = "3px solid #000" if selected else "1px solid #ddd"
    shadow = "0 4px 12px rgba(0,0,0,0.15)" if selected else "0 2px 6px rgba(0,0,0,0.08)"

    # Wrapper
    col.markdown('<div class="calendar-cell">', unsafe_allow_html=True)

    # Button (overlay)
    clicked = col.button("", key=f"btn_{key}", use_container_width=True)

    # Visual box
    col.markdown(f"""
    <div style="
        height: 95px;
        width: 100%;
        border-radius: 12px;
        border: {border};
        background-color: {color};
        color: white;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: {shadow};
        position: relative;
        z-index: 1;
        pointer-events: none;
    ">
        <div style="font-size:22px; font-weight:800; line-height:1;">
            {day}
        </div>
        <div style="font-size:10px; opacity:0.9; margin-top: 4px; font-weight:600; text-transform: uppercase;">
            {label}
        </div>
    </div>
    """, unsafe_allow_html=True)

    col.markdown("</div>", unsafe_allow_html=True)

    return clicked
