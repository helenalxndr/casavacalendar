import streamlit as st

def render_day_button(col, day, label, color, key, selected=False):
    border = "3px solid #000" if selected else "1px solid #ddd"
    shadow = "0 4px 12px rgba(0,0,0,0.15)" if selected else "0 2px 6px rgba(0,0,0,0.08)"
    
    # CSS untuk menyatukan Tombol Klik dan Visual dalam satu koordinat
    st.markdown(f"""
    <style>
    /* 1. Membuat container kolom menjadi relatif */
    div[data-testid="column"]:has(button[key="btn_{key}"]) {{
        position: relative;
        height: 100px; /* Samakan dengan tinggi visual */
    }}

    /* 2. Memaksa tombol asli menutupi seluruh area visual secara presisi */
    div[data-testid="stElementContainer"]:has(button[key="btn_{key}"]) {{
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 10; /* Berada di depan untuk menangkap klik */
    }}

    div[data-testid="stElementContainer"]:has(button[key="btn_{key}"]) button {{
        height: 95px !important;
        width: 100% !important;
        background: transparent !important;
        border: none !important;
        color: transparent !important;
        cursor: pointer;
    }}
    </style>
    """, unsafe_allow_html=True)

    # RENDER AREA KLIK (Sekarang posisinya sudah absolute menimpa visual)
    clicked = col.button("", key=f"btn_{key}", use_container_width=True)

    # RENDER VISUAL CUSTOM
    col.markdown(f"""
    <div style="
        height: 95px;
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
        z-index: 1; /* Di belakang tombol klik */
        pointer-events: none;
    ">
        <div style="font-size:20px; font-weight:800; line-height:1.1;">
            {day}
        </div>
        <div style="font-size:10px; opacity:0.9; margin-top: 4px; font-weight:500; text-transform: uppercase;">
            {label}
        </div>
    </div>
    """, unsafe_allow_html=True)

    return clicked
