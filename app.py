import json
import os
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


# Hjälpfunktion för uppladdning till Google Drive
def spara_till_google_drive(uploaded_file):
    """Här kopplas din Google Drive-integration.

    Exempelvis med google-api-python-client eller PyDrive2 till mappen '02.
    Affärsplan & Strategi'.
    """
    # Exempel: ID för mappen "02. Affärsplan & Strategi" i Google Drive
    FOLDER_ID = "DIN_GOOGLE_DRIVE_FOLDER_ID"

    # För tillfället sparar vi filen lokalt eller visar bekräftelse.
    # När dina API-nycklar/Service Account är inlagda skickas filen hit.
    return True


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
        f"Välkommen {st.session_state.get('anvandarnamn', '')}! Du är nu"
        " inloggad."
    )

    st.markdown("---")

    # Centrerad uppladdningsruta
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.subheader("📁 Ladda upp dokument till Google Drive")
        st.caption(
            "Dokument som släpps här sparas direkt i mappen **02. Affärsplan &"
            " Strategi**."
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
                        f"✅ **{uploaded_file.name}** har laddats upp till **02."
                        " Affärsplan & Strategi**!"
                    )
                else:
                    st.error(
                        f"❌ Det gick inte att ladda upp {uploaded_file.name}."
                import json
import os
import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

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

# Håll koll på inloggningsstatus
if "inloggad" not in st.session_state:
    st.session_state["inloggad"] = False
    st.session_state["anvandare"] = ""

# Formulär för inloggning i appen
if not st.session_state["inloggad"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if logo_file:
            st.image(logo_file, width=250)
        st.title("Jimotec AB - Intranät")
        st.subheader("Logga in")

        anvandarnamn = st.text_input("Användarnamn")
        losenord = st.text_input("Lösenord", type="password")

        if st.button("Logga in", type="primary"):
            if (
                anvandarnamn in anvandare_dict
                and anvandare_dict[anvandarnamn] == losenord
            ):
                st.session_state["inloggad"] = True
                st.session_state["anvandare"] = anvandarnamn
                st.rerun()
            else:
                st.error("Felaktigt användarnamn eller lösenord.")
    st.stop()


# Hjälpfunktion för säkra sidlänkar
def safe_page_link(page_path, label, container=st.sidebar):
    if os.path.exists(page_path):
        container.page_link(page_path, label=label)
    else:
        container.warning(f"Sidan saknas: {label}")


# --- Hjälpfunktion för uppladdning till Google Drive via OAuth ---
def spara_till_google_drive(uploaded_file):
    FOLDER_ID = "1kRIqLxosFRv7E9-rdtKN_ECGtoLCy1yw"
    SCOPES = ["https://www.googleapis.com/auth/drive.file"]

    # Om vi redan har OAuth-credentials sparade i sessionen
    if "oauth_credentials" in st.session_state:
        creds = Credentials.from_authorized_user_info(
            st.session_state["oauth_credentials"], SCOPES
        )
        service = build("drive", "v3", credentials=creds)
    else:
        # Konfigurera OAuth från Streamlit Secrets
        client_config = {
            "web": {
                "client_id": st.secrets["oauth"]["client_id"],
                "client_secret": st.secrets["oauth"]["client_secret"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [st.secrets["oauth"]["redirect_uri"]],
            }
        }
        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=st.secrets["oauth"]["redirect_uri"],
        )

        code = st.query_params.get("code")
        if code:
            flow.fetch_token(code=code)
            creds = flow.credentials
            st.session_state["oauth_credentials"] = json.loads(creds.to_json())
            st.query_params.clear()
            st.rerun()

        auth_url, _ = flow.authorization_url(prompt="consent")
        st.info("Logga in på Google Drive för att aktivera filuppladdning.")
        st.link_button("🔑 Logga in på Google Drive", auth_url)
        return False

    temp_path = f"temp_{uploaded_file.name}"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        file_metadata = {"name": uploaded_file.name, "parents": [FOLDER_ID]}
        media = MediaFileUpload(temp_path, resumable=True)
        service.files().create(
            body=file_metadata, media_body=media, fields="id"
        ).execute()

        if os.path.exists(temp_path):
            os.remove(temp_path)
        return True
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        st.error(f"Ett fel uppstod vid uppladdning till Google Drive: {e}")
        return False


# --- Sidonavigering (Sidopanelen) ---
st.sidebar.title(f"Välkommen {st.session_state['anvandare']}!")

safe_page_link("app.py", "Startsida")
safe_page_link("pages/1_ledning.py", "01. Ledning & Styrning")
safe_page_link("pages/2_affarsplan.py", "02. Affärsplan & Strategi")
safe_page_link("pages/3_personal.py", "03. Personal & Organisation")
safe_page_link("pages/4_ekonomi.py", "04. Ekonomi & Administration")
safe_page_link("pages/5_marknad.py", "05. Marknad & Försäljning")
safe_page_link("pages/6_inkop.py", "06. Inköp & Logistik")
safe_page_link("pages/7_produktion.py", "07. Produktion & Kvalitet")
safe_page_link("pages/8_it.py", "08. IT, Säkerhet & Miljö")
safe_page_link("pages/9_motesprotokoll.py", "09. Mötesprotokoll")

st.sidebar.markdown("---")

if st.sidebar.button("Logga ut"):
    st.session_state["inloggad"] = False
    st.session_state["anvandare"] = ""
    if "oauth_credentials" in st.session_state:
        del st.session_state["oauth_credentials"]
    st.rerun()

# --- Huvudfältet (Startsidan) ---
if logo_file:
    st.image(logo_file, width=250)

st.title("Jimotec AB - Intranät")
st.write(
    "Välkommen till Jimotecs interna portal. Välj en meny i sidopanelen till vänster."
)
