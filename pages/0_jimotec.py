import os
import streamlit as st
from pypdf import PdfReader
from docx import Document

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

st.title("📂 Sammanställ dokument för AI-analys")
st.caption("Välj en mapp, läs ut all text från alla Word- och PDF-filer och kopiera texten direkt till Gemini.")

# Basmapp för dina Google Drive-kataloger
# Ändra bas-sökvägen nedan till där dina Drive-mappar ligger lokalt/monterat
BAS_SOKVAG = r"G:\Min enhet"

# Lista över standardmapparna
MAPPAR = {
    "00. Ägare": "00. Ägare",
    "01. Styrelse (Protokoll m.m.)": "01. Styrelse",
    "02. Affärsplan": "02. Affärsplan",
    "03. Möten": "03. Möten",
    "04. Rutiner": "04. Rutiner",
    "05. Kvalitet": "05. Kvalitet",
    "06. CRM & Sälj": "06. CRM & Sälj",
    "07. ERP & Produktion": "07. ERP & Prod",
    "08. HR": "08. HR",
    "Egen sökväg...": "custom"
}

vald_etikett = st.selectbox("Välj vilken mapp du vill läsa in:", list(MAPPAR.keys()))

if MAPPAR[vald_etikett] == "custom":
    aktiv_mapp = st.text_input("Ange fullständig sökväg till mappen:", value=BAS_SOKVAG)
else:
    aktiv_mapp = os.path.join(BAS_SOKVAG, MAPPAR[vald_etikett])

st.info(f"📁 **Aktiv sökväg:** `{aktiv_mapp}`")

# Funktioner för att extrahera text
def las_pdf(fil_path):
    text = ""
    try:
        reader = PdfReader(fil_path)
        for sida in reader.pages:
            sid_text = sida.extract_text()
            if sid_text:
                text += sid_text + "\n"
    except Exception as e:
        text = f"[Kunde inte läsa PDF: {e}]"
    return text

def las_docx(fil_path):
    text = ""
    try:
        doc = Document(fil_path)
        for p in doc.paragraphs:
            if p.text:
                text += p.text + "\n"
    except Exception as e:
        text = f"[Kunde inte läsa Word-dokument: {e}]"
    return text

def las_txt(fil_path):
    try:
        with open(fil_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        return f"[Kunde inte läsa textfil: {e}]"

# Knapp för att starta inläsningen
if st.button("🚀 Läs in alla dokument i mappen", type="primary"):
    if not os.path.exists(aktiv_mapp):
        st.error(f"❌ Mappen hittades inte: `{aktiv_mapp}`. Kontrollera att enheten är monterad/ansluten.")
    else:
        meddelande = st.empty()
        meddelande.info("Läser in och bearbetar dokument...")

        samlad_text = []
        antal_filer = 0

        for rot, mappar, filer in os.walk(aktiv_mapp):
            for fil in filer:
                full_path = os.path.join(rot, fil)
                ext = os.path.splitext(fil)[1].lower()

                fil_innehall = ""
                if ext == ".pdf":
                    fil_innehall = las_pdf(full_path)
                elif ext in [".docx", ".doc"]:
                    fil_innehall = las_docx(full_path)
                elif ext in [".txt", ".md", ".csv", ".json"]:
                    fil_innehall = las_txt(full_path)
                
                if fil_innehall.strip():
                    antal_filer += 1
                    rel_namn = os.path.relpath(full_path, aktiv_mapp)
                    samlad_text.append(f"==================================================")
                    samlad_text.append(f"DOKUMENT: {rel_namn}")
                    samlad_text.append(f"==================================================")
                    samlad_text.append(fil_innehall.strip())
                    samlad_text.append("\n")

        meddelande.empty()

        if antal_filer == 0:
            st.warning("Hittade inga läsbara PDF-, Word- eller textfiler i vald mapp.")
        else:
            komplett_text = "\n".join(samlad_text)
            st.session_state.inlast_text = komplett_text
            st.session_state.antal_filer = antal_filer
            st.success(f"✅ Inläsning klar! Läste in **{antal_filer}** dokument.")

# Visa resultatet och kopieringsruta om data finns inläst
if "inlast_text" in st.session_state and st.session_state.inlast_text:
    st.write("---")
    st.subheader("📋 Sammanställd text")
    st.caption("Klicka på kopieringsikonen uppe till höger i textrutan nedan eller markera allt och klistra in i Gemini:")

    st.text_area(
        label=f"All fakta från {st.session_state.get('antal_filer', 0)} filer:",
        value=st.session_state.inlast_text,
        height=350
    )
    
    # Knapp för att ladda ner hela underlaget som en samlad textfil om man vill
    st.download_button(
        label="💾 Ladda ner allt som en .txt-fil",
        data=st.session_state.inlast_text,
        file_name=f"sammanstallning_{vald_etikett.replace(' ', '_')}.txt",
        mime="text/plain"
    )
