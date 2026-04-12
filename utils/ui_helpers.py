import streamlit as st

def render_day_button(col, day, label, color, key, selected=False):
    border = "3px solid #000" if selected else "1px solid #ddd"
    shadow = "0 4px 12px rgba(0,0,0,0.15)" if selected else "0 2px 6px rgba(0,0,0,0.08)"
    
    # CSS untuk menyembunyikan button asli tapi tetap bisa diklik
    # Kita buat button aslinya transparan dan menutupi seluruh area visual
    st.markdown(f"""
    <style>
    div[data-testid="stElementContainer"]:has(button[key="btn_{key}"]) {{
        position: relative;
        margin-bottom: -95px; /* Menarik konten di bawahnya naik setinggi kotak */
        z-index: 2;
    }}
    div[data-testid="stElementContainer"]:has(button[key="btn_{key}"]) button {{
        height: 95px !important;
        background: transparent !important;
        border: none !important;
        color: transparent !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # 1. Button asli untuk menangkap klik
    clicked = col.button("", key=f"btn_{key}", use_container_width=True)

    # 2. Visual Custom (Tanpa margin-top negatif yang merusak layout)
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
        pointer-events: none;
        position: relative;
        z-index: 1;
    ">
        <div style="font-size:22px; font-weight:700; line-height:1;">
            {day}
        </div>
        <div style="font-size:11px; opacity:0.9; margin-top: 4px; text-transform: lowercase;">
            {label}
        </div>
    </div>
    """, unsafe_allow_html=True)

    return clicked
