import io
import os
import streamlit as st
from pypdf import PdfReader
from docx import Document
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account

st.set_page_config(page_title="Jimotec - Dokument & Filer", layout="wide")

# Kontrollera inloggning
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Du måste logga in via startsidan först.")
    st.stop()

# Logotyp uppe till vänster
logo_file = None
for f in ["Jimotec.jpg", "jimotec.jpg", "Jimotec.png", "jimotec.png"]:
    if os.path.exists(f):
        logo_file = f
        break

if logo_file:
    st.image(logo_file, width=180)

st.title("📂 Sammanställ dokument från Google Drive")
st.caption("Välj mapp från Google Drive för att automatiskt läsa ut all text och kopiera till Gemini.")

# Mapp-ID för respektive mapp i Google Drive
MAPPAR = {
    "00. Ägare": "1Y3G3mbLjB0-yytQVrTLNqG0lUhNSJX3s",
    "01. Styrelse": "1J_f2FeSxVoh1lMwZhBhK9B2Jmtms99t5",
    "02. Affärsplan & Strategi": "1kRIqLxosFRv7E9-rdtKN_ECGtoLCy1yw",
    "03. Mötesprotokoll & Ledning": "1dlH1Vtf8o1b9qEsWnrYYxcx7W-11wQ2u",
    "04. Rutiner & Instruktioner": "1orxyLf4BUO1eIGArEleDBD2_WlHJ85oD",
    "05. Kvalitet & Avvikelser": "1qBWiM-7LKI7rKpkXFSVP2T0TSEIphq1c",
    "06. CRM & Sälj": "1K49xSjbeYKXX1P84pWTibXsl09bC3-2q",
    "07. ERP & Produktion": "1JeX24o7uWjIAiCaqWl8B89VsSDqwXX_h",
    "08. HR & Personal": "1wF99tAUAKY575OBO4kN3Ggu5L2SerF_d",
}

vald_mapp = st.selectbox("Välj mapp att sammanställa:", list(MAPPAR.keys()))
folder_id = MAPPAR[vald_mapp]

def get_drive_service():
    scopes = ["https://www.googleapis.com/auth/drive.readonly"]
    if "gcp_service_account" in st.secrets:
        creds = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=scopes
        )
    elif os.path.exists("credentials.json"):
        creds = service_account.Credentials.from_service_account_file(
            "credentials.json", scopes=scopes
        )
    else:
        return None
    return build("drive", "v3", credentials=creds)

def extrahera_text_fran_fil(service, fil):
    fil_id = fil["id"]
    fil_namn = fil["name"]
    mime_type = fil.get("mimeType", "")
    
    # 1. Google Docs -> Exportera som ren text direkt
    if mime_type == "application/vnd.google-apps.document":
        try:
            req = service.files().export_media(fileId=fil_id, mimeType="text/plain")
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, req)
            done = False
            while not done:
                _, done = downloader.next_chunk()
            return fh.getvalue().decode("utf-8", errors="ignore")
        except Exception as e:
            return f"[Kunde inte exportera Google Doc: {e}]"

    # 2. Övriga binära filer (PDF, DOCX, TXT) -> Ladda ner till minnet
    try:
        req = service.files().get_media(fileId=fil_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, req)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        fh.seek(0)
    except Exception as e:
        return f"[Kunde inte hämta filinnehåll: {e}]"

    # Extrahera baserat på filtillägg
    ext = os.path.splitext(fil_namn)[1].lower()
    text = ""
    
    if ext == ".pdf" or mime_type == "application/pdf":
        try:
            reader = PdfReader(fh)
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
        except Exception as e:
            text = f"[Kunde inte läsa PDF: {e}]"
            
    elif ext in [".docx", ".doc"]:
        try:
            doc = Document(fh)
            for p in doc.paragraphs:
                if p.text:
                    text += p.text + "\n"
        except Exception as e:
            text = f"[Kunde inte läsa DOCX: {e}]"
            
    elif ext in [".txt", ".md", ".csv", ".json"]:
        try:
            text = fh.getvalue().decode("utf-8", errors="ignore")
        except Exception as e:
            text = f"[Kunde inte avkoda textfil: {e}]"
            
    return text

if st.button("🚀 Läs in alla dokument i mappen", type="primary"):
    service = get_drive_service()
    if not service:
        st.error("❌ Saknar Google Service Account-autentisering (secrets eller credentials.json).")
    else:
        meddelande = st.empty()
        meddelande.info(f"Hämtar filer från {vald_mapp}...")

        # Hämta lista med filer i mappen
        query = f"'{folder_id}' in parents and trashed = false"
        res = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
        filer = res.get("files", [])

        samlad_text = []
        antal_dokument = 0

        for f in filer:
            text = extrahera_text_fran_fil(service, f)
            if text.strip():
                antal_dokument += 1
                samlad_text.append("==================================================")
                samlad_text.append(f"DOKUMENT: {f['name']}")
                samlad_text.append("==================================================")
                samlad_text.append(text.strip())
                samlad_text.append("\n")

        meddelande.empty()

        if antal_dokument == 0:
            st.warning(f"Inga läsbara filer hittades i {vald_mapp}.")
        else:
            st.session_state.inlast_text = "\n".join(samlad_text)
            st.session_state.antal_filer = antal_dokument
            st.success(f"✅ Klart! Läste in text från **{antal_dokument}** dokument.")

# Visa samlat resultat
if "inlast_text" in st.session_state and st.session_state.inlast_text:
    st.write("---")
    st.subheader(f"📋 Sammanställd fakta ({st.session_state.get('antal_filer', 0)} filer)")
    st.caption("Kopiera texten nedan via ikonen uppe i högra hörnet på textrutan och klistra in här i Gemini:")
    
    st.text_area(
        label="Samlad text:",
        value=st.session_state.inlast_text,
        height=400
    )
    
    st.download_button(
        label="💾 Ladda ner allt som .txt",
        data=st.session_state.inlast_text,
        file_name=f"GoogleDrive_{vald_mapp.replace(' ', '_')}.txt",
        mime="text/plain"
    )
