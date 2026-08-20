from datetime import date, datetime, timedelta
import json
import os
import tempfile
import urllib.parse
import urllib.request
from fpdf import FPDF
import streamlit as st

st.set_page_config(page_title="Mötesprotokoll - Jimotec", layout="wide")

# CSS för dölja sidonavigering och skapa ett maffigt blått avskiljande band
st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] {display: none;}
        
        /* Ett tjockt blått band med 5 interna linjer som avskiljer dokumentet från sektion 5 */
        div.blue-thick-band {
            background-color: #0284c7 !important;
            height: 18px !important;
            border-radius: 6px !important;
            margin-top: 35px !important;
            margin-bottom: 35px !important;
            box-shadow: inset 0 2px 0 #38bdf8, inset 0 -2px 0 #0369a1, 0 2px 4px rgba(0,0,0,0.1);
            background-image: repeating-linear-gradient(
                0deg,
                #0284c7,
                #0284c7 2px,
                #38bdf8 2px,
                #38bdf8 4px
            ) !important;
        }

        /* Kraftig ram och ljus bakgrund runt hela sektion 5-containern */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div.export-marker) {
            background-color: #f0f9ff !important;
            padding: 24px !important;
            border-radius: 12px !important;
            border: 3px solid #0284c7 !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        }

        /* Gör alla knappar i sektion 5 breda och tydliga */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div.export-marker) button {
            width: 100% !important;
            font-weight: bold !important;
            height: 42px !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- HANTERA FORMULÄRTÖMNING INNAN ELEMENTEN RITAS ---
if st.session_state.get("clear_form_flag", False):
    st.session_state.markdown_text_val = ""
    st.session_state.datum_tid_val = ""
    st.session_state.foretag_val = ""
    st.session_state.plats_val = ""
    st.session_state.deltagare_val = ""
    st.session_state.uploaded_images = []
    st.session_state.atgarder_lista = [{
        "aktivitet": "",
        "ansvarig": "",
        "datum": date.today() + timedelta(days=7),
    }]

    # Nollställ widget-nycklar säkert innan de ritas ut
    for k in ["datum_tid_input", "foretag_input", "plats_input", "deltagare_input", "markdown_text_area"]:
        if k in st.session_state:
            st.session_state[k] = ""

    for key in list(st.session_state.keys()):
        if key.startswith("akt_") or key.startswith("ans_") or key.startswith("dat_"):
            del st.session_state[key]

    st.session_state["clear_form_flag"] = False

# Sidopanel för navigering
st.sidebar.title("Meny")
if os.path.exists("app.py"):
    st.sidebar.page_link("app.py", label="👈 Tillbaka till Startsida")

st.title("📋 Skapa Mötesprotokoll")
st.write(
    "Fyll i mötesinformation, klistra in din text och koppla bilderna direkt till"
    " punkterna."
)


# --- INBYGGDA ÖVERSÄTTNINGSFUNKTIONEN ---
def oversatt_text(text, target="en"):
    """Översätter text via Google Translate API med Pythons inbyggda urllib."""
    if not text or not str(text).strip():
        return text
    try:
        text_str = str(text).strip()
        url = (
            "https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl="
            + target
            + "&dt=t&q="
            + urllib.parse.quote(text_str)
        )
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"}
        )
        response = urllib.request.urlopen(req, timeout=5)
        data = json.loads(response.read().decode("utf-8"))

        res_text = ""
        for item in data[0]:
            if item[0]:
                res_text += item[0]
        return res_text if res_text else text_str
    except Exception:
        return text


# --- SESSION STATES INITIALISERING ---
if "uploaded_images" not in st.session_state:
    st.session_state.uploaded_images = []

if "atgarder_lista" not in st.session_state:
    st.session_state.atgarder_lista = [{
        "aktivitet": "",
        "ansvarig": "Torbjörn",
        "datum": date.today() + timedelta(days=7),
    }]

