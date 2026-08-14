import json
import os
import streamlit as st

# Konfigurera sidan
st.set_page_config(page_title="Jimotec AB", layout="wide")

# Döljer automatiska listan med sidor i sidopanelen
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

    # 1. Mötesprotokoll
    with st.sidebar.expander("Mötesprotokoll", expanded=False):
        try_page_link("pages/6_motesprotokoll.py", "Mötesprotokoll")

    # 2. Vision
    with st.sidebar.expander("Vision", expanded=False):
        try_page_link("pages/4_vision.py", "Vision")

    # 3. Affärsplan
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
    st.title("Jimotec AB – Startsida")
    st.success(
        f"Välkommen {st.session_state.get('anvandarnamn', '')}! Du är inloggad."
    )

    st.write("---")
    st.subheader("📁 Google Drive - Dokument & Mappar")

    # Funktion för att rita ut färgkodade knappar
    def farg_knapp(lank, ikon, text, bg_color):
        st.markdown(
            f"""
        <a href="{lank}" target="_blank" style="
            display: block;
            background-color: {bg_color};
            color: white;
            text-align: left;
            padding: 14px 18px;
            border-radius: 8px;
            text-decoration: none;
            font-size: 15px;
            font-weight: bold;
            margin-bottom: 14px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.08);
            transition: transform 0.1s ease-in-out;
        ">
            <span style="font-size: 18px; margin-right: 8px;">{ikon}</span> {text}
        </a>
        """,
            unsafe_allow_html=True,
        )

    # 3-kolumn layout för knapparna
    col1, col2, col3 = st.columns(3)

    with col1:
        # 00. Ägare
        farg_knapp(
            "https://drive.google.com/drive/u/0/folders/1Y3G3mbLjB0-yytQVrTLNqG0IUhNSJX3s",
            "👑",
            "00. Ägare",
            "#c0392b",
        )
        # 03. Mötesprotokoll & Ledning
        farg_knapp(
            "https://drive.google.com/drive/u/0/folders/1dIH1Vtf8o1b9qEsWnrYYxcx7W-11wQ2u",
            "📝",
            "03. Mötesprotokoll & Ledning",
            "#8e44ad",
        )
        # 06. CRM & Sälj
        farg_knapp(
            "https://drive.google.com/drive/u/0/folders/1K49xSjbeYKXX1P84pWTibXsl09bC3-2q",
            "🤝",
            "06. CRM & Sälj",
            "#27ae60",
        )

    with col2:
        # 01. Styrelse
        farg_knapp(
            "https://drive.google.com/drive/u/0/folders/1J_f2FeSxVoh1IMwZhBhK9B2Jmtms99t5",
            "🏛️",
            "01. Styrelse",
            "#d35400",
        )
        # 04. Rutiner & Instruktioner
        farg_knapp(
            "https://drive.google.com/drive/u/0/folders/1orxyLf4BUO1eIGArEleDBD2_WlHJ85oD",
            "📋",
            "04. Rutiner & Instruktioner",
            "#16a085",
        )
        # 07. ERP & Produktion
        farg_knapp(
            "https://drive.google.com/drive/u/0/folders/1JeX24o7uWjIAiCaqWI8B89VsSDqwXX_h",
            "🏭",
            "07. ERP & Produktion",
            "#2980b9",
        )

    with col3:
        # 02. Affärsplan & Strategi
        farg_knapp(
            "https://drive.google.com/drive/u/0/folders/1kRIqLxosFRv7E9-rdtKN_ECGtoLCy1yw",
            "🚀",
            "02. Affärsplan & Strategi",
            "#2980b9",
        )
        # 05. Kvalitet & Avvikelser
        farg_knapp(
            "https://drive.google.com/drive/u/0/folders/1qBWiM-7LKI7rKpkXFSVP2T0TSEIphq1c",
            "🔎",
            "05. Kvalitet & Avvikelser",
            "#f39c12",
        )
        # 08. HR & Personal
        farg_knapp(
            "https://drive.google.com/drive/u/0/folders/1wF99tAUAKY575OBO4kN3Ggu5L2SerF_d",
            "👥",
            "08. HR & Personal",
            "#e84393",
        )
