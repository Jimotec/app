import os
import tempfile
import urllib.parse
import urllib.request
import json
from datetime import datetime, date, timedelta
import streamlit as st
from fpdf import FPDF
from icalendar import Calendar, Event

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
st.write("Fyll i mötesinformation, klistra in din text och koppla bilderna direkt till punkterna.")

# --- SESSION STATES ---
if "uploaded_images" not in st.session_state:
    st.session_state.uploaded_images = []

if "atgarder_lista" not in st.session_state:
    st.session_state.atgarder_lista = [
        {"aktivitet": "", "ansvarig": "Torbjörn", "datum": date.today() + timedelta(days=7)}
    ]

if "markdown_text" not in st.session_state:
    st.session_state.markdown_text = ""


# --- SEKTION: ÖVERSÄTTNINGSFUNKTION ---
def oversatt_till_engelska(text):
    """Översätter text från svenska till engelska via Google Translate API utan externa beroenden."""
    if not text or not text.strip():
        return text
    try:
        url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=sv&tl=en&dt=t&q=" + urllib.parse.quote(text)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode('utf-8'))
            översatt_text = "".join([segment[0] for segment in res[0] if segment[0]])
            return översatt_text
    except Exception:
        return text


# --- SEKTION 1: MÖTESINFO & TEXTINPUT ---
st.subheader("1. Mötesinformation")
col_info1, col_info2 = st.columns(2)

with col_info1:
    datum_tid = st.text_input("Datum & Tid:", value="2026-08-07 10:00")
    foretag = st.text_input("Företag / Kund:", value="Jimotec AB")

with col_info2:
    plats = st.text_input("Plats:", value="Online / Kontoret")
    deltagare = st.text_area(
        "Deltagare (en per rad):",
        value="Torbjörn Karlsson - VD\nMikael Svensson - Projektledare",
        height=100,
    )

st.subheader("2. Minnesanteckningar & Punkter")

markdown_text = st.text_area(
    "Minnesanteckningar:",
    height=200,
    placeholder="""1. Fel stift
2. Smeda
""",
    key="markdown_text"
)

st.subheader("3. Åtgärdslista (Rutor för Ansvarig & Datum)")

ny_atgarder = []
for idx, item in enumerate(st.session_state.atgarder_lista):
    col_akt, col_ans, col_dat, col_del = st.columns([4, 2, 2, 1])
    
    with col_akt:
        akt_val = st.text_input(f"Aktivitet #{idx+1}", value=item["aktivitet"], key=f"akt_{idx}")
    with col_ans:
        ans_val = st.text_input(f"Ansvarig #{idx+1}", value=item["ansvarig"], key=f"ans_{idx}")
    with col_dat:
        dat_val = st.date_input(f"Klar senast #{idx+1}", value=item["datum"], key=f"dat_{idx}")
    with col_del:
        st.write("")
        st.write("")
        if st.button("❌", key=f"del_{idx}"):
            st.session_state.atgarder_lista.pop(idx)
            st.rerun()
            
    ny_atgarder.append({"aktivitet": akt_val, "ansvarig": ans_val, "datum": dat_val})

st.session_state.atgarder_lista = ny_atgarder

if st.button("➕ Lägg till ny åtgärdsrad"):
    st.session_state.atgarder_lista.append(
        {"aktivitet": "", "ansvarig": "", "datum": date.today() + timedelta(days=7)}
    )
    st.rerun()

st.divider()

# --- SEKTION 2: BILDHANTERING & SORTERING ---
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
    st.caption("Ändra numret först i raden om du vill skifta vilken bild som hamnar under vilken punkt.")

    bild_som_ska_ta_bort = None

    for index, img_obj in enumerate(st.session_state.uploaded_images):
        col_num, col_img, col_btn = st.columns([1, 2, 2])

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

        with col_btn:
            st.write("")
            st.write("")
            if st.button("🗑️ Ta bort bild", key=f"del_img_{index}_{img_obj['file'].name}"):
                bild_som_ska_ta_bort = index

    if bild_som_ska_ta_bort is not None:
        st.session_state.uploaded_images.pop(bild_som_ska_ta_bort)
        st.rerun()

    st.session_state.uploaded_images.sort(key=lambda x: x["order"])

    st.write("")
    if st.button("❌ Rensa alla bilder"):
        st.session_state.uploaded_images = []
        st.rerun()

st.divider()

