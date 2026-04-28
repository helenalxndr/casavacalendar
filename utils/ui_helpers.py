def render_day_button(col, day, label, color, key, selected=False):
    border = "3px solid #000" if selected else "1px solid #ddd"
    shadow = "0 4px 12px rgba(0,0,0,0.15)" if selected else "0 2px 6px rgba(0,0,0,0.08)"

    class_name = f"calendar-btn-wrapper"

    col.markdown(f'<div class="{class_name}">', unsafe_allow_html=True)

    # tombol invisible (klik)
    clicked = col.button("", key=f"btn_{key}", use_container_width=True)

    # UI visual (tidak bisa diklik)
    col.markdown(f"""
        <div style="
            position: relative;
            height: 95px;
            margin-top: -95px;
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
            z-index: 1;
        ">
            <div style="font-size:28px; font-weight:700;">
                {day}
            </div>
            <div style="font-size:30px; font-weight:700;">
                {label}
            </div>
        </div>
    """, unsafe_allow_html=True)

    col.markdown("</div>", unsafe_allow_html=True)

    return clicked
