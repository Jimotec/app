import streamlit as st
import fitz
import os
import importlib.util
import zipfile
import io
from datetime import datetime
import cadquery as cq

st.set_page_config(page_title="Jimotec Verktyg", layout="wide")

BASE_DIR = r"C:\Jimotec\Kund pdf"

# Välj funktion
val_program = st.radio(
    "Välj funktion:",
    ["📄 Ritningshantering (Kund)", "⚙️ Beredning & Detaljhantering"],
    horizontal=True
)

st.markdown("---")

if val_program == "⚙️ Beredning & Detaljhantering":
    beredning_fil = os.path.join(BASE_DIR, "beredning.py")
    if os.path.exists(beredning_fil):
        with open(beredning_fil, "r", encoding="utf-8") as f:
            exec(f.read())
    else:
        st.error(f"Kunde inte hitta filen: {beredning_fil}")
else:
    OUTPUT_FOLDER = os.path.join(BASE_DIR, "Klara")
    TEMPLATES_DIR = os.path.join(BASE_DIR, "Mallar")
    STEP_FOLDER = os.path.join(BASE_DIR, "step_fil")
    LOGO_PATH = os.path.join(BASE_DIR, "Jimotec.jpg")

    st.markdown("""
        <style>
            [data-testid="stFileUploader"] { border: 2px dashed #004a99; border-radius: 10px; background-color: #f8f9fa; }
            div.stButton > button#töm-knapp { background-color: #ff4b4b; color: white; }
        </style>
    """, unsafe_allow_html=True)

    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=200)

    tab_pdf, tab_vikt = st.tabs(["📄 PDF-bearbetning", "⚖️ Viktberäkning (STEP)"])

    with tab_pdf:
        header_col, select_col = st.columns([2, 1])
        with header_col:
            st.title("PDF-bearbetning med AI-stöd")
        with select_col:
            if not os.path.exists(TEMPLATES_DIR):
                os.makedirs(TEMPLATES_DIR)
            templates = [f for f in os.listdir(TEMPLATES_DIR) if f.endswith('.py')]
            selected_template = st.selectbox("Välj mall för bearbetning:", templates)

        st.markdown("---")
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📥 Bearbeta filer")
            uploaded_files = st.file_uploader("Dra och släpp PDF-filer", accept_multiple_files=True, type=['pdf'])
            process_btn = st.button("🚀 Bearbeta och stämpla")

            if process_btn and uploaded_files and selected_template:
                os.makedirs(OUTPUT_FOLDER, exist_ok=True)
                template_path = os.path.join(TEMPLATES_DIR, selected_template)
                spec = importlib.util.spec_from_file_location("dynamic_template", template_path)
                template_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(template_module)

                with st.spinner(f'Bearbetar {len(uploaded_files)} filer...'):
                    for uploaded_file in uploaded_files:
                        save_path = os.path.join(OUTPUT_FOLDER, uploaded_file.name)
                        doc = fitz.open(stream=uploaded_file.getvalue(), filetype="pdf")
                        template_module.apply_template(doc, LOGO_PATH)
                        doc.save(save_path)
                        doc.close()
                    st.success("Bearbetning klar!")

        with col2:
            header_col2, btn_col = st.columns([3, 1])
            with header_col2:
                st.subheader("📂 Färdiga filer")
            with btn_col:
                if st.button("🗑️ Töm Klara-mapp", key="töm-knapp"):
                    if os.path.exists(OUTPUT_FOLDER):
                        for f in os.listdir(OUTPUT_FOLDER):
                            p = os.path.join(OUTPUT_FOLDER, f)
                            if os.path.isfile(p): os.remove(p)
                        st.rerun()

            if os.path.exists(OUTPUT_FOLDER):
                files = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith('.pdf')]
                if files:
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                        for file in files:
                            zip_file.write(os.path.join(OUTPUT_FOLDER, file), arcname=file)
                    zip_buffer.seek(0)
                    st.download_button(
                        label=f"📦 Ladda ner ALLA i ZIP ({len(files)} st)",
                        data=zip_buffer,
                        file_name=f"Ritningar_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.zip",
                        mime="application/zip",
                        use_container_width=True
                    )

    with tab_vikt:
        st.title("Jimotec - STEP Viktuppskattning")
        d_dict = {"Aluminium (2.70 g/cm³)": 2.70, "Stål (7.85 g/cm³)": 7.85, "Rostfritt (8.00 g/cm³)": 8.00}
        mat_val = st.selectbox("Välj material", list(d_dict.keys()))
        step_up = st.file_uploader("Ladda upp STEP-fil (.step, .stp)", type=["step", "stp"])
        if step_up:
            os.makedirs(STEP_FOLDER, exist_ok=True)
            sp = os.path.join(STEP_FOLDER, step_up.name)
            with open(sp, "wb") as f:
                f.write(step_up.getbuffer())
            try:
                m = cq.importers.importStep(sp)
                v = m.val().Volume() / 1000.0
                w = (v * d_dict[mat_val]) / 1000.0
                st.metric("Vikt", f"{w:.3f} kg")
            except Exception as e:
                st.error(f"Fel vid STEP-läsning: {e}")