import json
import os
import streamlit as st

# Konfigurera sidan
st.set_page_config(page_title="Jimotec AB", layout="wide")

# Döljer automatiska listan med sidor i sidopanelen helt
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
for f in [
    "jimotec.jpg",
    "Jimotec.jpg",
    "jimotec.JPG",
    "Jimotec.JPG",
    "jimotec.png",
    "Jimotec.png",
]:
    if os.path.exists(f):
        logo_file = f
        break

# Inloggningslogik
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Visa loggan om den hittades
    if logo_file:
        st.image(logo_file, width=200)

    st.title("🔒 Inloggning - Jimotec AB")

    input_namn = st.text_input("Namn")
    input_losenord = st.text_input("Lösenord", type="password")

    if st.button("Logga in"):
        if (
            input_namn in anvandare_dict
            and anvandare_dict[input_namn] == input_losenord
        ):
            st.session_state.logged_in = True
            st.session_state.anvandarnamn = input_namn
            st.rerun()
        else:
            st.error("❌ Fel namn eller lösenord. Försök igen.")

else:
    # Loggan i sidopanelen när man är inloggad
    if logo_file:
        st.sidebar.image(logo_file, width=150)

    st.sidebar.title("Meny")

    # Huvudlänk för startsidan
    st.sidebar.page_link("app.py", label="Startsida")

    # 1. Admin-meny
    with st.sidebar.expander("Admin", expanded=False):
        st.page_link("pages/1_start_admin.py", label="Admin Start")
        st.page_link("pages/2_sida_password.py", label="Hantera lösenord")

    # 2. Jimotec-meny
    with st.sidebar.expander("Jimotec", expanded=False):
        st.page_link("pages/4_jimotec_miro.py", label="Miro-analys")

    # 3. Vision-meny
    with st.sidebar.expander("Vision", expanded=False):
        st.page_link("pages/5_jimotec_ai.py", label="AI")

    # 4. Affärsplan-meny
    with st.sidebar.expander("Affärsplan", expanded=False):
        st.page_link(
            "pages/3_affarsplan_sammanfattning.py", label="1. Sammanfattning"
        )
        st.page_link(
            "pages/3_affarsplan_ide.py", label="2. Affärsidé och vision"
        )
        st.page_link(
            "pages/3_affarsplan_foretag.py", label="3. Företagsbeskrivning"
        )
        st.page_link(
            "pages/3_affarsplan_marknad.py", label="4. Marknad och bransch"
        )
        st.page_link(
            "pages/3_affarsplan_forsaljning.py",
            label="5. Marknadsföring och försäljning",
        )
        st.page_link(
            "pages/3_affarsplan_organisation.py",
            label="6. Organisation och personal",
        )
        st.page_link(
            "pages/3_affarsplan_produkter.py", label="7. Produkter eller tjänster"
        )
        st.page_link("pages/3_affarsplan_ekonomi.py", label="8. Ekonomisk plan")

    if st.sidebar.button("Logga ut"):
        st.session_state.logged_in = False
        st.rerun()

    # Startsida innehåll
    st.title("Jimotec AB – Startsida")
    st.success(
        f"Välkommen {st.session_state.get('anvandarnamn', '')}! Du är nu inloggad."
    )

    st.write("---")
    st.subheader("📁 Google Drive – Dokument & Filer")
    st.info("Klicka på knappen nedan för att öppna Jimotecs Google Drive direkt i en ny flik för att läsa eller ladda upp filer.")

    # Knapp som öppnar Google Drive direkt
    st.link_button("🚀 Öppna Jimotec Google Drive", "https://drive.google.com")
