import streamlit as st

def render_day_button(col, day, label, color, key, selected=False):
    """
    Fungsi untuk merender tombol kalender dengan warna dinamis.
    """
    # Logika border: Hitam jika dipilih, abu-abu jika tidak
    border_style = "border: 3px solid #000 !important;" if selected else "border: 1px solid #ddd !important;"
    
    # CSS dinamis menggunakan :has selector untuk menargetkan key spesifik
    with col:
        st.markdown(f"""
        <style>
        div[data-testid="stElementContainer"]:has(button[key="{key}"]) button {{
            background-color: {color} !important;
            color: white !important;
            {border_style}
            height: 100px;
            border-radius: 10px;
            font-weight: bold;
            white-space: pre-line;
            font-size: 11px;
            line-height: 1.2;
        }}
        
        /* Efek hover agar tombol terasa interaktif */
        div[data-testid="stElementContainer"]:has(button[key="{key}"]) button:hover {{
            filter: brightness(0.9);
            {border_style}
        }}
        </style>
        """, unsafe_allow_html=True)
        
        return st.button(
            f"{day}\n{label}",
            key=key,
            use_container_width=True
        )

def get_color_by_code(kode):
    """
    Memetakan kode aktivitas dari RBS ke warna HEX.
    Pastikan fungsi ini sejajar dengan render_day_button (tidak menjorok ke dalam).
    """
    mapping = {
        "tanam":   "#22c55e", # Hijau
        "tunda":   "#f97316", # Oranye
        "air":     "#3b82f6", # Biru
        "pupuk":   "#eab308", # Kuning
        "gulma":   "#a855f7", # Ungu
        "panen":   "#ef4444", # Merah
        "monitor": "#9ca3af", # Abu-abu
    }
    return mapping.get(kode, "#9ca3af")
