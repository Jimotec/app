import os
import re
import streamlit as st

st.set_page_config(page_title="Artikelregister - Jimotec AB", layout="wide")

# Sökväg till Y:
REGISTER_PATH = r"Y:\Artikelregister"

# CSS
st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    .card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
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
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidomeny & Logga
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

# Header & Drive-knappar
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

def parse_underlag(filepath):
    data = {"Artnr": "", "Benämning": "", "Ritningsnr": "", "Material": "", "Revision": ""}
    if not os.path.exists(filepath):
        return data
    
    encodings = ["utf-8", "latin-1", "cp1252"]
    text = ""
    for enc in encodings:
        try:
            with open(filepath, "r", encoding=enc) as f:
                text = f.read()
                break
        except UnicodeDecodeError:
            continue
            
    for line in text.splitlines():
        line_clean = line.strip()
        if ":" in line_clean:
            key, val = line_clean.split(":", 1)
            key = key.strip().lower()
            val = val.strip()
            if "artnr" in key or "artikelnr" in key:
                data["Artnr"] = val
            elif "benämning" in key or "benamning" in key:
                data["Benämning"] = val
            elif "ritningsnr" in key or "ritning" in key:
                data["Ritningsnr"] = val
            elif "material" in key:
                data["Material"] = val
            elif "revision" in key:
                data["Revision"] = val
    return data

artiklar = []
if os.path.exists(REGISTER_PATH):
    try:
        entries = os.listdir(REGISTER_PATH)
        for item in entries:
            full_item_path = os.path.join(REGISTER_PATH, item)
            if os.path.isdir(full_item_path):
                txt_path = os.path.join(full_item_path, "Underlag_Beredning.txt")
                info = parse_underlag(txt_path)
                art_visning = info["Artnr"] if info["Artnr"] else item
                artiklar.append({
                    "mappnamn": item,
                    "artnr": art_visning,
                    "benamning": info["Benämning"],
                    "ritningsnr": info["Ritningsnr"],
                    "material": info["Material"],
                    "revision": info["Revision"]
                })
    except Exception as e:
        st.error(f"Fel vid inläsning: {e}")
else:
    st.error(f"Sökvägen `{REGISTER_PATH}` hittades inte. Kontrollera att RaiDrive är ansluten.")

col_sok, col_antal = st.columns([4, 1])
with col_sok:
    sok_text = st.text_input("🔍 Sök på Artikelnummer, Benämning, Ritningsnummer eller Material:", "")
with col_antal:
    st.metric("Totalt antal artiklar", len(artiklar))

if sok_text.strip():
    q = sok_text.strip().lower()
    filtrerade = [
        a for a in artiklar
        if q in a["artnr"].lower()
        or q in a["benamning"].lower()
        or q in a["ritningsnr"].lower()
        or q in a["material"].lower()
        or q in a["mappnamn"].lower()
    ]
else:
    filtrerade = artiklar

st.caption(f"Visar {len(filtrerade)} st artiklar")

# Tabellhuvud
col1, col2, col3, col4, col5, col6 = st.columns([2, 3, 2, 2.5, 1, 1.5])
col1.markdown("**Artikelnummer**")
col2.markdown("**Benämning**")
col3.markdown("**Ritningsnr**")
col4.markdown("**Material**")
col5.markdown("**Rev**")
col6.markdown("**Åtgärd**")
st.markdown("<hr style='margin-top: -5px; margin-bottom: 10px;'>", unsafe_allow_html=True)

if not filtrerade:
    st.info("Inga artiklar matchade sökningen.")
else:
    for row in filtrerade:
        c1, c2, c3, c4, c5, c6 = st.columns([2, 3, 2, 2.5, 1, 1.5])
        c1.write(row["artnr"])
        c2.write(row["benamning"] if row["benamning"] else "-")
        c3.write(row["ritningsnr"] if row["ritningsnr"] else "-")
        c4.write(row["material"] if row["material"] else "-")
        c5.write(row["revision"] if row["revision"] else "-")
        
        if c6.button("Öppna ➡️", key=f"btn_{row['mappnamn']}"):
            st.session_state["vald_artikel"] = row["mappnamn"]
            st.switch_page("pages/2_Sammanstallning_artikel.py")