if "markdown_text_val" not in st.session_state:
    st.session_state.markdown_text_val = ""

if "datum_tid_val" not in st.session_state:
    st.session_state.datum_tid_val = "2026-08-07 10:00"

if "foretag_val" not in st.session_state:
    st.session_state.foretag_val = "Jimotec AB"

if "plats_val" not in st.session_state:
    st.session_state.plats_val = "Online / Kontoret"

if "deltagare_val" not in st.session_state:
    st.session_state.deltagare_val = (
        "Torbjörn Karlsson - VD\nMikael Svensson - Projektledare"
    )

# --- SEKTION 1: MÖTESINFO & TEXTINPUT ---
st.subheader("1. Mötesinformation")
col_info1, col_info2 = st.columns(2)

with col_info1:
    datum_tid = st.text_input(
        "Datum & Tid:",
        value=st.session_state.datum_tid_val,
        key="datum_tid_input",
    )
    foretag = st.text_input(
        "Företag / Kund:",
        value=st.session_state.foretag_val,
        key="foretag_input",
    )

with col_info2:
    plats = st.text_input(
        "Plats:", value=st.session_state.plats_val, key="plats_input"
    )
    deltagare = st.text_area(
        "Deltagare (en per rad):",
        value=st.session_state.deltagare_val,
        height=100,
        key="deltagare_input",
    )

st.session_state.datum_tid_val = datum_tid
st.session_state.foretag_val = foretag
st.session_state.plats_val = plats
st.session_state.deltagare_val = deltagare

st.subheader("2. Minnesanteckningar & Punkter")
markdown_text = st.text_area(
    "Minnesanteckningar:",
    value=st.session_state.markdown_text_val,
    height=200,
    key="markdown_text_area",
    placeholder="""1. Fel stift\n2. Smeda\n""",
)
st.session_state.markdown_text_val = markdown_text


