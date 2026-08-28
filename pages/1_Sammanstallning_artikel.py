import streamlit as st
import pandas as pd
import subprocess
import os

# Konfigurera sidan
st.set_page_config(page_title="Sammanställning Artikel - Jimotec AB", layout="wide")

# Anpassad CSS för Jimotec-design, Drive-knappar och kortlayout
st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    
    /* Toppbehållare för Drive-knappar */
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
        transition: all 0.2s ease-in-out;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        white-space: nowrap;
    }
    
    .drive-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 3px 6px rgba(0,0,0,0.2);
        opacity: 0.92;
    }

    /* Mappfärger */
    .btn-00 { background-color: #8E44AD; }
    .btn-01 { background-color: #2C3E50; }
    .btn-02 { background-color: #27AE60; }
    .btn-03 { background-color: #2980B9; }
    .btn-04 { background-color: #16A085; }
    .btn-05 { background-color: #D35400; }
    .btn-06 { background-color: #C0392B; }
    .btn-07 { background-color: #34495E; }
    .btn-08 { background-color: #E67E22; }

    /* Informationskort */
    .info-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    .card-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 10px;
        border-bottom: 2px solid #f1f5f9;
        padding-bottom: 6px;
    }
    .badge-artnr {
        background-color: #d9381e;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 1.1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Sidopanel Meny ---
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
    try_page_link("pages/1_Sammanstallning_artikel.py", "Sammanställning Artikel")

with st.sidebar.expander("Mötesprotokoll", expanded=False):
    try_page_link("pages/6_motesprotokoll.py", "Mötesprotokoll")

with st.sidebar.expander("Affärsplan", expanded=False):
    try_page_link("pages/3_affarsplan_sammanfattning.py", "1. Sammanfattning")
    try_page_link("pages/3_affarsplan_ide.py", "2. Affärsidé och vision")

# --- Topprad & Snabblänkar ---
col_head, col_drives = st.columns([1.2, 2.8])

with col_head:
    st.title("📄 Sammanställning")
    st.caption("Jimotec Produktions- & Artikelöversikt")

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

# --- Artikeldata ---
col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown(
        """
        <div class="info-card">
            <div class="card-title">📌 Artikel- & Ritningsinformation</div>
            <table style="width:100%; border-collapse: collapse; font-size: 0.95rem;">
                <tr><td style="padding:4px 0; color:#64748b;">Jimotec Artnr:</td><td><span class="badge-artnr">4-210-A1038867</span></td></tr>
                <tr><td style="padding:4px 0; color:#64748b;">Benämning:</td><td><strong>Hållare</strong></td></tr>
                <tr><td style="padding:4px 0; color:#64748b;">Ritningsnr:</td><td><code>A1038867</code></td></tr>
                <tr><td style="padding:4px 0; color:#64748b;">Revision / Utgåva:</td><td><strong>B</strong> (Bearbetning tillagd)</td></tr>
                <tr><td style="padding:4px 0; color:#64748b;">Material:</td><td><strong>PE300, svart</strong> (Densitet: 0.95 g/cm³)</td></tr>
                <tr><td style="padding:4px 0; color:#64748b;">Ytbehandling:</td><td>Obehandlad</td></tr>
                <tr><td style="padding:4px 0; color:#64748b;">Tolerans / Standard:</td><td>SS-ISO 2768-m, Skarpa kanter bryts</td></tr>
                <tr><td style="padding:4px 0; color:#64748b;">Konstruktör / Datum:</td><td>Sten Lundström (2026-08-03)</td></tr>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_right:
    st.markdown(
        """
        <div class="info-card">
            <div class="card-title">⚖️ Mått, Volym & Materialåtgång</div>
            <table style="width:100%; border-collapse: collapse; font-size: 0.95rem;">
                <tr><td style="padding:4px 0; color:#64748b;">Färdigmått:</td><td><strong>70.0 × 50.0 × 70.0 mm</strong></td></tr>
                <tr><td style="padding:4px 0; color:#64748b;">Detaljvikt (Färdig):</td><td><strong>1.320 kg</strong></td></tr>
                <tr><td style="padding:4px 0; color:#64748b;">Råmått (Sågsnitt):</td><td><strong>75.0 × 55.0 × 75.0 mm</strong> (Block)</td></tr>
                <tr><td style="padding:4px 0; color:#64748b;">Ämnesvikt (Inköp):</td><td><strong>2.429 kg</strong></td></tr>
                <tr><td style="padding:4px 0; color:#64748b;">Spånförlust:</td><td><strong style="color:#d9381e;">1.108 kg (45.6 %)</strong></td></tr>
                <tr><td style="padding:4px 0; color:#64748b;">Geometri / Egenskaper:</td><td>Hålbild 4x Ø9, faser 2x45°, hörnradier R2</td></tr>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- Operationsplan ---
st.markdown("### 🛠️ Beredd Operationsplan")

ops_data = [
    {"Op": "Op 10", "Maskin": "Kapsåg", "Beskrivning": "Kapning av plastämne PE300 svart till rätt yttermått/blockstorlek"},
    {"Op": "Op 20", "Maskin": "CNC-fräs", "Beskrivning": "Fräsning av kontur, plana ytor, hålbild 4x Ø9, faser 2x45° samt hörnradier R2"},
    {"Op": "Op 30", "Maskin": "Manuell / Gradningsstation", "Beskrivning": "Manuell gradning (bryt alla skarpa kanter), rengöring och avsyning enligt SS-ISO 2768-m"}
]

st.dataframe(pd.DataFrame(ops_data), use_container_width=True, hide_index=True)

st.write("---")

# --- Snabböppning av mappar på Server / Lokalt ---
c_btn1, c_btn2 = st.columns(2)

with c_btn1:
    if st.button("📂 Öppna på Y:\\Artikelregister\\4-210-A1038867", use_container_width=True):
        subprocess.Popen(r'explorer.exe "Y:\Artikelregister\4-210-A1038867"')

with c_btn2:
    if st.button("📂 Öppna Lokalt (C:\\Jimotec\\Kund pdf\\Klara_Beredningar)", use_container_width=True):
        subprocess.Popen(r'explorer.exe "C:\Jimotec\Kund pdf\Klara_Beredningar\4-210-A1038867"')
