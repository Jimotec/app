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


def ladda_anvandare():
    if os.path.exists(FILNAMN):
        try:
            with open(FILNAMN, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"admin": "12"}
    return {"admin": "12"}


anvandare_dict = ladda_anvandare()


def henta_logo_path():
    sökvägar = [
        "Jimotec.jpg",
        "jimotec.jpg",
        "Jimotec.JPG",
        "jimotec.JPG",
        "Jimotec.png",
        "jimotec.png",
        "../Jimotec.jpg",
        "../jimotec.jpg",
    ]
    for path in sökvägar:
        if os.path.exists(path):
            return path
    return None


logo_path = henta_logo_path()

# Inloggningslogik
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    if logo_path:
        st.image(logo_path, width=220)

    st.title("🔒 Inloggning")
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
    # Loggan överst i sidopanelen
    if logo_path:
        st.sidebar.image(logo_path, use_container_width=True)
        st.sidebar.divider()

    st.sidebar.title("Meny")

    # Använd st.page_link direkt för att säkerställa att länkarna alltid visas
    st.sidebar.page_link("app.py", label="Startsida")

    # 1. Admin-meny
    with st.sidebar.expander("Admin", expanded=False):
        st.page_link("pages/1_start_admin.py", label="Admin Start")
        st.page_link("pages/2_sida_password.py", label="Hantera lösenord")

    # 2. Jimotec-meny
    with st.sidebar.expander("Jimotec", expanded=False):
        st.page_link("pages/4_jimotec_miro.py", label="Miro-analys")

    # 3. Jimotec med AI-meny
    with st.sidebar.expander("Jimotec med AI", expanded=True):
        st.page_link("pages/6_motesprotokoll.py", label="Mötesprotokoll")

    # 4. Vision-meny
    with st.sidebar.expander("Vision", expanded=False):
        st.page_link("pages/4_vision.py", label="Vision & AI")
        st.page_link("pages/5_jimotec_ai.py", label="AI")

    # 5. Affärsplan-meny
    with st.sidebar.expander("Affärsplan", expanded=False):
        st.page_link("pages/3_affarsplan_sammanfattning.py", label="1. Sammanfattning")
        st.page_link("pages/3_affarsplan_ide.py", label="2. Affärsidé och vision")
        st.page_link("pages/3_affarsplan_foretag.py", label="3. Företagsbeskrivning")
        st.page_link("pages/3_affarsplan_produkter.py", label="4. Produkter eller tjänster")
        st.page_link("pages/3_affarsplan_marknad.py", label="5. Marknad och bransch")
        st.page_link("pages/3_affarsplan_forsaljning.py", label="6. Marknadsföring och försäljning")
        st.page_link("pages/3_affarsplan_organisation.py", label="7. Organisation och personal")
        st.page_link("pages/3_affarsplan_riskanalys.py", label="8. Riskanalys och hantering")
        st.page_link("pages/3_affarsplan_genomforandeplan.py", label="9. Genomförandeplan")
        st.page_link("pages/3_affarsplan_ekonomi.py", label="10. Ekonomisk plan")

    st.sidebar.divider()
    if st.sidebar.button("Logga ut"):
        st.session_state.logged_in = False
        st.rerun()

    # Innehåll på Startsidan
    st.success(
        f"Välkommen {st.session_state.get('anvandarnamn', '')}! Du är nu inloggad."
    )
