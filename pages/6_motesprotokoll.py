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
st.write("Fyll i mötesinformation, klistra in din text från chatten och ladda upp bilder.")

# --- SEKTION 1: SESSION STATE FOR BILDER ---
if "uploaded_images" not in st.session_state:
    st.session_state.uploaded_images = []

# --- SEKTION 2: MÖTESINFO & TEXTINPUT ---
st.subheader("1. Mötesinformation")
col_info1, col_info2 = st.columns(2)

with col_info1:
    datum_tid = st.text_input("Datum & Tid:", value="2026-08-07 10:00")
    foretag = st.text_input("Företag / Kund:", value="Jimotec AB")

with col_info2:
    plats = st.text_input("Plats:", value="Online / Kontoret")
    deltagare = st.text_input("Deltagare:", value="Torbjörn Karlsson - VD")

st.subheader("2. Protokolltext (Markdown & Bilder)")
markdown_text = st.text_area(
    "Minnesanteckningar & Punkter:",
    height=220,
    placeholder="""1. Genomgång av projekt status.
2. Skada identifierad på vänster hörn.
   ![Skada hörn](bild1.jpg)
3. Ny logotyp monterad och godkänd.
""",
)

st.subheader("3. Åtgärdslista (Tabell)")
atgards_text = st.text_area(
    "Ange åtgärder (en per rad i formatet: Aktivitet | Ansvarig | Notering):",
    height=120,
    placeholder="""Uppdatera ritningshuvud i CAD | Torbjörn | System
Beställa nytt material enligt punkt 2 | Mikael | Inköp""",
)

st.divider()

# --- SEKTION 3: BILDHANTERING & SORTERING ---
st.subheader("4. Bilder")

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
    st.caption("Ändra numret i rutan om du vill ändra bildernas ordningsföljd/referens.")

    for index, img_obj in enumerate(st.session_state.uploaded_images):
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            st.image(img_obj["file"], width=150)

        with col2:
            st.write(f"**Originalfil:** {img_obj['file'].name}")
            st.info(f"Kopplad som: `bild{img_obj['order']}.jpg`")

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

# --- SEKTION 4: PDF GENERATOR (FPDF2 - JIMOTEC MALL) ---
class JimotecPDF(FPDF):
    def header(self):
        # Sök efter logotyp
        logo_paths = ["Jimotec.jpg", "jimotec.jpg", "Jimotec.png", "jimotec.png", "../Jimotec.jpg"]
        logo_found = None
        for path in logo_paths:
            if os.path.exists(path):
                logo_found = path
                break

        if logo_found:
            self.image(logo_found, x=10, y=8, w=45)

        self.set_font("Helvetica", "B", 18)
        self.set_text_color(26, 54, 93)
        self.cell(0, 12, "MÖTESPROTOKOLL", border=False, ln=True, align="R")
        
        self.set_draw_color(26, 54, 93)
        self.set_line_width(0.8)
        self.line(10, 25, 200, 25)
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Sida {self.page_no()} av {{nb}}", align="C")


