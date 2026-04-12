import streamlit as st

def render_day_button(col, day, label, color, key, selected=False):
    # Pengaturan Style
    border = "3px solid #000" if selected else "1px solid #ddd"
    shadow = "0 4px 12px rgba(0,0,0,0.15)" if selected else "0 2px 6px rgba(0,0,0,0.08)"
    
    # CSS Sakti untuk "Ghost Button" (Menghilangkan gap antara tombol dan visual)
    st.markdown(f"""
    <style>
    /* 1. Membuat kolom menjadi container relatif agar absolute child-nya terkunci di sini */
    div[data-testid="column"]:has(button[key="btn_{key}"]) {{
        position: relative;
        min-height: 95px;
    }}

    /* 2. Menghilangkan ruang fisik pembungkus tombol Streamlit */
    div[data-testid="stElementContainer"]:has(button[key="btn_{key}"]) {{
        position: absolute !important;
        top: 0;
        left: 0;
        width: 100%;
        height: 100% !important;
        z-index: 10; /* Berada di depan untuk menangkap klik */
        margin: 0 !important;
        padding: 0 !important;
    }}

    /* 3. Membuat tombol bening sempurna menutupi area */
    div[data-testid="stElementContainer"]:has(button[key="btn_{key}"]) button {{
        height: 95px !important;
        width: 100% !important;
        background: transparent !important;
        border: none !important;
        color: transparent !important;
        box-shadow: none !important;
        cursor: pointer;
    }}

    /* 4. Mencegah perubahan warna saat di-hover agar kotak hijau tidak tertutup abu-abu */
    div[data-testid="stElementContainer"]:has(button[key="btn_{key}"]) button:hover {{
        background: transparent !important;
        border: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # --- PROSES RENDER ---
    
    # Tombol klik (Secara visual tidak terlihat, tapi ada di depan)
    clicked = col.button("", key=f"btn_{key}", use_container_width=True)

    # Kotak Visual (Berada tepat di bawah tombol klik)
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
        z-index: 1; /* Di belakang tombol */
        pointer-events: none; /* Klik akan menembus ke tombol di depannya */
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
