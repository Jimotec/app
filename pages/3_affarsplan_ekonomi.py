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

# Sök och visa loggan i sidopanelen
logo_sökvägar = [
    "Jimotec.jpg",
    "jimotec.jpg",
    "Jimotec.JPG",
    "jimotec.JPG",
    "Jimotec.png",
    "jimotec.png",
    "../Jimotec.jpg",
    "../jimotec.jpg",
]

for path in logo_sökvägar:
    if os.path.exists(path):
        st.sidebar.image(path, use_container_width=True)
        st.sidebar.divider()
        break

# Länk tillbaka till Startsidan
if os.path.exists("app.py"):
    st.sidebar.page_link("app.py", label="Startsida", icon="🏠")
elif os.path.exists("../app.py"):
    st.sidebar.page_link("../app.py", label="Startsida", icon="🏠")

# --- INBÄDDAT GOOGLE DOCS-DOKUMENT ---
doc_url = "https://docs.google.com/document/d/1C5lMmkIjkaDNaqD72WJ-VFCwaGKCcu7P/preview"

st.components.v1.iframe(doc_url, height=800, scrolling=True)

st.divider()

# Knapp för att öppna och redigera i ny flik
st.link_button(
    "Öppna och redigera i Google Docs",
    "https://docs.google.com/document/d/1C5lMmkIjkaDNaqD72WJ-VFCwaGKCcu7P/edit",
    type="primary",
)
