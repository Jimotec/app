import os
import json
import streamlit as st

# Konfigurera sidan
st.set_page_config(page_title="Jimotec AB", layout="wide")

# Dölj den automatiska sidolistan i sidopanelen
st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True,
)

FILNAMN = "users.json"

# Ladda användare från fil (standardlösenord satt till 12)
def ladda_anvandare():
    if os.path.exists(FILNAMN):
        with open(FILNAMN, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"admin": "12"}

anvandare_dict = ladda_anvandare()

# Hitta rätt filnamn oavsett stora/små bokstäver för loggan
logo_file = None
for f in os.listdir("."):
    if f.lower() in ["jimotec.jpg", "jimotec.png", "jimotec.jpeg"]:
        logo_file = f
        break

# Sidopanel med logotyp och navigeringsmeny
if logo_file:
    st.sidebar.image(logo_file, use_container_width=True)

st.sidebar.title("Navigering")

# --- Säker navigering (länkar bara till filer som faktiskt finns) ---

# Startsida
st.sidebar.page_link("app.py", label="Startsida", icon="🏠")

# Undersidor i mappen pages/
sidor = [
    ("pages/1_kund.py", "Kund", "👤"),
    ("pages/2_ritningar.py", "Ritningar", "📐"),
    ("pages/3_affarsplan_ekonomi.py", "Affärsplan & Ekonomi", "📊"),
]

for sökvaeg, etikett, ikon in sidor:
    if os.path.exists(sökvaeg):
        st.sidebar.page_link(sökvaeg, label=etikett, icon=ikon)

# --- Innehåll på startsidan ---
st.title("Välkommen till Jimotec AB")
st.write("Välj en sida i menyn till vänster för att komma igång.")
