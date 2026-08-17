import streamlit as st

def render_folder_buttons():
    # Mappstruktur, färgkodning och Drive-länkar
    buttons_data = [
        {"name": "👑 00. Ägare", "color": "#8e44ad", "url": "https://drive.google.com/drive/folders/DITT_MAPP_ID_00"},
        {"name": "🏛️ 01. Styrelse", "color": "#2c3e50", "url": "https://drive.google.com/drive/folders/DITT_MAPP_ID_01"},
        {"name": "🚀 02. Affärsplan", "color": "#27ae60", "url": "https://drive.google.com/drive/folders/DITT_MAPP_ID_02"},
        {"name": "📝 03. Möten", "color": "#2980b9", "url": "https://drive.google.com/drive/folders/DITT_MAPP_ID_03"},
        {"name": "📋 04. Rutiner", "color": "#16a085", "url": "https://drive.google.com/drive/folders/DITT_MAPP_ID_04"},
        {"name": "🔎 05. Kvalitet", "color": "#d35400", "url": "https://drive.google.com/drive/folders/DITT_MAPP_ID_05"},
        {"name": "🤝 06. CRM & Sälj", "color": "#c0392b", "url": "https://drive.google.com/drive/folders/DITT_MAPP_ID_06"},
        {"name": "🏭 07. ERP & Prod", "color": "#34495e", "url": "https://drive.google.com/drive/folders/DITT_MAPP_ID_07"},
        {"name": "👥 08. HR", "color": "#e67e22", "url": "https://drive.google.com/drive/folders/DITT_MAPP_ID_08"},
    ]

    # CSS för knappar och layout
    html_code = """
    <style>
    .folder-nav-container {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        align-items: center;
        margin-bottom: 20px;
    }
    .folder-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 6px 12px;
        color: #ffffff !important;
        text-decoration: none !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-weight: 600;
        font-size: 12.5px;
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        transition: all 0.15s ease-in-out;
        white-space: nowrap;
    }
    .folder-btn:hover {
        opacity: 0.88;
        transform: translateY(-1px);
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    </style>
    <div class="folder-nav-container">
    """

    for btn in buttons_data:
        html_code += f'<a href="{btn["url"]}" target="_blank" rel="noopener noreferrer" class="folder-btn" style="background-color: {btn["color"]};">{btn["name"]}</a>'

    html_code += "</div>"

    st.markdown(html_code, unsafe_allow_html=True)


# Exempel på integrering i app.py
if __name__ == "__main__":
    st.set_page_config(page_title="Jimotec App", layout="wide")
    
    # Ritar ut knappraden längst upp
    render_folder_buttons()
    
    st.title("Jimotec Huvudmeny")
    st.write("Välj en sektion eller klicka på snabbknapparna ovan för att öppna respektive mapp i Google Drive.")
