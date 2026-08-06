import os
import streamlit as st

# Konfigurera sidan
st.set_page_config(page_title="1. Sammanfattning - Jimotec AB", layout="wide")

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

# --- HUVUDINNEHÅLL ---

# Liten knapp längst till vänster i marginalen
col1, _ = st.columns([2, 10])

with col1:
    st.link_button(
        "✏️ Redigera i Google Docs",
        "https://docs.google.com/document/d/1oq-db-sl71-yBWgliLo8brRI07ro96D-/edit",
    )

st.write("")  # Lite avstånd innan dokumentet

# --- INBÄDDAT GOOGLE DOCS-DOKUMENT ---
doc_url = "https://docs.google.com/document/d/1oq-db-sl71-yBWgliLo8brRI07ro96D-/preview"

st.components.v1.iframe(doc_url, height=800, scrolling=True)