def generera_pdf_jimotec(d_tid, frtg, plts, deltag, md_text, atgarder_raw, bild_lista):
    pdf = JimotecPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    def clean_txt(t):
        return t.encode("latin-1", "replace").decode("latin-1")

    # Mötesfakta (2-kolumners vy)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(26, 54, 93)
    
    pdf.cell(30, 5, "DATUM & TID:", ln=False)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(65, 5, clean_txt(d_tid), ln=False)
    
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(25, 5, "FÖRETAG:", ln=False)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(70, 5, clean_txt(frtg), ln=True)

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(30, 5, "PLATS:", ln=False)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(65, 5, clean_txt(plts), ln=False)

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(25, 5, "DELTAGARE:", ln=False)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(70, 5, clean_txt(deltag), ln=True)

    pdf.ln(4)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)

    # Minnesanteckningar Rubrik
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(0, 7, "MINNESANTECKNINGAR & PUNKTER", ln=True)
    pdf.ln(2)

    with tempfile.TemporaryDirectory() as temp_dir:
        # Spara bilder lokalt
        bild_map = {}
        for img in bild_lista:
            ext = os.path.splitext(img["file"].name)[1] or ".jpg"
            alias_name = f"bild{img['order']}{ext}".lower()
            save_path = os.path.join(temp_dir, alias_name)
            with open(save_path, "wb") as f:
                f.write(img["file"].getvalue())
            bild_map[f"bild{img['order']}".lower()] = save_path
            bild_map[img["file"].name.lower()] = save_path

        # Rendera punkter
        rader = md_text.split("\n")
        for rad in rader:
            rad_trim = rad.strip()
            if not rad_trim:
                pdf.ln(2)
                continue

            if "![" in rad_trim or "bild" in rad_trim.lower():
                hittat = False
                for key, img_path in bild_map.items():
                    if key in rad_trim.lower():
                        pdf.ln(2)
                        pdf.image(img_path, w=120)
                        pdf.ln(2)
                        hittat = True
                        break
                if not hittat:
                    pdf.set_font("Helvetica", "", 10)
                    pdf.set_text_color(30, 30, 30)
                    pdf.multi_cell(0, 5, clean_txt(rad_trim.replace("**", "")))
            else:
                pdf.set_font("Helvetica", "", 10)
                pdf.set_text_color(30, 30, 30)
                pdf.multi_cell(0, 5, clean_txt(rad_trim.replace("**", "")))

        pdf.ln(6)

        # Åtgärdslista Rubrik
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(26, 54, 93)
        pdf.cell(0, 7, "SAMMANSTÄLLD ÅTGÄRDSLISTA", ln=True)
        pdf.ln(2)

        # Tabellhuvud
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(240, 244, 248)
        pdf.set_text_color(26, 54, 93)
        
        pdf.cell(12, 7, "NR", border=1, align="C", fill=True)
        pdf.cell(90, 7, "AKTIVITET / PUNKT", border=1, fill=True)
        pdf.cell(43, 7, "ANSVARIG", border=1, fill=True)
        pdf.cell(45, 7, "NOTERING / SYSTEM", border=1, ln=True, fill=True)

        # Tabellrader
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(30, 30, 30)
        
        atgard_rader = [r.strip() for r in atgards_text.split("\n") if r.strip()]
        for idx, rad in enumerate(atgard_rader, 1):
            delar = [d.strip() for d in rad.split("|")]
            aktivitet = delar[0] if len(delar) > 0 else ""
            ansvarig = delar[1] if len(delar) > 1 else ""
            notering = delar[2] if len(delar) > 2 else ""

            pdf.cell(12, 6, str(idx), border=1, align="C")
            pdf.cell(90, 6, clean_txt(aktivitet), border=1)
            pdf.cell(43, 6, clean_txt(ansvarig), border=1)
            pdf.cell(45, 6, clean_txt(notering), border=1, ln=True)

        pdf_path = os.path.join(temp_dir, "Jimotec_Protokoll.pdf")
        pdf.output(pdf_path)

        with open(pdf_path, "rb") as f:
            return f.read()


# --- SEKTION 5: KNAPP FÖR SKAPANDE ---
st.subheader("5. Skapa PDF")

if st.button("🚀 Generera PDF-Protokoll", type="primary"):
    if not markdown_text.strip():
        st.warning("⚠️ Du måste fylla i protokolltexten innan du skapar PDF:en.")
    else:
        try:
            pdf_data = generera_pdf_jimotec(
                datum_tid,
                foretag,
                plats,
                deltagare,
                markdown_text,
                atgards_text,
                st.session_state.uploaded_images,
            )
            st.success("✅ PDF har skapats i Jimotec-mallen!")
            st.download_button(
                label="📥 Ladda ned PDF",
                data=pdf_data,
                file_name="Motesprotokoll_Jimotec.pdf",
                mime="application/pdf",
            )
        except Exception as e:
            st.error(f"❌ Ett fel uppstod vid skapandet av PDF: {e}")
