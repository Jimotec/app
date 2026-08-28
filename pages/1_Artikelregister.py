import streamlit as st
import os
import re
import pandas as pd

# Konfigurera sidan
st.set_page_config(page_title="Artikelregister - Jimotec AB", layout="wide")

# CSS för stil och Drive-knappar
st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    .drive-buttons-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: flex-end;
        align-items: center;
        gap: 6px;
        margin-top: 5px;
        margin-bottom: 15px;
    }
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
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        white-space: nowrap;
    }
    .btn-00 { background-color: #8E44AD; }
    .btn-01 { background-color: #2C3E50; }
    .btn-02 { background-color: #27AE60; }
    .btn-03 { background-color: #2980B9; }
    .btn-04 { background-color: #16A085; }
    .btn-05 { background-color: #D35400; }
    .btn-06 { background-color: #C0392B; }
    .btn-07 { background-color: #34495E; }
    .btn-08 { background-color: #E67E22; }

    .art-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sökvägar till artikelregistret
REMOTE_PATH = r"Y:\Artikelregister"
LOCAL_PATH = r"C:\Jimotec\Kund pdf\Klara_Beredningar"
REGISTER_PATH = REMOTE_PATH if os.path.exists(REMOTE_PATH) else LOCAL_PATH

# Logotyp och sidomeny
logo_file = None
for f in ["jimotec.jpg", "Jimotec.jpg", "jimotec.png", "Jimotec.png"]:
    if os.path.exists(f):
        logo_file = f
        break

if logo_file:
    st.sidebar.image(logo_file, width=150)

st.sidebar.title("Meny")
st.sidebar.page_link("app.py", label="Startsida")

def try_page_link(path, label):
    if os.path.exists(path):
        st.page_link(path, label=label)
    else:
        st.caption(f"📄 {label} *(saknas)*")

with st.sidebar.expander("Jimotec", expanded=True):
    try_page_link("pages/0_jimotec.py", "Dokument & Filer")
    try_page_link("pages/1_Artikelregister.py", "Artikelregister")
    try_page_link("pages/2_Sammanstallning_artikel.py", "Sammanställning Artikel")

with st.sidebar.expander("Mötesprotokoll", expanded=False):
    try_page_link("pages/6_motesprotokoll.py", "Mötesprotokoll")

# Topprad
col_head, col_drives = st.columns([1.2, 2.8])
with col_head:
    st.title("📦 Artikelregister")
    st.caption(f"Aktiv sökväg: `{REGISTER_PATH}`")

with col_drives:
    st.markdown(
        """
        <div class="drive-buttons-container">
            <a href="https://drive.google.com/drive/folders/1Y3G3mbLjB0-yytQVrTLNqG0lUhNSJX3s" target="_blank" class="drive-btn btn-00">👑 00. Ägare</a>
            <a href="https://drive.google.com/drive/folders/1J_f2FeSxVoh1lMwZhBhK9B2Jmtms99t5" target="_blank" class="drive-btn btn-01">🏛️ 01. Styrelse</a>
            <a href="https://drive.google.com/drive/folders/1kRIqLxosFRv7E9-rdtKN_ECGtoLCy1yw" target="_blank" class="drive-btn btn-02">🚀 02. Affärsplan</a>
            <a href="https://drive.google.com/drive/folders/1dlH1Vtf8o1b9qEsWnrYYxcx7W-11wQ2u" target="_blank" class="drive-btn btn-03">📝 03. Möten</a>
            <a href="https://drive.google.com/drive/folders/1orxyLf4BUO1eIGArEleDBD2_WlHJ85oD" target="_blank" class="drive-btn btn-04">📋 04. Rutiner</a>
            <a href="https://drive.google.com/drive/folders/1qBWiM-7LKI7rKpkXFSVP2T0TSEIphq1c" target="_blank" class="drive-btn btn-05">🔎 05. Kvalitet</a>
            <a href="https://drive.google.com/drive/folders/1K49xSjbeYKXX1P84pWTibXsl09bC3-2q" target="_blank" class="drive-btn btn-06">🤝 06. CRM & Sälj</a>
            <a href="https://drive.google.com/drive/folders/1JeX24o7uWjIAiCaqWl8B89VsSDqwXX_h" target="_blank" class="drive-btn btn-07">🏭 07. ERP & Prod</a>
            <a href="https://drive.google.com/drive/folders/1wF99tAUAKY575OBO4kN3Ggu5L2SerF_d" target="_blank" class="drive-btn btn-08">👥 08. HR</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("---")

# Hjälpfunktion för att läsa underlag från en artikelmapp
def parse_underlag(folder_path):
    txt_file = os.path.join(folder_path, "Underlag_Beredning.txt")
    info = {
        "Jimotec Artnr": os.path.basename(folder_path),
        "Benämning": "-",
        "Ritningsnr": "-",
        "Revision": "-",
        "Material": "-"
    }
    if os.path.exists(txt_file):
        try:
            with open(txt_file, "r", encoding="utf-8") as f:
                content = f.read()
                m_art = re.search(r"Jimotec Artnr:\s*(.*)", content)
                m_ben = re.search(r"Benämning:\s*(.*)", content)
                m_rit = re.search(r"Ritningsnr:\s*(.*)", content)
                m_rev = re.search(r"Revision:\s*(.*)", content)
                m_mat = re.search(r"Material:\s*(.*)", content)
                
                if m_art: info["Jimotec Artnr"] = m_art.group(1).strip()
                if m_ben: info["Benämning"] = m_ben.group(1).strip()
                if m_rit: info["Ritningsnr"] = m_rit.group(1).strip()
                if m_rev: info["Revision"] = m_rev.group(1).strip()
                if m_mat: info["Material"] = m_mat.group(1).strip()
        except Exception:
            pass
    return info

# Hämta alla artiklar
articles = []
if os.path.exists(REGISTER_PATH):
    for item in sorted(os.listdir(REGISTER_PATH)):
        item_path = os.path.join(REGISTER_PATH, item)
        if os.path.isdir(item_path):
            articles.append(parse_underlag(item_path))

# Sökruta
col_search, col_stats = st.columns([3, 1])
with col_search:
    search_query = st.text_input("🔍 Sök på Artikelnummer, Benämning, Ritningsnummer eller Material:", placeholder="T.ex. 4-210, Hållare, A1038867, PE300...")
with col_stats:
    st.metric("Totalt antal artiklar", len(articles))

# Filtrera resultat
filtered_articles = articles
if search_query:
    q = search_query.lower()
    filtered_articles = [
        a for a in articles
        if q in a["Jimotec Artnr"].lower()
        or q in a["Benämning"].lower()
        or q in a["Ritningsnr"].lower()
        or q in a["Material"].lower()
    ]

st.markdown(f"**Visar {len(filtered_articles)} st artiklar**")

# Visa artiklar med knapp som öppnar sammanställningen
for art in filtered_articles:
    col_a, col_b, col_c, col_d, col_btn = st.columns([2, 2, 1.5, 2, 1.2])
    
    with col_a:
        st.markdown(f"**{art['Jimotec Artnr']}**")
    with col_b:
        st.markdown(f"🏷️ {art['Benämning']}")
    with col_c:
        st.markdown(f"📄 `{art['Ritningsnr']}` *(Rev {art['Revision']})*")
    with col_d:
        st.markdown(f"🧱 {art['Material']}")
    with col_btn:
        if st.button("Öppna ➡️", key=f"btn_{art['Jimotec Artnr']}", use_container_width=True):
            st.session_state.vald_artikel = art["Jimotec Artnr"]
            st.switch_page("pages/2_Sammanstallning_artikel.py")
    st.markdown("<hr style='margin: 4px 0; border: none; border-bottom: 1px solid #f1f5f9;'>", unsafe_allow_html=True)
