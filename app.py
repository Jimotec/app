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
            if anvandarnamn in anvandare_dict and anvandare_dict[anvandarnamn] == losenord:
                st.session_state["inloggad"] = True
                st.session_state["anvandare"] = anvandarnamn
                st.rerun()
            else:
                st.error("Felaktigt användarnamn eller lösenord.")
    st.stop()

# --- GOOGLE DRIVE OAUTH 2.0 FUNKTIONER ---
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_google_drive_service():
    """Hanterar OAuth 2.0-inloggning och returnerar Drive-tjänsten."""
    if "oauth_credentials" in st.session_state:
        creds = Credentials.from_authorized_user_info(st.session_state["oauth_credentials"], SCOPES)
        return build('drive', 'v3', credentials=creds)

    # Hämta sekretessuppgifter från Streamlit Secrets
    client_config = {
        "web": {
            "client_id": st.secrets["oauth"]["client_id"],
            "client_secret": st.secrets["oauth"]["client_secret"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [st.secrets["oauth"]["redirect_uri"]]
        }
    }

    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=st.secrets["oauth"]["redirect_uri"]
    )

    # Om vi har fått tillbaka en auktoriseringskod från Google i URL:en
    code = st.query_params.get("code")
    if code:
        flow.fetch_token(code=code)
        creds = flow.credentials
        st.session_state["oauth_credentials"] = json.loads(creds.to_json())
        st.query_params.clear()
        st.rerun()

    # Om användaren inte är inloggad på Google Drive än
    auth_url, _ = flow.authorization_url(prompt='consent')
    st.info("Logga in på Google Drive för att aktivera filuppladdning.")
    st.link_button("🔑 Logga in på Google Drive", auth_url)
    return None

def ladda_upp_till_drive(uploaded_file, folder_id):
    service = get_google_drive_service()
    if not service:
        return False, "Du måste logga in på Google Drive först."

    temp_path = uploaded_file.name
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        file_metadata = {
            'name': uploaded_file.name,
            'parents': [folder_id] if folder_id else []
        }
        media = MediaFileUpload(temp_path, resumable=True)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        if os.path.exists(temp_path):
            os.remove(temp_path)

        return True, file.get('id')
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return False, str(e)

# --- MENY OCH GRÄNSSNITT ---
st.sidebar.title(f"Välkommen {st.session_state['anvandare']}!")

val = st.sidebar.radio(
    "Navigera",
    [
        "Startsida",
        "01. Ledning & Styrning",
        "02. Affärsplan & Strategi",
        "03. Personal & Organisation",
        "04. Ekonomi & Administration",
        "05. Marknad & Försäljning",
        "06. Inköp & Logistik",
        "07. Produktion & Kvalitet",
        "08. IT, Säkerhet & Miljö",
        "09. Mötesprotokoll",
    ],
)

if st.sidebar.button("Logga ut"):
    st.session_state["inloggad"] = False
    st.session_state["anvandare"] = ""
    if "oauth_credentials" in st.session_state:
        del st.session_state["oauth_credentials"]
    st.rerun()

# Sidinnehåll
if val == "Startsida":
    if logo_file:
        st.image(logo_file, width=300)
    st.title("Jimotec AB - Intranät")
    st.write("Välkommen till Jimotecs interna portal. Välj en meny i sidopanelen till vänster.")

elif val == "02. Affärsplan & Strategi":
    st.title("02. Affärsplan & Strategi")
    
    st.subheader("📂 Ladda upp dokument till Google Drive")
    st.caption("Dokument som släpps här sparas direkt i meppen 02. Affärsplan & Strategi.")

    # Mapp ID för 02. Affärsplan & Strategi
    FOLDER_ID = "143g_6TllvPj_w74U-lIuA1A8q5B97j6-"

    uploaded_files = st.file_uploader("Dra och släpp dina filer här", accept_multiple_files=True)

    if uploaded_files:
        for uploaded_file in uploaded_files:
            ok, res = ladda_upp_till_drive(uploaded_file, FOLDER_ID)
            if ok:
                st.success(f"Filen **{uploaded_file.name}** har laddats upp till Google Drive!")
            else:
                st.error(f"Ett fel uppstod vid uppladdning av {uploaded_file.name}: {res}")

else:
    st.title(val)
    st.info("Denna sida är under uppbyggnad.")
