import streamlit as st

def render_day_button(col, day, label, color, key, selected=False):
    # Logika Style
    border = "3px solid #000" if selected else "1px solid #ddd"
    shadow = "0 4px 12px rgba(0,0,0,0.15)" if selected else "0 2px 6px rgba(0,0,0,0.08)"
    
    # CSS Sakti untuk menyatukan Klik dan Visual
    st.markdown(f"""
    <style>
    /* 1. Paksa container tombol asli Streamlit menjadi 0 height agar elemen di bawahnya naik */
    div[data-testid="stElementContainer"]:has(button[key="btn_{key}"]) {{
        height: 0px !important;
        margin-bottom: 0px !important;
        padding: 0px !important;
        z-index: 10;
        position: relative;
    }}

    /* 2. Buat tombol aslinya transparan dan menutupi area 95px ke bawah */
    div[data-testid="stElementContainer"]:has(button[key="btn_{key}"]) button {{
        height: 95px !important;
        width: 100% !important;
        background: transparent !important;
        border: none !important;
        color: transparent !important;
        box-shadow: none !important;
        cursor: pointer;
        position: relative;
        top: 0;
    }}

    /* 3. Hilangkan efek hover merah/abu bawaan Streamlit */
    div[data-testid="stElementContainer"]:has(button[key="btn_{key}"]) button:hover {{
        background: transparent !important;
        color: transparent !important;
        border: none !important;
    }}
    div[data-testid="stElementContainer"]:has(button[key="btn_{key}"]) button:active {{
        background: transparent !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # --- RENDER AREA ---
    
    # Area Klik (Diletakkan pertama, tapi karena height:0, dia tidak memakan ruang)
    clicked = col.button("", key=f"btn_{key}", use_container_width=True)

    # Visual Box (Muncul tepat di posisi yang sama karena elemen di atasnya height:0)
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
        z-index: 1;
        pointer-events: none;
        text-align: center;
    ">
        <div style="font-size:22px; font-weight:800; line-height:1;">
            {day}
        </div>
        <div style="font-size:10px; opacity:0.9; margin-top: 4px; font-weight:600; text-transform: uppercase;">
            {label}
        </div>
    </div>
    """, unsafe_allow_html=True)

    return clicked