# --- SEKTION 3: FUNKTION FÖR OUTLOOK ICS-FIL ---
def generera_outlook_ics(atgarder_list, frtg):
    cal = Calendar()
    cal.add('prodid', '-//Jimotec AB Task Exporter//jimotec.se//')
    cal.add('version', '2.0')

    aktiva_atgarder = [a for a in atgarder_list if a["aktivitet"].strip()]
    if not aktiva_atgarder:
        return None

    now = datetime.now()
    
    for idx, item in enumerate(aktiva_atgarder, 1):
        event = Event()
        event.add('summary', f"[Åtgärd Jimotec] {item['aktivitet']}")
        
        beskrivning = f"Aktivitet: {item['aktivitet']}\nAnsvarig: {item['ansvarig']}\nKlar senast: {item['datum']}\nKopplat till möte för: {frtg}"
        event.add('description', beskrivning)
        
        due_datetime = datetime.combine(item['datum'], datetime.min.time()).replace(hour=9, minute=0)
        
        event.add('dtstart', due_datetime)
        event.add('dtend', due_datetime + timedelta(hours=1))
        event.add('dtstamp', now)

        cal.add_component(event)

    return cal.to_ical()


# --- SEKTION 4: PDF GENERATOR ---
class JimotecPDF(FPDF):
    def __init__(self, rubrik="MÖTESPROTOKOLL", sida_text="Sida"):
        super().__init__()
        self.rubrik = rubrik
        self.sida_text = sida_text

    def header(self):
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
        self.set_xy(10, 8)
        self.cell(190, 12, self.rubrik, border=False, ln=True, align="R")
        
        self.set_draw_color(26, 54, 93)
        self.set_line_width(0.8)
        self.line(10, 24, 200, 24)
        self.set_y(28)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"{self.sida_text} {self.page_no()} av {{nb}}", align="C")


def generera_pdf_jimotec(d_tid, frtg, plts, deltag, md_text, atgarder_list, bild_lista, sprak="sv"):
    is_en = (sprak == "en")
    
    t_rubrik = "MEETING MINUTES" if is_en else "MÖTESPROTOKOLL"
    t_sida = "Page" if is_en else "Sida"
    t_datum = "DATE & TIME:" if is_en else "DATUM & TID:"
    t_foretag = "COMPANY:" if is_en else "FÖRETAG:"
    t_plats = "LOCATION:" if is_en else "PLATS:"
    t_deltagare = "PARTICIPANTS:" if is_en else "DELTAGARE:"
    t_minnes_rubrik = "MEETING NOTES & POINTS" if is_en else "MINNESANTECKNINGAR & PUNKTER"
    t_atg_rubrik = "ACTION ITEM LIST" if is_en else "SAMMANSTÄLLD ÅTGÄRDSLISTA"
    t_nr = "NO" if is_en else "NR"
    t_akt = "ACTION / ITEM" if is_en else "AKTIVITET / PUNKT"
    t_ans = "RESPONSIBLE" if is_en else "ANSVARIG"
    t_klar = "DUE DATE" if is_en else "KLAR SENAST"

    if is_en:
        d_tid = oversatt_till_engelska(d_tid)
        frtg = oversatt_till_engelska(frtg)
        plts = oversatt_till_engelska(plts)
        deltag = oversatt_till_engelska(deltag)
        md_text = oversatt_till_engelska(md_text)

    pdf = JimotecPDF(rubrik=t_rubrik, sida_text=t_sida)
    pdf.alias_nb_pages()
    pdf.set_margins(10, 10, 10)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    def clean_txt(t):
        if not t:
            return ""
        return str(t).encode("latin-1", "replace").decode("latin-1")

    # Mötesfakta
    pdf.set_x(10)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(28, 5, t_datum, ln=False)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(65, 5, clean_txt(d_tid), ln=False)
    
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(22, 5, t_foretag, ln=False)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(75, 5, clean_txt(frtg), ln=True)

    deltagare_lista = [clean_txt(d.strip()) for d in deltag.split("\n") if d.strip()]
    första_deltagare = deltagare_lista[0] if deltagare_lista else ""

    pdf.set_x(10)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(28, 5, t_plats, ln=False)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(65, 5, clean_txt(plts), ln=False)

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(22, 5, t_deltagare, ln=False)
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
    pdf.cell(0, 7, t_minnes_rubrik, ln=True)
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
            bild_som_ska_visas = None

            for order, img_path in bild_paths_by_order.items():
                taggar = [f"[bild {order}]", f"[bild{order}]", f"bild {order}", f"bild{order}"]
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
        pdf.cell(0, 7, t_atg_rubrik, ln=True)
        pdf.ln(2)

        # Tabellhuvud
        pdf.set_x(10)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(240, 244, 248)
        pdf.set_text_color(26, 54, 93)
        
        pdf.cell(12, 7, t_nr, border=1, align="C", fill=True)
        pdf.cell(90, 7, t_akt, border=1, fill=True)
        pdf.cell(45, 7, t_ans, border=1, fill=True)
        pdf.cell(43, 7, t_klar, border=1, ln=True, fill=True)

        # Tabellrader
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(30, 30, 30)
        
        aktiva_atgarder = [a for a in atgarder_list if a["aktivitet"].strip()]
        for idx, item in enumerate(aktiva_atgarder, 1):
            akt_txt = oversatt_till_engelska(item["aktivitet"]) if is_en else item["aktivitet"]
            ans_txt = oversatt_till_engelska(item["ansvarig"]) if is_en else item["ansvarig"]
            
            pdf.set_x(10)
            pdf.cell(12, 6, str(idx), border=1, align="C")
            pdf.cell(90, 6, clean_txt(akt_txt[:50]), border=1)
            pdf.cell(45, 6, clean_txt(ans_txt[:22]), border=1)
            pdf.cell(43, 6, str(item["datum"]), border=1, ln=True)

        pdf_path = os.path.join(temp_dir, "Jimotec_Protokoll.pdf")
        pdf.output(pdf_path)

        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

    return pdf_bytes


