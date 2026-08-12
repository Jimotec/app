import io
import json
import os
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

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

# ID för mappen "02. Affärsplan & Strategi" i Google Drive
FOLDER_ID_AFFARSPLAN = "DIN_MAPP_ID_HÄR"

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


# Funktion för att koppla upp mot Google Drive API
def upload_to_drive(uploaded_file, folder_id):
  SCOPES = ["https://www.googleapis.com/auth/drive.file"]
  creds_dict = dict(st.secrets["gcp_service_account"])
  creds = service_account.Credentials.from_service_account_info(
      creds_dict, scopes=SCOPES
  )
  service = build("drive", "v3", credentials=creds)

  file_metadata = {"name": uploaded_file.name, "parents": [folder_id]}
  media = MediaIoBaseUpload(
      io.BytesIO(uploaded_file.getvalue()),
      mimetype=uploaded_file.type,
      resumable=True,
  )

  file = (
      service.files()
      .create(body=file_metadata, media_body=media, fields="id")
      .execute()
  )
  return file.get("id")


# Inloggningslogik
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False

if not st.session_state.logged_in:
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
  if logo_file:
    st.sidebar.image(logo_file, width=150)
  st.sidebar.title("Meny")

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
    st.page_link("pages/3_affarsplan_ide.py", label="2. Affärsidé och vision")
    st.page_link("pages/3_affarsplan_foretag.py", label="3. Företagsbeskrivning")
    st.page_link(
        "pages/3_affarsplan_marknad.py", label="4. Marknad och bransch"
    )
    st.page_link(
        "pages/3_affarsplan_forsaljning.py",
        label="5. Marknadsföring och försäljning",
    )
    st.page_link(
        "pages/3_affarsplan_organisation.py", label="6. Organisation och personal"
    )
    st.page_link(
        "pages/3_affarsplan_produkter.py", label="7. Produkter eller tjänster"
    )
    st.page_link("pages/3_affarsplan_ekonomi.py", label="8. Ekonomisk plan")

  if st.sidebar.button("Logga ut"):
    st.session_state.logged_in = False
    st.rerun()

  # -------------------- STARTSIDA & OPPLADDNING --------------------
  st.title("Jimotec AB – Startsida")
  st.success(
      f"Välkommen {st.session_state.get('anvandarnamn', '')}! Du är nu"
      " inloggad."
  )

  st.divider()

  # Släpp-ruta för uppladdning till Drive
  st.subheader(
      "📁 Ladda upp dokument till: [02. Affärsplan & Strategi]"
  )  #
  uploaded_files = st.file_uploader(
      "Dra och släpp filer här (PDF, Word, Excel osv.):",
      accept_multiple_files=True,
  )

  if uploaded_files and st.button("Ladda upp till Google Drive"):
    for uploaded_file in uploaded_files:
      try:
        file_id = upload_to_drive(uploaded_file, FOLDER_ID_AFFARSPLAN)
        st.success(
            f"✅ Filen '{uploaded_file.name}' laddades upp till Drive!"
        )
      except Exception as e:
        st.error(f"❌ Fel vid uppladdning av {uploaded_file.name}: {e}")
