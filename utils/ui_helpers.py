def render_day_button(col, day, label, color, key, selected=False):

    border = "3px solid #000" if selected else "1px solid #ddd"
    shadow = "0 0 0 2px rgba(0,0,0,0.2)" if selected else "0 1px 3px rgba(0,0,0,0.1)"

    class_name = f"btn_{key}"

    col.markdown(f"""
    <style>
    .{class_name} button {{
        height: 100px;
        border-radius: 12px;
        border: {border};
        background-color: {color} !important;
        color: white;
        font-weight: 600;

        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;

        padding: 6px;
        line-height: 1.2;
        box-shadow: {shadow};

        transition: all 0.2s ease;
    }}

    .{class_name} button:hover {{
        transform: scale(1.05);
        filter: brightness(1.1);
    }}
    </style>
    <div class="{class_name}">
    """, unsafe_allow_html=True)

    clicked = col.button(
        f"{day}\n{label}",
        key=key,
        use_container_width=True
    )

    col.markdown("</div>", unsafe_allow_html=True)

    return clicked
    
