def render_day_button(col, day, label, color, key, selected=False):

    border = "3px solid black" if selected else "1px solid #ddd"

    # unique class per tombol
    class_name = f"btn_{key}"

    col.markdown(f"""
    <style>
    .{class_name} button {{
        height: 100px;
        border-radius: 10px;
        border: {border};
        background-color: {color} !important;
        color: white;
        font-weight: bold;

        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;

        white-space: normal !important;
        text-align: center;
    }}
    </style>
    <div class="{class_name}">
    """, unsafe_allow_html=True)

    clicked = col.button(
        f"**{day}**\n{label}",
        key=key,
        use_container_width=True
    )

    col.markdown("</div>", unsafe_allow_html=True)

    return clicked