# --- SEKTION 5: SKAPA EXPORT (PDF + OUTLOOK) ---
st.subheader("5. Skapa & Exportera")

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    st.write("**PDF-Protokoll:**")
    col_pdf_sv, col_pdf_en = st.columns(2)
    
    with col_pdf_sv:
        if st.button("🇸🇪 Generera Svensk PDF", type="primary", use_container_width=True):
            if not st.session_state.markdown_text.strip():
                st.warning("⚠️ Fyll i protokolltexten först.")
            else:
                try:
                    pdf_data = generera_pdf_jimotec(
                        datum_tid,
                        foretag,
                        plats,
                        deltagare,
                        st.session_state.markdown_text,
                        st.session_state.atgarder_lista,
                        st.session_state.uploaded_images,
                        sprak="sv"
                    )
                    st.success("✅ Svensk PDF skapad!")
                    st.download_button(
                        label="📥 Ladda ned Svensk PDF",
                        data=pdf_data,
                        file_name="Motesprotokoll_Jimotec_SV.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"❌ Fel vid PDF-skapande: {e}")

    with col_pdf_en:
        if st.button("🇬🇧 Generera Engelska PDF", type="secondary", use_container_width=True):
            if not st.session_state.markdown_text.strip():
                st.warning("⚠️ Fyll i protokolltexten först.")
            else:
                with st.spinner("Översätter och skapar engelsk PDF..."):
                    try:
                        pdf_data_en = generera_pdf_jimotec(
                            datum_tid,
                            foretag,
                            plats,
                            deltagare,
                            st.session_state.markdown_text,
                            st.session_state.atgarder_lista,
                            st.session_state.uploaded_images,
                            sprak="en"
                        )
                        st.success("✅ Engelsk PDF skapad!")
                        st.download_button(
                            label="📥 Ladda ned Engelska PDF",
                            data=pdf_data_en,
                            file_name="Meeting_Minutes_Jimotec_EN.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )
                    except Exception as e:
                        st.error(f"❌ Fel vid översättning/PDF-skapande: {e}")

with col_btn2:
    st.write("**Outlook Kalender:**")
    if st.button("📅 Skapa Outlook-uppgifter (.ics)", use_container_width=True):
        har_atgarder = any(a["aktivitet"].strip() for a in st.session_state.atgarder_lista)
        if not har_atgarder:
            st.warning("⚠️ Fyll i minst en aktivitet i åtgärdslistan.")
        else:
            try:
                ics_data = generera_outlook_ics(st.session_state.atgarder_lista, foretag)
                st.success("✅ Outlook-fil skapad!")
                st.download_button(
                    label="📥 Ladda ned till Outlook / Kalender",
                    data=ics_data,
                    file_name="Jimotec_Atgarder.ics",
                    mime="text/calendar",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"❌ Ett fel uppstod: {e}")
