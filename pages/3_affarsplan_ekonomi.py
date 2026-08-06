import os
import streamlit as st

# Konfigurera sidan
st.set_page_config(page_title="Ekonomisk plan - Jimotec AB", layout="wide")

# Dölj standardmenyn i sidopanelen
st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True,
)

# Sök och visa loggan i sidopanelen (kollar i både mappen och överliggande mapp)
logo_sökvägar = [
    "Jimotec.jpg",
    "jimotec.jpg",
    "Jimotec.JPG",
    "jimotec.JPG",
    "Jimotec.png",
    "jimotec.png",
    "../Jimotec.jpg",
    "../jimotec.jpg",
    "../Jimotec.png",
    "../jimotec.png",
]

for path in logo_sökvägar:
    if os.path.exists(path):
        st.sidebar.image(path, use_container_width=True)
        st.sidebar.divider()
        break

# Länk tillbaka till Startsidan i sidopanelen
if os.path.exists("app.py"):
    st.sidebar.page_link("app.py", label="Startsida", icon="🏠")
elif os.path.exists("../app.py"):
    st.sidebar.page_link("../app.py", label="Startsida", icon="🏠")

# --- HUVUDINNEHÅLL ---
st.title("Ekonomisk plan")

st.write("Detta är grundläggande anteckningar för Jimotec AB och den ekonomiska planen.")
st.markdown(
    """
- **Affärsområde:** CNC-bearbetning och tillverkning av mekaniska komponenter.
- **System och verktyg:** Monitor ERP, n8n, Streamlit.
"""
)

st.divider()

# Grön knapp för Google Docs
st.link_button(
    "Öppna och redigera i Google Docs",
    "https://docs.google.com",  # Byt ut mot din länk till dokumentet
    type="primary",
)
