import streamlit as st

st.set_page_config(page_title="Jimotec Mappar", page_icon="📁", layout="wide")

st.title("📁 Jimotec Mappar & Dokument")
st.write("Välj en mapp nedan för att öppna den direkt i Google Drive.")

# Mappstruktur och motsvarande Google Drive-länkar
jimotec_folders = {
    "00 Ägande & Styrelse": "https://drive.google.com/drive/folders/DIN_MAPP_ID_00",
    "01 Affärsplan & Strategi": "https://drive.google.com/drive/folders/DIN_MAPP_ID_01",
    "02 Mötesprotokoll": "https://drive.google.com/drive/folders/DIN_MAPP_ID_02",
    "03 Rutiner & Processer": "https://drive.google.com/drive/folders/DIN_MAPP_ID_03",
    "04 Kvalitet": "https://drive.google.com/drive/folders/DIN_MAPP_ID_04",
    "05 CRM & Kunder": "https://drive.google.com/drive/folders/DIN_MAPP_ID_05",
    "06 Produktion & Leverans": "https://drive.google.com/drive/folders/DIN_MAPP_ID_06",
    "07 Personal": "https://drive.google.com/drive/folders/DIN_MAPP_ID_07",
    "08 Ekonomi & Administration": "https://drive.google.com/drive/folders/DIN_MAPP_ID_08",
}

st.divider()

# Alternativ 1: Välj via dropdown och öppna med knapp
st.subheader("Snabbval via meny")
col1, col2 = st.columns([3, 1])

with col1:
    selected_folder = st.selectbox(
        "Välj mapp:",
        options=list(jimotec_folders.keys()),
        label_visibility="collapsed"
    )

with col2:
    if selected_folder:
        target_url = jimotec_folders[selected_folder]
        st.link_button(
            label=f"Öppna {selected_folder.split(' ')[0]}",
            url=target_url,
            type="primary",
            use_container_width=True
        )

st.divider()

# Alternativ 2: Rutnät med alla mappar för snabb överblick
st.subheader("Alla mappar")
cols = st.columns(3)

for idx, (folder_name, folder_url) in enumerate(jimotec_folders.items()):
    with cols[idx % 3]:
        with st.container(border=True):
            st.markdown(f"**{folder_name}**")
            st.link_button(
                label="Öppna mapp ↗",
                url=folder_url,
                use_container_width=True
            )