# --- SEKTION 3: ÅTGÄRDSLISTA MED OUTLOOK-KNAPP ---
def skapad_enkelt_ics_objekt(aktivitet_text, ansvarig_namn, forfallo_datum):
    now = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    due_date = forfallo_datum.strftime("%Y%m%d")
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Jimotec AB//Task Generator//SE
BEGIN:VTODO
UID:jimotec-task-{now}@jimotec.se
DTSTAMP:{now}
SUMMARY:[Åtgärd Jimotec] {aktivitet_text}
DESCRIPTION:Ansvarig: {ansvarig_namn}\\nKopplat till möte: {st.session_state.foretag_val}
DUE;VALUE=DATE:{due_date}
STATUS:NEEDS-ACTION
END:VTODO
END:VCALENDAR"""
    return ics_content.encode("utf-8")


st.subheader("3. Åtgärdslista (Rutor för Ansvarig & Datum)")

ny_atgarder = []
for idx, item in enumerate(st.session_state.atgarder_lista):
    col_akt, col_ans, col_dat, col_export, col_del = st.columns([4, 2, 2, 2.5, 1])

    with col_akt:
        akt_val = st.text_input(
            f"Aktivitet #{idx+1}", value=item["aktivitet"], key=f"akt_{idx}"
        )
    with col_ans:
        ans_val = st.text_input(
            f"Ansvarig #{idx+1}", value=item["ansvarig"], key=f"ans_{idx}"
        )
    with col_dat:
        dat_val = st.date_input(
            f"Klar senast #{idx+1}", value=item["datum"], key=f"dat_{idx}"
        )

    with col_export:
        st.write("")
        st.write("")
        if akt_val.strip():
            ics_bytes = skapad_enkelt_ics_objekt(akt_val, ans_val, dat_val)
            st.download_button(
                label="⚡ Öppna i Outlook",
                data=ics_bytes,
                file_name=f"Uppgift_{idx+1}.ics",
                mime="text/calendar",
                key=f"dl_ics_{idx}",
            )
        else:
            st.button("⚡ Öppna i Outlook", disabled=True, key=f"dis_ics_{idx}")

    with col_del:
        st.write("")
        st.write("")
        if st.button("❌", key=f"del_{idx}"):
            st.session_state.atgarder_lista.pop(idx)
            st.rerun()

    ny_atgarder.append(
        {"aktivitet": akt_val, "ansvarig": ans_val, "datum": dat_val}
    )

st.session_state.atgarder_lista = ny_atgarder

if st.button("➕ Lägg till", key="btn_add_action"):
    st.session_state.atgarder_lista.append({
        "aktivitet": "",
        "ansvarig": "Torbjörn",
        "datum": date.today() + timedelta(days=7),
    })
    st.rerun()

st.divider()

# --- SEKTION 4: BILDHANTERING & SORTERING ---
st.subheader("4. Bilder")

ny_filer = st.file_uploader(
    "Ladda upp bilder till protokollet:",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
)

if ny_filer:
    befintliga_namn = [
        img["file"].name for img in st.session_state.uploaded_images
    ]
    for f in ny_filer:
        if f.name not in befintliga_namn:
            st.session_state.uploaded_images.append(
                {"file": f, "order": len(st.session_state.uploaded_images) + 1}
            )

if st.session_state.uploaded_images:
    st.write("**Sortera och granska bilder:**")
    st.caption(
        "Ändra numret först i raden om du vill skifta vilken bild som hamnar"
        " under vilken punkt."
    )

    for index, img_obj in enumerate(st.session_state.uploaded_images):
        col_num, col_img, col_txt = st.columns([1, 2, 4])

        with col_num:
            ny_ordning = st.number_input(
                "Bild ID:",
                min_value=1,
                max_value=99,
                value=img_obj["order"],
                key=f"order_{index}_{img_obj['file'].name}",
            )
            img_obj["order"] = ny_ordning

        with col_img:
            st.image(img_obj["file"], width=130)

        with col_txt:
            st.write("")
            st.info(
                f"Bild {img_obj['order']} -> Kopplas till Punkt"
                f" {img_obj['order']}"
            )

    st.session_state.uploaded_images.sort(key=lambda x: x["order"])

    if st.button("❌ Rensa alla bilder", key="btn_clear_imgs"):
        st.session_state.uploaded_images = []
        st.rerun()


# --- REJÄLT BLÅTT AVSKILJANDE BAND FÖR ATT SEKTIONERA SIDAN ---
st.markdown('<div class="blue-thick-band"></div>', unsafe_allow_html=True)


# --- SEKTION 5: PDF GENERATOR ---
class JimotecPDF(FPDF):

    def __init__(self, is_en=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_en = is_en

    def header(self):
        logo_paths = [
            "Jimotec.jpg",
            "jimotec.jpg",
            "Jimotec.png",
            "jimotec.png",
            "../Jimotec.jpg",
        ]
        logo_found = None
        for path in logo_paths:
            if os.path.exists(path):
                logo_found = path
                break

        if logo_found:
            self.image(logo_found, x=10, y=8, w=45)

        title_text = "MEETING MINUTES" if self.is_en else "MÖTESPROTOKOLL"
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(26, 54, 93)
        self.set_xy(10, 8)
        self.cell(190, 12, title_text, border=False, ln=True, align="R")

        self.set_draw_color(26, 54, 93)
        self.set_line_width(0.8)
        self.line(10, 24, 200, 24)
        self.set_y(28)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        page_str = (
            f"Page {self.page_no()} of {{nb}}"
            if self.is_en
            else f"Sida {self.page_no()} av {{nb}}"
        )
        self.cell(0, 10, page_str, align="C")


def generera_pdf_jimotec(
    d_tid, frtg, plts, deltag, md_text, atgarder_list, bild_lista, is_en=False
):
    pdf = JimotecPDF(is_en=is_en)
    pdf.alias_nb_pages()
    pdf.set_margins(10, 10, 10)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    def clean_txt(t):
        if not t:
            return ""
        return str(t).encode("latin-1", "replace").decode("latin-1")

    # Språkanpassade rubriker
    lbl_date = "DATE & TIME:" if is_en else "DATUM & TID:"
    lbl_comp = "COMPANY:" if is_en else "FÖRETAG:"
    lbl_loc = "LOCATION:" if is_en else "PLATS:"
    lbl_att = "ATTENDEES:" if is_en else "DELTAGARE:"
    lbl_notes = (
        "NOTES & DISCUSSION POINTS" if is_en else "MINNESANTECKNINGAR & PUNKTER"
    )
    lbl_actions = "SUMMARY OF ACTION ITEMS" if is_en else "SAMMANSTÄLLD ÅTGÄRDSLISTA"
    lbl_nr = "NO" if is_en else "NR"
    lbl_act = "ACTIVITY / ITEM" if is_en else "AKTIVITET / PUNKT"
    lbl_resp = "RESPONSIBLE" if is_en else "ANSVARIG"
    lbl_due = "DUE DATE" if is_en else "KLAR SENAST"

    if is_en:
        plts = oversatt_text(plts, "en")

    # Mötesfakta
    pdf.set_x(10)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(28, 5, lbl_date, ln=False)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(65, 5, clean_txt(d_tid), ln=False)

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(22, 5, lbl_comp, ln=False)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(75, 5, clean_txt(frtg), ln=True)

    deltagare_lista = [
        clean_txt(d.strip()) for d in deltag.split("\n") if d.strip()
    ]
    första_deltagare = deltagare_lista[0] if deltagare_lista else ""

    pdf.set_x(10)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(28, 5, lbl_loc, ln=False)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(65, 5, clean_txt(plts), ln=False)

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(22, 5, lbl_att, ln=False)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(75, 5, första_deltagare, ln=True)

    if len(deltagare_lista) > 1:
        for övrig in deltagare_lista[1:]:
            pdf.set_x(125)
            pdf.cell(75, 5, övrig, ln=True)

    pdf.ln(4)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)

    # Minnesanteckningar
    pdf.set_x(10)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(0, 7, lbl_notes, ln=True)
    pdf.ln(2)

    with tempfile.TemporaryDirectory() as temp_dir:
        bild_paths_by_order = {}
        for img in bild_lista:
            ext = os.path.splitext(img["file"].name)[1] or ".jpg"
            save_path = os.path.join(temp_dir, f"bild_{img['order']}{ext}")
            with open(save_path, "wb") as f:
                f.write(img["file"].getvalue())
            bild_paths_by_order[img["order"]] = save_path

        rader = [r.strip() for r in md_text.split("\n") if r.strip()]
        punkt_index = 1

        for rad in rader:
            rad_text = rad

            # Översätt varje rad om engelska är valt
            if is_en:
                rad_text = oversatt_text(rad_text, "en")

            bild_som_ska_visas = None

            for order, img_path in bild_paths_by_order.items():
                taggar = [
                    f"[bild {order}]",
                    f"[bild{order}]",
                    f"bild {order}",
                    f"bild{order}",
                    f"[image {order}]",
                    f"[image{order}]",
                ]
                for t in taggar:
                    if t in rad_text.lower():
                        bild_som_ska_visas = img_path
                        for t_clean in [t, t.upper(), t.title()]:
                            rad_text = rad_text.replace(t_clean, "").strip()
                        break
                if bild_som_ska_visas:
                    break

            if not bild_som_ska_visas and punkt_index in bild_paths_by_order:
                bild_som_ska_visas = bild_paths_by_order[punkt_index]

            pdf.set_x(10)
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(0, 5, clean_txt(rad_text.replace("**", "")))

            if bild_som_ska_visas:
                pdf.ln(2)
                pdf.image(bild_som_ska_visas, x=15, w=60)
                pdf.ln(3)

            punkt_index += 1

        pdf.ln(4)

        # Åtgärdslista
        pdf.set_x(10)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(26, 54, 93)
        pdf.cell(0, 7, lbl_actions, ln=True)
        pdf.ln(2)

        # Tabellhuvud (Totalt 190 mm)
        pdf.set_x(10)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(240, 244, 248)
        pdf.set_text_color(26, 54, 93)

        pdf.cell(12, 7, lbl_nr, border=1, align="C", fill=True)
        pdf.cell(90, 7, lbl_act, border=1, fill=True)
        pdf.cell(45, 7, lbl_resp, border=1, fill=True)
        pdf.cell(43, 7, lbl_due, border=1, ln=True, fill=True)

        # Tabellrader
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(30, 30, 30)

        aktiva_atgarder = [a for a in atgarder_list if a["aktivitet"].strip()]
        for idx, item in enumerate(aktiva_atgarder, 1):
            akt_str = item["aktivitet"]
            if is_en:
                akt_str = oversatt_text(akt_str, "en")

            pdf.set_x(10)
            pdf.cell(12, 6, str(idx), border=1, align="C")
            pdf.cell(90, 6, clean_txt(akt_str[:50]), border=1)
            pdf.cell(45, 6, clean_txt(item["ansvarig"][:22]), border=1)
            pdf.cell(43, 6, str(item["datum"]), border=1, ln=True)

        filename = (
            "Jimotec_Minutes_EN.pdf" if is_en else "Jimotec_Protokoll.pdf"
        )
        pdf_path = os.path.join(temp_dir, filename)
        pdf.output(pdf_path)

        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

    return pdf_bytes


# --- SEKTION 5: SKAPA, IMPORTERA & EXPORTERA (KRAFTIG RAM) ---
st.subheader("5. Skapa, Importera & Exportera")

with st.container(border=True):
    st.markdown('<div class="export-marker"></div>', unsafe_allow_html=True)

    # AI-Instruktioner och JSON-importör
    with st.expander("ℹ️ Klicka här för instruktioner till AI (Kopiera till chatten)"):
        st.markdown(
            """
            **Kopiera texten nedan och klistra in till AI tillsammans med dina anteckningar/bild:**
            
            ```text
            Du är en assistent som tolkar handskrivna mötesanteckningar och skapar en JSON-fil som ska importeras i Streamlit-appen 'Mötesprotokoll - Jimotec'.
            Generera enbart en nedladdningsbar .json-fil med följande nycklar:
            {
              "datum_tid": "YYYY-MM-DD HH:MM",
              "foretag": "Företagsnamn",
              "plats": "Plats",
              "deltagare": "Namn 1 - Roll 1\\nNamn 2 - Roll 2",
              "markdown_text": "1. Punkt 1\\n2. Punkt 2\\n3. Punkt 3",
              "atgarder": [
                {
                  "aktivitet": "Beskrivning av åtgärd",
                  "ansvarig": "Namn",
                  "datum": "YYYY-MM-DD"
                }
              ]
            }
            VIKTIGT: 
            1. Alla minnesanteckningar MÅSTE vara numrerade som '1.', '2.', '3.' osv. i markdown_text så att bildkopplingen fungerar.
            2. Säg alltid till mig att "Ladda ner dina mötesanteckningar" när filen är klar.
            ```
            """
        )

    json_file = st.file_uploader(
        "📂 Ladda upp sparat protokoll (.json) från AI", type=["json"]
    )

    if json_file is not None:
        try:
            # Säker avkodning som klarar både UTF-8 (med/utan BOM) och Windows ANSI (latin-1)
            raw_bytes = json_file.getvalue()
            try:
                content = raw_bytes.decode("utf-8-sig")
            except UnicodeDecodeError:
                content = raw_bytes.decode("latin-1")
            
            data = json.loads(content)

            if "datum_tid" in data:
                st.session_state.datum_tid_val = data["datum_tid"]
                st.session_state.datum_tid_input = data["datum_tid"]
            if "foretag" in data:
                st.session_state.foretag_val = data["foretag"]
                st.session_state.foretag_input = data["foretag"]
            if "plats" in data:
                st.session_state.plats_val = data["plats"]
                st.session_state.plats_input = data["plats"]
            if "deltagare" in data:
                st.session_state.deltagare_val = data["deltagare"]
                st.session_state.deltagare_input = data["deltagare"]
            if "markdown_text" in data:
                st.session_state.markdown_text_val = data["markdown_text"]
                st.session_state.markdown_text_area = data["markdown_text"]

            if "atgarder" in data and isinstance(data["atgarder"], list):
                nya_atgarder = []
                for a in data["atgarder"]:
                    d_val = date.today() + timedelta(days=7)
                    if "datum" in a and a["datum"]:
                        try:
                            d_val = datetime.strptime(
                                a["datum"], "%Y-%m-%d"
                            ).date()
                        except Exception:
                            pass
                    nya_atgarder.append({
                        "aktivitet": a.get("aktivitet", ""),
                        "ansvarig": a.get("ansvarig", "Torbjörn"),
                        "datum": d_val,
                    })
                if nya_atgarder:
                    st.session_state.atgarder_lista = nya_atgarder

            st.success("✅ Data importerades från JSON-filen!")
        except Exception as e:
            st.error(f"❌ Fel vid läsning av JSON-fil: {e}")

    st.write("")

    # Knappar på en samlad rad för PDF & Formulärtömning
    c1, c2, c3 = st.columns([1, 1, 1])

    with c1:
        if st.button("🇸🇪 Skapa PDF (SV)", type="primary", key="btn_pdf_sv"):
            if not markdown_text.strip():
                st.warning("⚠️ Fyll i protokolltexten först.")
            else:
                try:
                    pdf_data = generera_pdf_jimotec(
                        datum_tid,
                        foretag,
                        plats,
                        deltagare,
                        markdown_text,
                        st.session_state.atgarder_lista,
                        st.session_state.uploaded_images,
                        is_en=False,
                    )
                    st.download_button(
                        label="📥 Hämta SV PDF",
                        data=pdf_data,
                        file_name="Motesprotokoll_Jimotec_SV.pdf",
                        mime="application/pdf",
                    )
                except Exception as e:
                    st.error(f"❌ Fel: {e}")

    with c2:
        if st.button("🇬🇧 Skapa PDF (EN)", type="primary", key="btn_pdf_en"):
            if not markdown_text.strip():
                st.warning("⚠️ Fyll i protokolltexten först.")
            else:
                try:
                    with st.spinner("Översätter..."):
                        st.session_state.markdown_text_val = oversatt_text(
                            markdown_text, "en"
                        )
                        for item in st.session_state.atgarder_lista:
                            if item["aktivitet"]:
                                item["aktivitet"] = oversatt_text(
                                    item["aktivitet"], "en"
                                )

                        pdf_data = generera_pdf_jimotec(
                            datum_tid,
                            foretag,
                            plats,
                            deltagare,
                            st.session_state.markdown_text_val,
                            st.session_state.atgarder_lista,
                            st.session_state.uploaded_images,
                            is_en=True,
                        )
                    st.download_button(
                        label="📥 Hämta EN PDF",
                        data=pdf_data,
                        file_name="Meeting_Minutes_Jimotec_EN.pdf",
                        mime="application/pdf",
                    )
                except Exception as e:
                    st.error(f"❌ Fel: {e}")

    with c3:
        if st.button("🗑️ Töm formulär", type="primary", key="btn_clear_all"):
            st.session_state["clear_form_flag"] = True
            st.rerun()
