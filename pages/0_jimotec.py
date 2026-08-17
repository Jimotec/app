import os
import streamlit as st

# Kontrollera inloggning från app.py
if not st.session_state.get("logged_in", False):
    st.warning("⚠️ Du måste logga in på startsidan först.")
    st.stop()

st.title("📁 Jimotec – Dokument & Mappstruktur")
st.write("Välj en sektion eller mapp i rullgardinen nedan för att öppna den direkt i Google Drive.")

# Mapp- och länkstruktur för Jimotecs verksamhetssystem
MAPPAR = {
    "00. Ägare (Begränsad behörighet)": "https://drive.google.com/drive/folders/DIN_MAPP_ID_00",
    "01. Styrelse (Styrelseprotokoll & Stämmohandlingar)": "https://drive.google.com/drive/folders/DIN_MAPP_ID_01",
    "02. Affärsplan & Strategi (SWOT, Riskanalys & Mål)": "https://drive.google.com/drive/folders/DIN_MAPP_ID_02",
    "03. Mötesprotokoll & Ledning (Veckomöten & Beslut)": "https://drive.google.com/drive/folders/DIN_MAPP_ID_03",
    "04. Rutiner & Instruktioner (Processer & Miro-länkar)": "https://drive.google.com/drive/folders/DIN_MAPP_ID_04",
    "05. Kvalitet & Avvikelser (ISO & Förbättringsförslag)": "https://drive.google.com/drive/folders/DIN_MAPP_ID_05",
    "06. CRM & Sälj (HubSpot-rutiner, Avtal & Prislistor)": "https://drive.google.com/drive/folders/DIN_MAPP_ID_06",
    "07. ERP & Produktion (Monitor ERP & Beredningar)": "https://drive.google.com/drive/folders/DIN_MAPP_ID_07",
    "08. HR & Personal (Fortnox, Avtal & Policys)": "https://drive.google.com/drive/folders/DIN_MAPP_ID_08",
}

# Rullgardinsmeny
vald_mapp = st.selectbox(
    "Välj mapp:",
    options=list(MAPPAR.keys())
)

vald_url = MAPPAR[vald_mapp]

# Klickbar knapp som öppnar den valda mappen direkt i ny flik
st.link_button(f"🔗 Öppna {vald_mapp.split(' ')[0]} i Google Drive", vald_url, use_container_width=True)

st.markdown("---")

# Information om den valda mappen
st.info(f"**Vald resurs:** {vald_mapp}\n\nKlicka på knappen ovan för att öppna mappen i ett nytt fönster.")
