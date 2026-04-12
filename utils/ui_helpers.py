def render_day_button(col, day, label, color, key, selected=False):

    border = "2px solid #000" if selected else "1px solid #ddd"
    shadow = "0 4px 12px rgba(0,0,0,0.15)" if selected else "0 2px 6px rgba(0,0,0,0.08)"

    class_name = f"btn_{key}"

    col.markdown(f"""
    <style>
    .{class_name} button {{
        height: 95px;
        border-radius: 14px;
        border: {border};
        background-color: {color} !important;
        color: white;

        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;

        padding: 6px;
        box-shadow: {shadow};
        transition: all 0.2s ease;
    }}

    .{class_name} button:hover {{
        transform: translateY(-2px) scale(1.03);
        filter: brightness(1.08);
    }}

    /* TANGGAL (BESAR & DI ATAS) */
    .{class_name} .day-number {{
        font-size: 24px;
        font-weight: 700;
        line-height: 1;
        text-align: center;
    }}

    /* LABEL (KECIL DI BAWAH) */
    .{class_name} .day-label {{
        font-size: 11px;
        margin-top: 4px;
        opacity: 0.9;
        text-align: center;
    }}
    </style>

    <div class="{class_name}">
    """, unsafe_allow_html=True)

    clicked = col.button(
        f"<div class='day-number'>{day}</div>"
        f"<div class='day-label'>{label}</div>",
        key=key,
        use_container_width=True
    )

    col.markdown("</div>", unsafe_allow_html=True)

    return clicked
