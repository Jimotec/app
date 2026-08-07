import os
import tempfile
import streamlit as st
import markdown
from weasyprint import HTML, CSS

st.set_page_config(page_title="Mötesprotokoll - Jimotec", layout="wide")

# Döljer automatiska listan i sidopanelen
st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidopanel för navigering
st.sidebar.title("Meny")
if os.path.exists("app.py"):
    st.sidebar.page_link("app.py", label="👈 Tillbaka till Startsida")

st.title("📋 Skapa Mötesprotokoll")
st.write("Klistra in strukturerad text från chatten, ladda upp bilder och generera din PDF.")

# --- SEKTION 1: SESSION STATE FOR BILDER ---
if "uploaded_images" not in st.session_state:
    st.session_state.uploaded_images = []

# --- SEKTION 2: TEXTINPUT ---
st.subheader("1. Protokolltext (Markdown)")
markdown_text = st.text_area(
    "Klistra in din text här:",
    height=250,
    placeholder="""# Mötesprotokoll - Projekt X

## Identifierade punkter
* **Punkt 1:** Genomgång av stativ genomförd utan anmärkning.
* **Punkt 2:** Skada på vänster hörn vid leverans.
  ![Skada hörn](bild1.jpg)
* **Punkt 3:** Ny logotyp monterad i nederkant.
  ![Ny logotyp](bild2.jpg)
""",
)

st.divider()

# --- SEKTION 3: BILDHANTERING & SORTERING ---
st.subheader("2. Bilder")

ny_filer = st.file_uploader(
    "Ladda upp bilder till protokollet:",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
)

if ny_filer:
    befintliga_namn = [img["file"].name for img in st.session_state.uploaded_images]
    for f in ny_filer:
        if f.name not in befintliga_namn:
            st.session_state.uploaded_images.append({"file": f, "order": len(st.session_state.uploaded_images) + 1})

if st.session_state.uploaded_images:
    st.write("**Sortera och granska bilder:**")
    st.caption("Ändra numret i rutan om du vill ändra bildernas ordning/referensnamn.")

    for index, img_obj in enumerate(st.session_state.uploaded_images):
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            st.image(img_obj["file"], width=150)
            
        with col2:
            st.write(f"**Originalfil:** {img_obj['file'].name}")
            st.info(f"Använd i texten som: `![Beskrivning](bild{img_obj['order']}.jpg)`")
            
        with col3:
            ny_ordning = st.number_input(
                "Bildnummer (ID):",
                min_value=1,
                max_value=99,
                value=img_obj["order"],
                key=f"order_{index}_{img_obj['file'].name}",
            )
            img_obj["order"] = ny_ordning

    st.session_state.uploaded_images.sort(key=lambda x: x["order"])

    if st.button("❌ Rensa alla bilder"):
        st.session_state.uploaded_images = []
        st.rerun()

st.divider()

# --- SEKTION 4: GENERERA PDF ---
st.subheader("3. Skapa PDF")

def generera_pdf(md_text, bild_lista):
    with tempfile.TemporaryDirectory() as temp_dir:
        for img in bild_lista:
            ext = os.path.splitext(img["file"].name)[1]
            if not ext:
                ext = ".jpg"
            
            alias_path = os.path.join(temp_dir, f"bild{img['order']}{ext}")
            orig_path = os.path.join(temp_dir, img["file"].name)
            
            bytes_data = img["file"].getvalue()
            with open(alias_path, "wb") as f:
                f.write(bytes_data)
            with open(orig_path, "wb") as f:
                f.write(bytes_data)

        html_innehall = markdown.markdown(
            md_text, extensions=["tables", "fenced_code", "nl2br"]
        )

        css_stil = """
        @page {
            size: A4;
            margin: 20mm 15mm 20mm 15mm;
            @bottom-right {
                content: "Sida " counter(page) " av " counter(pages);
                font-family: Arial, sans-serif;
                font-size: 8pt;
                color: #666;
            }
        }
        body {
            font-family: Arial, sans-serif;
            font-size: 10.5pt;
            line-height: 1.5;
            color: #222;
        }
        h1 {
            color: #1a365d;
            border-bottom: 2px solid #1a365d;
            padding-bottom: 5px;
            font-size: 18pt;
        }
        h2 {
            color: #2b6cb0;
            font-size: 14pt;
            margin-top: 20px;
            border-left: 4px solid #2b6cb0;
            padding-left: 8px;
        }
        ul, ol {
            padding-left: 20px;
        }
        li {
            margin-bottom: 8px;
        }
        img {
            max-width: 100%;
            max-height: 110mm;
            height: auto;
            display: block;
            margin: 12px 0;
            border-radius: 4px;
            page-break-inside: avoid;
        }
        p {
            page-break-inside: avoid;
        }
        """

        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"></head>
        <body>{html_innehall}</body>
        </html>
        """

        pdf_path = os.path.join(temp_dir, "protokoll.pdf")
        HTML(string=full_html, base_url=temp_dir).write_pdf(
            target=pdf_path, stylesheets=[CSS(string=css_stil)]
        )

        with open(pdf_path, "rb") as f:
            return f.read()


if st.button("🚀 Generera PDF-Protokoll", type="primary"):
    if not markdown_text.strip():
        st.warning("⚠️ Du måste klistra in text i rutan innan du skapar PDF:en.")
    else:
        try:
            pdf_data = generera_pdf(markdown_text, st.session_state.uploaded_images)
            st.success("✅ PDF har skapats!")
            st.download_button(
                label="📥 Ladda ned PDF",
                data=pdf_data,
                file_name="Motesprotokoll.pdf",
                mime="application/pdf",
            )
        except Exception as e:
            st.error(f"❌ Ett fel uppstod vid skapandet av PDF: {e}")
