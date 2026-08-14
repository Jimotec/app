import io
import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import streamlit as st

# Konfigurera sidan
st.set_page_config(page_title="Jimotec AB", layout="wide")

# Dölj den automatiska listan med sidor i sidopanelen helt
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


# Hjälpfunktion för säkra sidlänkar i rätt container
def safe_page_link(page_path, label, container=st.sidebar):
    try:
        container.page_link(page_path, label=label)
    except Exception:
        container.warning(f"Sidan saknas: {label}")


# Hjälpfunktion för uppladdning till Google Drive (Service Account)
def spara_till_google_drive(uploaded_file):
    folder_id = "1kRIqLxosFRv7E9-rdtKN_ECGtoLCy1yw"
    try:
        # Skapar uppkoppling via robotkontot i st.secrets
        info = st.secrets["gcp_service_account"]
        creds = service_account.Credentials.from_service_account_info(
            info, scopes=["https://www.googleapis.com/auth/drive"]
        )
        service = build("drive", "v3", credentials=creds)

        file_metadata = {
            "name": uploaded_file.name,
            "parents": [folder_id],
        }

        media = MediaIoBaseUpload(
            io.BytesIO(uploaded_file.getvalue()),
            mimetype=uploaded_file.type or "application/octet-stream",
            resumable=True,
        )

        service.files().create(
            body=file_metadata, media_body=media, fields="id"
        ).execute()

        return True
    except Exception as e:
        st.error(f"Ett fel uppstod vid uppladdning till Google Drive: {e}")
        return False


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

    # 1. Vision & AI
    vision_exp = st.sidebar.expander("Vision", expanded=False)
    safe_page_link("pages/4_vision.py", "Vision & AI", container=vision_exp)

    # 2. Möten
    mote_exp = st.sidebar.expander("Möten", expanded=False)
    safe_page_link(
        "pages/6_motesprotokoll.py", "Mötesprotokoll", container=mote_exp
    )

    # 3. Affärsplan
    affarsplan_exp = st.sidebar.expander("Affärsplan", expanded=False)
    safe_page_link(
        "pages/3_affarsplan_sammanfattning.py",
        "1. Sammanfattning",
        container=affarsplan_exp,
    )
    safe_page_link(
        "pages/3_affarsplan_ide.py",
        "2. Affärsidé och vision",
        container=affarsplan_exp,
    )
    safe_page_link(
        "pages/3_affarsplan_foretag.py",
        "3. Företagsbeskrivning",
        container=affarsplan_exp,
    )
    safe_page_link(
        "pages/3_affarsplan_marknad.py",
        "4. Marknad och bransch",
        container=affarsplan_exp,
    )
    safe_page_link(
        "pages/3_affarsplan_forsaljning.py",
        "5. Marknadsföring och försäljning",
        container=affarsplan_exp,
    )
    safe_page_link(
        "pages/3_affarsplan_organisation.py",
        "6. Organisation och personal",
        container=affarsplan_exp,
    )
    safe_page_link(
        "pages/3_affarsplan_produkter.py",
        "7. Produkter eller tjänster",
        container=affarsplan_exp,
    )
    safe_page_link(
        "pages/3_affarsplan_genomforandeplan.py",
        "8. Genomförandeplan",
        container=affarsplan_exp,
    )
    safe_page_link(
        "pages/3_affarsplan_riskanalys.py",
        "9. Riskanalys",
        container=affarsplan_exp,
    )
    safe_page_link(
        "pages/3_affarsplan_ekonomi.py",
        "10. Ekonomisk plan",
        container=affarsplan_exp,
    )

    if st.sidebar.button("Logga ut"):
        st.session_state.logged_in = False
        st.rerun()

    # --- Huvudfältet (Mitten på sidan) ---
    st.title("Jimotec AB – Startsida")
    st.success(
        f"Välkommen {st.session_state.get('anvandarnamn', '')}! Du är nu inloggad."
    )

    st.markdown("---")

    # Centrerad uppladdningsruta
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.subheader("📁 Ladda upp dokument till Google Drive")
        st.caption(
            "Dokument som släpps här sparas direkt i mappen **02. Affärsplan & Strategi**."
        )

        uploaded_files = st.file_uploader(
            "Dra och släpp dina filer här",
            accept_multiple_files=True,
            type=["pdf", "docx", "xlsx", "pptx", "txt"],
        )

        if uploaded_files:
            for uploaded_file in uploaded_files:
                ok = spara_till_google_drive(uploaded_file)
                if ok:
                    st.success(
                        f"✅ **{uploaded_file.name}** har laddats upp till **02. Affärsplan & Strategi**!"
                    )
