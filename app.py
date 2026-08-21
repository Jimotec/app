import json
import os
import streamlit as st

# Konfigurera sidan
st.set_page_config(page_title="Jimotec AB", layout="wide")

# Döljer automatiska listan med sidor i sidopanelen samt anpassad styling
st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    
    /* Behållare för att placera knapparna på en rad till höger */
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
    .btn-00 { background-color: #8E44AD; } /* Lila */
    .btn-01 { background-color: #2C3E50; } /* Mörkblå/Grafit */
    .btn-02 { background-color: #27AE60; } /* Grön */
    .btn-03 { background-color: #2980B9; } /* Blå */
    .btn-04 { background-color: #16A085; } /* Teal */
    .btn-05 { background-color: #D35400; } /* Orange */
    .btn-06 { background-color: #C0392B; } /* Röd */
    .btn-07 { background-color: #34495E; } /* Stålgrå */
    .btn-08 { background-color: #E67E22; } /* Bärnsten */

    /* Styling för produkt-/verktygskort på startsidan */
    .app-card {
        background-color: #f8f9fa;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        max-width: 380px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease-in-out;
    }
    .app-card:hover {
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    .app-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        width: 100%;
        background-color: #1f2937;
        color: #ffffff !important;
        font-weight: 600;
        font-size: 1rem;
        padding: 12px 18px;
        border-radius: 8px;
        text-decoration: none !important;
        margin-top: 15px;
        transition: background-color 0.2s ease-in-out;
    }
    .app-btn:hover {
        background-color: #374151;
        color: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

FILNAMN = "users.json"


def ladda_anvandare():
    if os.path.exists(FILNAMN):
        with open(FILNAMN, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"admin": "12"}


anvandare_dict = ladda_anvandare()

# Logotyp
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

# Inloggningsstatus
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
    # Sidopanel
    if logo_file:
        st.sidebar.image(logo_file, width=150)

    st.sidebar.title("Meny")
    st.sidebar.page_link("app.py", label="Startsida")

    # Hjälpfunktion för att länka utan krasch
    def try_page_link(path, label):
        if os.path.exists(path):
            st.page_link(path, label=label)
        else:
            st.caption(f"📄 {label} *(saknas)*")

    # 1. Jimotec
    with st.sidebar.expander("Jimotec", expanded=False):
        try_page_link("pages/0_jimotec.py", "Dokument & Filer")

    # 2. Mötesprotokoll
    with st.sidebar.expander("Mötesprotokoll", expanded=False):
        try_page_link("pages/6_motesprotokoll.py", "Mötesprotokoll")

    # 3. Vision
    with st.sidebar.expander("Vision", expanded=False):
        try_page_link("pages/4_vision.py", "Vision")

    # 4. Affärsplan
    with st.sidebar.expander("Affärsplan", expanded=False):
        try_page_link(
            "pages/3_affarsplan_sammanfattning.py", "1. Sammanfattning"
        )
        try_page_link("pages/3_affarsplan_ide.py", "2. Affärsidé och vision")
        try_page_link("pages/3_affarsplan_foretag.py", "3. Företagsbeskrivning")
        try_page_link("pages/3_affarsplan_marknad.py", "4. Marknad och bransch")
        try_page_link(
            "pages/3_affarsplan_forsaljning.py",
            "5. Marknadsföring och försäljning",
        )
        try_page_link(
            "pages/3_affarsplan_organisation.py",
            "6. Organisation och personal",
        )
        try_page_link(
            "pages/3_affarsplan_produkter.py", "7. Produkter eller tjänster"
        )
        try_page_link("pages/3_affarsplan_ekonomi.py", "8. Ekonomisk plan")
        try_page_link("pages/3_affarsplan_riskanalys.py", "9. Riskanalys")
        try_page_link(
            "pages/3_affarsplan_genomforandeplan.py", "10. Genomförandeplan"
        )

    if st.sidebar.button("Logga ut"):
        st.session_state.logged_in = False
        st.rerun()

    # Startsida innehåll
    col_titel, col_knappar = st.columns([1, 2.5])

    with col_titel:
        st.title("Jimotec AB")
        st.success(f"Inloggad som: **{st.session_state.get('anvandarnamn', '')}**")

    with col_knappar:
        # Små färgade knappar samlade på rad till höger
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

    # Applikationer & Verktyg på startsidan
    st.subheader("🛠️ Interna Verktyg & Produkter")

    col_app1, _ = st.columns([1, 2])

    with col_app1:
        st.markdown(
            """
            <div class="app-card">
                <h3 style="margin-top: 0; color: #1e293b;">📑 Bearbeta PDF</h3>
                <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 0;">
                    Verktyg för ritnings- och pdf-bearbetning.
                </p>
                <a href="http://100.90.128.75:8501/" target="_blank" class="app-btn">
                    ⚙️ Öppna Bearbeta PDF
                </a>
            </div>
            """,
            unsafe_allow_html=True,
        )
