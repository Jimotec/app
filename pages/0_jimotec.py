import os
import streamlit as st
from docx import Document
import pypdf

# Konfigurera sidan
st.set_page_config(page_title="Jimotec AB - Dokument & Filer", layout="wide")

# CSS-styling för knappar och behållare
st.markdown(
    """
    <style>
    /* Behållare för Drive-knappar */
    .drive-buttons-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: flex-end;
        align-items: center;
        gap: 6px;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    
    /* Kompakt styling för varje Drive-knapp */
    .drive-btn {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 5px 10px;
        font-size: 0.78rem;
        font-weight: 600;
        color: #ffffff !important;
        text-decoration: none !important;
        border-radius: 6px;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        white-space: nowrap;
    }
    
    .drive-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 3px 6px rgba(0,0,0,0.2);
        opacity: 0.92;
        color: #ffffff !important;
    }

    /* Specifika färger per mapp */
    .btn-00 { background-color: #8E44AD; }
    .btn-01 { background-color: #2C3E50; }
    .btn-02 { background-color: #27AE60; }
    .btn-03 { background-color: #2980B9; }
    .btn-04 { background-color: #16A085; }
    .btn-05 { background-color: #D35400; }
    .btn-06 { background-color: #C0392B; }
    .btn-07 { background-color: #34495E; }
    .btn-08 { background-color: #E67E22; }

    .instruction-box {
        background-color: #f8f9fa;
        border-left: 4px solid #16a085;
        padding: 12px 16px;
        border-radius: 4px;
        margin: 10px 0 20px 0;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidhuvud med rubrik och Drive-knappar
col_titel, col_knappar = st.columns([1, 2.5])

with col_titel:
    st.title("📁 Dokument & Filer")

with col_knappar:
    st.markdown(
        """
        <div class="drive-buttons-container">
            <a href="https://drive.google.com/drive/folders/1Y3G3mbLjB0-yytQVrTLNqG0lUhNSJX3s?usp=drive_link" target="_blank" class="drive-btn btn-00">👑 00. Ägare</a>
            <a href="https://drive.google.com/drive/folders/1J_f2FeSxVoh1lMwZhBhK9B2Jmtms99t5?usp=drive_link" target="_blank" class="drive-btn btn-01">🏛️ 01. Styrelse</a>
            <a href="https://drive.google.com/drive/folders/1kRIqLxosFRv7E9-rdtKN_ECGtoLCy1yw" target="_blank" class="drive-btn btn-02">🚀 02. Affärsplan</a>
            <a href="https://drive.google.com/drive/folders/1dlH1Vtf8o1b9qEsWnrYYxcx7W-11wQ2u?usp=drive_link" target="_blank" class="drive-btn btn-03">📝 03. Möten</a>
            <a href="https://drive.google.com/drive/folders/1orxyLf4BUO1eIGArEleDBD2_WlHJ85oD?usp=drive_link" target="_blank" class="drive-btn btn-04">📋 04. Rutiner</a>
            <a href="https://drive.google.com/drive/folders/1qBWiM-7LKI7rKpkXFSVP2T0TSEIphq1c?usp=drive_link" target="_blank" class="drive-btn btn-05">🔎 05. Kvalitet</a>
            <a href="https://drive.google.com/drive/folders/1K49xSjbeYKXX1P84pWTibXsl09bC3-2q?usp=drive_link" target="_blank" class="drive-btn btn-06">🤝 06. CRM & Sälj</a>
            <a href="https://drive.google.com/drive/folders/1JeX24o7uWjIAiCaqWl8B89VsSDqwXX_h?usp=drive_link" target="_blank" class="drive-btn btn-07">🏭 07. ERP & Prod</a>
            <a href="https://drive.google.com/drive/folders/1wF99tAUAKY575OBO4kN3Ggu5L2SerF_d?usp=drive_link" target="_blank" class="drive-btn btn-08">👥 08. HR</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("---")

# Funktioner för att läsa text ur uppladdade filer
def extract_text(uploaded_file):
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    text = ""
    try:
        if ext == ".txt":
            text = uploaded_file.read().decode("utf-8", errors="ignore")
        elif ext == ".docx":
            doc = Document(uploaded_file)
            text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        elif ext == ".pdf":
            reader = pypdf.PdfReader(uploaded_file)
            pages_text = [page.extract_text() for page in reader.pages if page.extract_text()]
            text = "\n".join(pages_text)
    except Exception as e:
        text = f"[Kunde inte läsa {uploaded_file.name}: {e}]"
    return text

# Sektion: Gemini Uppladdnings- och analyscenter
st.subheader("🤖 Dokumentberedning för Gemini")

st.markdown(
    """
    <div class="instruction-box">
        <b>Arbetsflöde:</b> Ladda upp ett eller flera dokument nedan (.pdf, .docx, .txt). 
        När alla filer är inlästa klickar du på knappen för att generera hela paketet och instruktionstexten som instruerar Gemini att bekräfta mottagandet och invänta din specifika fråga.
    </div>
    """,
    unsafe_allow_html=True,
)

# Instruktionstexten till Gemini
STANDARD_INSTRUCTION = (
    "VIKTIG INSTRUKTION TILL GEMINI:\n"
    "Jag har bifogat/klistrat in flera dokument här. Gör inga egna antaganden eller analyser direkt.\n"
    "Läs in och bekräfta endast att du har tagit emot alla dokumenten.\n"
    "Avsluta ditt svar med att fråga mig:\n"
    "'Jag har tagit emot alla dokument. Vad vill du ha för svar?'\n"
    "Invänta sedan mina specifika instruktioner."
)

uploaded_files = st.file_uploader(
    "Välj alla dokument som ska bearbetas:",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True
)

if uploaded_files:
    st.success(f"Totalt **{len(uploaded_files)}** dokument valda.")
    
    if st.button("🚀 Skapa färdigt Gemini-paket med instruktioner", type="primary"):
        with st.spinner("Läser in dokument..."):
            sammanställd_text = STANDARD_INSTRUCTION + "\n\n" + "=" * 50 + "\n\n"
            
            for f in uploaded_files:
                f.seek(0)
                content = extract_text(f)
                sammanställd_text += f"--- DOKUMENT: {f.name} ---\n"
                sammanställd_text += content + "\n\n"
            
            st.session_state["gemini_payload"] = sammanställd_text

if "gemini_payload" in st.session_state:
    st.write("### 📋 Färdig prompt för Gemini")
    st.caption("Kopiera texten nedan eller ladda ner som en fil att bifoga direkt i chatten:")
    
    st.code(st.session_state["gemini_payload"][:1200] + "\n\n[... resterande dokumentinnehåll ingår i kopieringen/filen ...]", language="markdown")
    
    col_copy, col_download = st.columns([1, 1])
    with col_download:
        st.download_button(
            label="💾 Ladda ner komplett underlag (.txt)",
            data=st.session_state["gemini_payload"],
            file_name="gemini_underlag_jimotec.txt",
            mime="text/plain",
            use_container_width=True
        )
