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
        try:
            with open(FILNAMN, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"admin": "12"}
    return {"admin": "12"}

anvandare_dict = ladda_anvandare()

# --- INLOGGNINGSHANTERING ---
if "inloggad" not in st.session_state:
    st.session_state["inloggad"] = False
if "anvandare" not in st.session_state:
    st.session_state["anvandare"] = ""

def logga_in():
    st.title("Inloggning - Jimotec AB")
    meddelande = st.empty()
    
    meddelande.info("Mata in användarnamn och lösenord för att fortsätta.")
    
    anvandarnamn = st.text_input("Användarnamn", key="login_user")
    losenord = st.text_input("Lösenord", type="password", key="login_pass")
    
    if st.button("Logga in", use_container_width=True):
        if anvandarnamn in anvandare_dict and anvandare_dict[anvandarnamn] == losenord:
            st.session_state["inloggad"] = True
            st.session_state["anvandare"] = anvandarnamn
            st.rerun()
        else:
            meddelande.error("Felaktigt användarnamn eller lösenord.")

# Om inte inloggad, visa endast inloggningsskärmen
if not st.session_state["inloggad"]:
    logga_in()
    st.stop()

# --- SIDOPANEL & MENYER (VISAS ENDAST NÄR MAN ÄR INLOGGAD) ---

# Hitta rätt filnamn oavsett stora/små bokstäver för loggan
logo_file = None
for f in os.listdir("."):
    if f.lower() in ["jimotec.jpg", "jimotec.png", "jimotec.jpeg"]:
        logo_file = f
        break

if logo_file:
    st.sidebar.image(logo_file, use_container_width=True)

st.sidebar.write(f"Inloggad som: **{st.session_state['anvandare']}**")
if st.sidebar.button("Logga ut"):
    st.session_state["inloggad"] = False
    st.session_state["anvandare"] = ""
    st.rerun()

st.sidebar.divider()

# Hjälpfunktion för att bara länka om filen faktiskt finns på GitHub
def skapa_säker_länk(sökväg, etikett, ikon=None):
    if os.path.exists(sökväg):
        st.sidebar.page_link(sökväg, label=etikett, icon=ikon)

# 1. HUVUDMENY: STARTSIDA
skapa_säker_länk("app.py", "Startsida", "🏠")

st.sidebar.divider()

# 2. HUVUDMENY: KUND & RITNINGAR
st.sidebar.markdown("### 📋 Kund & Produktion")
skapa_säker_länk("pages/1_kund.py", "Kundregister", "👤")
skapa_säker_länk("pages/2_ritningar.py", "Ritningshantering", "📐")

# 3. HUVUDMENY: EKONOMI & PLANERING
st.sidebar.markdown("### 📊 Ekonomi & Styrning")
skapa_säker_länk("pages/3_affarsplan_ekonomi.py", "Affärsplan & Ekonomi", "📈")

# --- INNEHÅLL PÅ STARTSIDAN ---
st.title("Välkommen till Jimotec AB")
st.write("Du är nu inloggad. Välj en meny i sidopanelen till vänster för att navigera i systemet.")
