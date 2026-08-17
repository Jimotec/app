import streamlit as st

# Konfigurera sidan
st.set_page_config(page_title="Jimotec AB - Dokument & Filer", layout="wide")

# CSS-styling för Drive-knappar och gränssnitt
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

    .info-card {
        background-color: #f8f9fa;
        border-left: 4px solid #2980b9;
        padding: 14px 18px;
        border-radius: 4px;
        margin-bottom: 20px;
        font-size: 0.92rem;
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

# Instruktionssektion för Gemini
st.subheader("🤖 Startprompt för Gemini")

st.markdown(
    """
    <div class="info-card">
        Klicka på knappen nedan för att hämta startinstruktionen. Klistra in den i Gemini <b>innan</b> du laddar upp dina dokument, så väntar Gemini in alla filer och frågar dig vad du vill ha för svar.
    </div>
    """,
    unsafe_allow_html=True,
)

gemini_start_instruction = (
    "VIKTIG INSTRUKTION TILL GEMINI:\n\n"
    "Jag kommer nu att ladda upp ett eller flera dokument/instruktioner i den här chatten.\n"
    "Du skall INTE analysera, sammanfatta, leta information eller svara på något i förväg.\n"
    "Du skall endast ta emot alla dokument och vänta tills jag har laddat upp allt.\n\n"
    "När du har tagit emot filerna skall du endast svara med följande exakta fråga:\n"
    "\"Jag har tagit emot alla dokument. Vad vill du ha för svar?\"\n\n"
    "Vänta därefter på min nästa instruktion."
)

if "show_prompt" not in st.session_state:
    st.session_state.show_prompt = False

if st.button("📋 Hämta instruktion till Gemini", type="primary"):
    st.session_state.show_prompt = True

if st.session_state.show_prompt:
    st.success("Kopiera instruktionen från rutan nedan och klistra in den till Gemini:")
    st.code(gemini_start_instruction, language="markdown")
