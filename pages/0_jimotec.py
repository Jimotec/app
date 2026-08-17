import os
import streamlit as st
from datetime import datetime

# Konfigurera sidan
st.set_page_config(page_title="Jimotec - Mappöversikt", layout="wide")

# Logotyp uppe till vänster om den finns
logo_file = None
for f in ["Jimotec.jpg", "jimotec.jpg", "Jimotec.png", "jimotec.png"]:
    if os.path.exists(f):
        logo_file = f
        break

if logo_file:
    st.image(logo_file, width=180)

# Kontrollera inloggning
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Du måste logga in via startsidan först.")
    st.stop()

st.title("📁 Jimotec - Google Drive Arkiv")

# Sökväg till den synkade/monterade Google Drive-mappen
# Ändra sökvägen nedan till din faktiska enhet/mapp (t.ex. G:\ eller nätverksenhet)
DRIVE_PATH = r"G:\Min enhet\Jimotec"

if not os.path.exists(DRIVE_PATH):
    st.error(f"❌ Hittade inte mappen: `{DRIVE_PATH}`")
    st.info("Kontrollera att Google Drive / nätverksenheten är ansluten och monterad.")
else:
    # Sökfunktion
    sokfilter = st.text_input("🔍 Sök fil eller undermapp", "")

    # Lista alla filer
    hittade_filer = []
    for rot, mappar, filer in os.walk(DRIVE_PATH):
        for fil in filer:
            full_path = os.path.join(rot, fil)
            rel_path = os.path.relpath(full_path, DRIVE_PATH)
            
            if sokfilter.lower() in fil.lower() or sokfilter.lower() in rel_path.lower():
                try:
                    stat = os.stat(full_path)
                    hittade_filer.append({
                        "namn": fil,
                        "mapp": os.path.dirname(rel_path) if os.path.dirname(rel_path) else "Rotmapp",
                        "storlek_kb": round(stat.st_size / 1024, 1),
                        "andrad": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                        "path": full_path
                    })
                except Exception:
                    pass

    st.caption(f"Visar **{len(hittade_filer)}** filer")
    st.write("---")

    # Gruppera och visa per mapp
    if hittade_filer:
        mappar_dict = {}
        for item in hittade_filer:
            mappar_dict.setdefault(item["mapp"], []).append(item)

        for mappnamn, filer_i_mapp in mappar_dict.items():
            with st.expander(f"📂 {mappnamn} ({len(filer_i_mapp)} filer)", expanded=True):
                for fil_info in filer_i_mapp:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    col1.markdown(f"📄 **{fil_info['namn']}**")
                    col2.caption(f"{fil_info['storlek_kb']} KB | {fil_info['andrad']}")
                    
                    # Ladda ner-knapp
                    try:
                        with open(fil_info["path"], "rb") as f:
                            col3.download_button(
                                label="⬇️ Ladda ner",
                                data=f.read(),
                                file_name=fil_info["namn"],
                                key=fil_info["path"]
                            )
                    except Exception:
                        col3.caption("Lås / ej läsbar")
    else:
        st.info("Inga filer matchade sökningen eller mappen är tom.")
