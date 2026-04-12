import streamlit as st

def render_day_button(col, day, label, color, key, selected=False):
    # Logika Style
    border = "3px solid #000" if selected else "1px solid #ddd"
    shadow = "0 4px 12px rgba(0,0,0,0.15)" if selected else "0 2px 6px rgba(0,0,0,0.08)"
    
    # 1. CSS untuk menghilangkan fisik tombol tapi tetap mempertahankan area klik
    st.markdown(f"""
    <style>
    /* Menargetkan container tombol agar tidak mendorong elemen di bawahnya */
    div[data-testid="stElementContainer"]:has(button[key="btn_{key}"]) {{
        margin-bottom: -95px; /* Tarik elemen di bawahnya (visual) ke atas */
        height: 95px;
        z-index: 10;
        position: relative;
    }}

    /* Menargetkan tombol asli agar transparan total */
    div[data-testid="stElementContainer"]:has(button[key="btn_{key}"]) button {{
        height: 95px !important;
        background: transparent !important;
        border: none !important;
        color: transparent !important;
        width: 100% !important;
        cursor: pointer;
        z-index: 10;
    }}

    /* Pastikan tidak ada warna merah saat hover di tombol transparan */
    div[data-testid="stElementContainer"]:has(button[key="btn_{key}"]) button:hover {{
        background: transparent !important;
        border: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # 2. RENDER AREA KLIK (Tombol hantu)
    clicked = col.button("", key=f"btn_{key}", use_container_width=True)

    # 3. RENDER VISUAL CUSTOM
    # Box ini akan naik secara otomatis karena margin-bottom negatif di atas
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
        <div style="font-size:10px; opacity:0.9; margin-top: 4px; font-weight:600; text-transform: uppercase; letter-spacing: 0.5px;">
            {label}
        </div>
    </div>
    """, unsafe_allow_html=True)

    return clicked
