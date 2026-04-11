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
