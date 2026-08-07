import os
import tempfile
import streamlit as st
from fpdf import FPDF

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
st.subheader("1. Protokolltext")
markdown_text = st.text_area(
    "Klistra in din text här:",
    height=250,
    placeholder="""# Mötesprotokoll - Projekt X

## Identifierade punkter
* Punkt 1: Genomgång av stativ genomförd utan anmärkning.
* Punkt 2: Skada på vänster hörn vid leverans.
  ![Skada hörn](bild1.jpg)
* Punkt 3: Ny logotyp monterad i nederkant.
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
            st.session_state.uploaded_images.append(
                {"file": f, "order": len(st.session_state.uploaded_images) + 1}
            )

if st.session_state.uploaded_images:
    st.write("**Sortera och granska bilder:**")
    st.caption("Ändra numret i rutan om du vill ändra bildernas ordning/referensnamn.")

    for index, img_obj in enumerate(st.session_state.uploaded_images):
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            st.image(img_obj["file"], width=150)

        with col2:
            st.write(f"**Originalfil:** {img_obj['file'].name}")
            st.info(f"Kopplad som: `bild{img_obj['order']}.jpg` eller `[Bild {img_obj['order']}]`")

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

# --- SEKTION 4: PDF GENERATOR (FPDF2) ---
class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(26, 54, 93)
        self.cell(0, 10, "JIMOTEC AB - MÖTESPROTOKOLL", border=False, ln=True, align="L")
        self.set_draw_color(26, 54, 93)
        self.set_line_width(0.8)
        self.line(10, 20, 200, 20)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Sida {self.page_no()}/{{nb}}", align="R")


def generera_pdf_fpdf(md_text, bild_lista):
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    with tempfile.TemporaryDirectory() as temp_dir:
        # Spara bilder lokalt för inbäddning
        bild_map = {}
        for img in bild_lista:
            ext = os.path.splitext(img["file"].name)[1]
            if not ext:
                ext = ".jpg"
            
            alias_name = f"bild{img['order']}{ext}".lower()
            save_path = os.path.join(temp_dir, alias_name)
            
            with open(save_path, "wb") as f:
                f.write(img["file"].getvalue())
            
            bild_map[f"bild{img['order']}".lower()] = save_path
            bild_map[img["file"].name.lower()] = save_path

        rader = md_text.split("\n")
        
        for rad in rader:
            rad_trim = rad.strip()

            if not rad_trim:
                pdf.ln(3)
                continue

            # Rubrik 1
            if rad_trim.startswith("# "):
                pdf.ln(4)
                pdf.set_font("Helvetica", "B", 16)
                pdf.set_text_color(26, 54, 93)
                txt = rad_trim[2:].encode('latin-1', 'replace').decode('latin-1')
                pdf.cell(0, 8, txt, ln=True)

            # Rubrik 2
            elif rad_trim.startswith("## "):
                pdf.ln(3)
                pdf.set_font("Helvetica", "B", 12)
                pdf.set_text_color(43, 108, 176)
                txt = rad_trim[3:].encode('latin-1', 'replace').decode('latin-1')
                pdf.cell(0, 7, txt, ln=True)

            # Punkter (* eller -)
            elif rad_trim.startswith("* ") or rad_trim.startswith("- "):
                pdf.set_font("Helvetica", "", 10)
                pdf.set_text_color(30, 30, 30)
                txt = rad_trim[2:].replace("**", "").encode('latin-1', 'replace').decode('latin-1')
                pdf.cell(5)
                pdf.multi_cell(0, 5, f"- {txt}")

            # Bilder (Markdown-bild eller referens)
            elif "![" in rad_trim or "bild" in rad_trim.lower():
                hittat = False
                for key, img_path in bild_map.items():
                    if key in rad_trim.lower():
                        pdf.ln(3)
                        pdf.image(img_path, w=130)
                        pdf.ln(3)
                        hittat = True
                        break
                if not hittat:
                    pdf.set_font("Helvetica", "", 10)
                    pdf.set_text_color(30, 30, 30)
                    txt = rad_trim.replace("**", "").encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 5, txt)

            # Vanlig text
            else:
                pdf.set_font("Helvetica", "", 10)
                pdf.set_text_color(30, 30, 30)
                txt = rad_trim.replace("**", "").encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 5, txt)

        pdf_path = os.path.join(temp_dir, "protokoll.pdf")
        pdf.output(pdf_path)

        with open(pdf_path, "rb") as f:
            return f.read()


# --- SEKTION 5: KNAPP FÖR SKAPANDE ---
st.subheader("3. Skapa PDF")

if st.button("🚀 Generera PDF-Protokoll", type="primary"):
    if not markdown_text.strip():
        st.warning("⚠️ Du måste klistra in text i rutan innan du skapar PDF:en.")
    else:
        try:
            pdf_data = generera_pdf_fpdf(
                markdown_text, st.session_state.uploaded_images
            )
            st.success("✅ PDF har skapats!")
            st.download_button(
                label="📥 Ladda ned PDF",
                data=pdf_data,
                file_name="Motesprotokoll.pdf",
                mime="application/pdf",
            )
        except Exception as e:
            st.error(f"❌ Ett fel uppstod vid skapandet av PDF: {e}")
