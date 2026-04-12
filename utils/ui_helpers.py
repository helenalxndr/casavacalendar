import streamlit as st

def render_day_button(col, day, label, color, key, selected=False):
    border = "3px solid #000" if selected else "1px solid #ddd"
    shadow = "0 4px 12px rgba(0,0,0,0.15)" if selected else "0 2px 6px rgba(0,0,0,0.08)"
    
    # CSS untuk memaksa penumpukan sempurna
    st.markdown(f"""
    <style>
    /* 1. Targetkan kolom agar menjadi anchor/jangkar */
    div[data-testid="column"]:has(button[key="btn_{key}"]) {{
        position: relative;
        height: 95px; /* Kunci: Tinggi kolom dikunci */
    }}

    /* 2. Paksa pembungkus tombol Streamlit untuk melayang di atas */
    div[data-testid="stElementContainer"]:has(button[key="btn_{key}"]) {{
        position: absolute !important;
        top: 0;
        left: 0;
        width: 100%;
        height: 100% !important;
        z-index: 10; /* Berada di lapisan paling depan */
        margin: 0 !important;
        padding: 0 !important;
    }}

    /* 3. Buat tombol aslinya benar-benar bening dan memenuhi kotak */
    div[data-testid="stElementContainer"]:has(button[key="btn_{key}"]) button {{
        height: 95px !important;
        width: 100% !important;
        background: transparent !important;
        border: none !important;
        color: transparent !important;
        box-shadow: none !important;
        cursor: pointer;
    }}

    /* 4. Pastikan tidak ada gangguan saat hover */
    div[data-testid="stElementContainer"]:has(button[key="btn_{key}"]) button:hover {{
        background: transparent !important;
        border: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # --- EKSEKUSI ---
    
    # Render Button (Sekarang melayang secara absolut)
    clicked = col.button("", key=f"btn_{key}", use_container_width=True)

    # Render Visual (Berada di bawah tombol karena z-index rendah)
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

    return clicked
    
