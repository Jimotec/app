import streamlit as st

# Konfigurera sidan
st.set_page_config(page_title="Jimotec AB - Dokument & Filer", layout="wide")

# CSS-styling (exakt samma klasser och färgkoder som i app.py)
st.markdown(
    """
    <style>
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
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidhuvud med rubrik till vänster och dina Drive-länkar till höger
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

# Här fortsätter ditt innehåll för 0_jimotec.py nedanför:
st.write("Välj en Drive-katalog ovan för att öppna den i en ny flik, eller arbeta med dokumenten nedan.")
