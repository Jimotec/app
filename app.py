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
        try:
            with open(FILNAMN, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"admin": "12"}
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

    # Hjälpfunktion för att länka säkert utan att appen kraschar om en fil saknas
    def sakert_link(sökväg, etikett):
        if os.path.exists(sökväg):
            st.page_link(sökväg, label=etikett)

    # Huvudlänk för startsidan
    sakert_link("app.py", "Startsida")

    # 1. Admin-meny
    with st.sidebar.expander("Admin", expanded=False):
        sakert_link("pages/1_start_admin.py", "Admin Start")
        sakert_link("pages/2_sida_password.py", "Hantera lösenord")

    # 2. Jimotec-meny
    with st.sidebar.expander("Jimotec", expanded=False):
        sakert_link("pages/4_jimotec_miro.py", "Miro-analys")

    # 3. Vision-meny
    with st.sidebar.expander("Vision", expanded=False):
        sakert_link("pages/5_jimotec_ai.py", "AI")

    # 4. Affärsplan-meny
    with st.sidebar.expander("Affärsplan", expanded=False):
        sakert_link("pages/3_affarsplan_sammanfattning.py", "1. Sammanfattning")
        sakert_link("pages/3_affarsplan_ide.py", "2. Affärsidé och vision")
        sakert_link("pages/3_affarsplan_foretag.py", "3. Företagsbeskrivning")
        sakert_link("pages/3_affarsplan_marknad.py", "4. Marknad och bransch")
        sakert_link("pages/3_affarsplan_forsaljning.py", "5. Marknadsföring och försäljning")
        sakert_link("pages/3_affarsplan_organisation.py", "6. Organisation och personal")
        sakert_link("pages/3_affarsplan_produkter.py", "7. Produkter eller tjänster")
        sakert_link("pages/3_affarsplan_ekonomi.py", "8. Ekonomisk plan")

    st.sidebar.divider()
    if st.sidebar.button("Logga ut"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("Jimotec AB – Startsida")
    st.success(
        f"Välkommen {st.session_state.get('anvandarnamn', '')}! Du är nu inloggad."
    )
