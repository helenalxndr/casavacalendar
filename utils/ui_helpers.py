import streamlit as st

def render_day_button(col, day, label, color, key, selected=False):
    # Buat border jika terpilih
    border_style = "border: 3px solid #000 !important;" if selected else "border: 1px solid #ddd !important;"
    
    # Gunakan container untuk menyuntikkan CSS spesifik ke button ini saja
    # Kita menggunakan f-string untuk menargetkan key spesifik (Streamlit meng-hash key ini)
    with col:
        st.markdown(f"""
        <style>
        div[data-testid="stElementContainer"]:has(button[key="{key}"]) button {{
            background-color: {color} !important;
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
        Memetakan kode aktivitas dari RBS ke warna HEX untuk UI kalender.
        """
        mapping = {
            "tanam":   "#22c55e", # Hijau (Masa Tanam)
            "tunda":   "#f97316", # Oranye (Kondisi Tidak Ideal)
            "air":     "#3b82f6", # Biru (Penyiraman/Drainase)
            "pupuk":   "#eab308", # Kuning (Pemupukan)
            "gulma":   "#a855f7", # Ungu (Penyiangan)
            "panen":   "#ef4444", # Merah (Panen)
            "monitor": "#9ca3af", # Abu-abu (Pemantauan Rutin)
        }
        # Default ke abu-abu jika kode tidak terdefinisi
        return mapping.get(kode, "#9ca3af")
