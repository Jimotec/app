import streamlit as st
import fitz  # PyMuPDF
import os
import shutil
import importlib.util
import json
import re
import math
import base64
import uuid
import time
import subprocess
import pandas as pd
import cadquery as cq
from cadquery import exporters
from google import genai

# --- Gemini Konfiguration ---
# Hämtas säkert från miljövariabel eller Streamlit secrets
GOOGLE_API_KEY = os.environ.get("GEMINI_API_KEY") or getattr(st.secrets, "GEMINI_API_KEY", None)

BASE_DIR = r"C:\Jimotec\Kund pdf"
OUTPUT_FOLDER = os.path.join(BASE_DIR, "Klara")
TEMPLATES_DIR = os.path.join(BASE_DIR, "Mallar")
STEP_FOLDER = os.path.join(BASE_DIR, "step_fil")
LOGO_PATH = os.path.join(BASE_DIR, "Jimotec.jpg")

# --- Hjälpfunktion: Robust AI-anrop med retry & fallback ---
def analyze_drawing_with_ai(pdf_name, pdf_text):
    if not GOOGLE_API_KEY:
        st.warning("⚠️ Ingen GEMINI_API_KEY hittades.")
        return {
            "Artikelnummer": "Okänt",
            "Benamning": "Okänd detalj",
            "Revision": "-",
            "Material": "Okänt",
            "Formtyp": "Block",
            "DrivnaVerktyg": True,
            "Ytbehandling": "Okänt",
            "Krav": "Ingen API-nyckel konfigurerad.",
            "Operationer": []
        }

    client = genai.Client(api_key=GOOGLE_API_KEY)
    prompt = f"""
    Du är produktionstekniker. Analysera ritningen ({pdf_name}):
    ---
    {pdf_text[:6000]}
    ---
    Identifiera följande och avgör tillverkningsmetod:
    - Artikelnummer / Ritningsnummer
    - Detaljnamn / Benämning (t.ex. FLÄNS, AXEL, FÄSTE, DISTANSRING, BRACKET osv)
    - Revision / Version / Utgåva (t.ex. Rev A, 01, B, Ind 1 osv från ritningshuvudet eller revisionsfältet)
    - Exakt Material från ritningen (t.ex. EN AW 7075, S355, 1.4404)
    - Råmaterialform: Avgör om detaljen är 'Plåt' (ska laserskäras/vattenskäras/bockas), 'Rundstång' (svarvas) eller 'Block' (fräsas).
    - Drivna verktyg: om det är en svarvdetalj med fräsning/tvärhål (true/false).
    - Ytbehandling
    - Krav & Toleranser
    - Skapa en logisk operationslista anpassad till metoden (t.ex. Laserskärning, Kantpressning, CNC, Ytbehandling).

    Svara ENDAST med ett giltigt JSON-objekt:
    {{
        "Artikelnummer": "hittat ritningsnummer",
        "Benamning": "hittat detaljnamn / benämning",
        "Revision": "hittad version/revision/utgåva (t.ex. A, 01, B eller -)",
        "Material": "exakt material från ritning",
        "Formtyp": "Plåt, Rundstång eller Block",
        "DrivnaVerktyg": true,
        "Ytbehandling": "angiven ytbehandling",
        "Krav": "kritiska toleranser osv",
        "Operationer": [
            {{"Op": "Op 10", "Maskin": "Maskinnamn", "Beskrivning": "Beskrivning"}}
        ]
    }}
    """
    
    candidate_models = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3.6-flash"]
    
    for model_name in candidate_models:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                clean_text = re.sub(r"```json|```", "", response.text).strip()
                return json.loads(clean_text)
            except Exception:
                time.sleep(1.5)
                continue
            
    return {
        "Artikelnummer": "Okänt",
        "Benamning": "Okänd detalj",
        "Revision": "-",
        "Material": "Okänt",
        "Formtyp": "Block",
        "DrivnaVerktyg": True,
        "Ytbehandling": "Okänt",
        "Krav": "Tillfälligt fel vid kontakt med AI.",
        "Operationer": []
    }

# --- Hjälpfunktion: Avgör densitet från text ---
def get_density_from_material(mat_str):
    m = str(mat_str).lower()
    if any(x in m for x in ["rostfri", "316", "304", "1.4404", "1.4301", "2333", "2343"]):
        return 8.00
    elif any(x in m for x in ["alu", "7075", "6082", "6060", "aw", "en aw", "almg"]):
        return 2.70
    elif any(x in m for x in ["stål", "s235", "s355", "domex", "hardox", "1651", "2172", "c45", "fe"]):
        return 7.85
    elif any(x in m for x in ["mässing", "brons", "koppar", "cw"]):
        return 8.50
    elif any(x in m for x in ["pom", "plast", "delrin", "pa6", "peek", "ptfe"]):
        return 1.41
    elif "titan" in m:
        return 4.50
    return 7.85

# --- Funktion: Beräkna Jimotec-kod ---
def get_jimotec_code(material_str, shape_type, dims, has_driven_tools):
    mat_lower = str(material_str).lower()
    
    if any(x in mat_lower for x in ["rostfri", "316", "304", "1.4404", "1.4301", "2333", "2343"]):
        mat_prefix = "3"
    elif any(x in mat_lower for x in ["alu", "7075", "6082", "6060", "aw", "en aw", "almg"]):
        mat_prefix = "4"
    elif any(x in mat_lower for x in ["stål", "s355", "s235", "domex", "hardox", "1651", "2172", "c45", "fe"]):
        mat_prefix = "5"
    elif any(x in mat_lower for x in ["pom", "plast", "delrin", "pa6", "peek", "ptfe"]):
        mat_prefix = "6"
    elif any(x in mat_lower for x in ["mässing", "brons", "koppar", "cw"]):
        mat_prefix = "7"
    else:
        mat_prefix = "4"

    d_min, d_mid, d_max = dims

    if shape_type == "Plåt":
        max_sheet_dim = max(d_mid, d_max)
        if max_sheet_dim <= 100: cat_code = "680"
        elif max_sheet_dim <= 200: cat_code = "682"
        elif max_sheet_dim <= 500: cat_code = "684"
        elif max_sheet_dim <= 1000: cat_code = "686"
        elif max_sheet_dim <= 1500: cat_code = "688"
        elif max_sheet_dim <= 2000: cat_code = "690"
        elif max_sheet_dim <= 2500: cat_code = "692"
        else: cat_code = "694"

    elif shape_type == "Rundstång":
        dia = d_mid
        if dia <= 25: cat_code = "110" if has_driven_tools else "100"
        elif dia <= 50: cat_code = "112" if has_driven_tools else "111"
        elif dia <= 100: cat_code = "114" if has_driven_tools else "113"
        elif dia <= 500: cat_code = "116" if has_driven_tools else "115"
        else: cat_code = "118" if has_driven_tools else "117"

    else:
        max_block_dim = max(d_mid, d_max)
        if max_block_dim <= 100: cat_code = "210"
        elif max_block_dim <= 200: cat_code = "212"
        elif max_block_dim <= 300: cat_code = "215"
        elif max_block_dim <= 500: cat_code = "220"
        elif max_block_dim <= 750: cat_code = "222"
        elif max_block_dim <= 1000: cat_code = "225"
        elif max_block_dim <= 1500: cat_code = "227"
        else: cat_code = "228"

    return f"{mat_prefix}-{cat_code}"

# --- Session State för nollställning ---
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0
if "active_files_sig" not in st.session_state:
    st.session_state.active_files_sig = None
if "ber_result" not in st.session_state:
    st.session_state.ber_result = None
if "operations_list" not in st.session_state:
    st.session_state.operations_list = []
if "local_saved_dir" not in st.session_state:
    st.session_state.local_saved_dir = None
if "remote_saved_dir" not in st.session_state:
    st.session_state.remote_saved_dir = None
if "save_status_msg" not in st.session_state:
    st.session_state.save_status_msg = None

def clear_all_inputs():
    st.session_state.uploader_key += 1
    st.session_state.ber_result = None
    st.session_state.active_files_sig = None
    st.session_state.operations_list = []
    st.session_state.local_saved_dir = None
    st.session_state.remote_saved_dir = None
    st.session_state.save_status_msg = None
    st.rerun()

# --- Kompakt Styling ---
st.markdown("""
    <style>
        .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
        [data-testid="stFileUploader"] { padding: 0.3rem !important; border: 2px dashed #004a99; border-radius: 8px; background-color: #f8f9fa; }
        div.stButton > button { padding: 0.4rem 0.8rem !important; font-size: 1rem !important; font-weight: bold; }
        h1, h2, h3, h4 { margin-top: 0.2rem !important; margin-bottom: 0.2rem !important; }
        hr { margin-top: 0.5rem !important; margin-bottom: 0.5rem !important; }
    </style>
""", unsafe_allow_html=True)

# --- Topprad ---
top_col1, top_col2, top_col3 = st.columns([1, 3.5, 1.5])
with top_col1:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=140)
with top_col2:
    st.subheader("⚙️ Jimotec - Beredning & Detaljkalkyl")
with top_col3:
    if st.button("🗑️ Ny Detalj (Rensa)", use_container_width=True):
        clear_all_inputs()

# --- Uppladdningsruta ---
uploaded_files = st.file_uploader(
    "📥 Släpp BÅDE PDF-ritning och STEP-fil här",
    type=["pdf", "step", "stp"],
    accept_multiple_files=True,
    key=f"ber_uploader_{st.session_state.uploader_key}",
    label_visibility="collapsed"
)

uploaded_pdf = None
uploaded_step = None

if uploaded_files:
    pdf_list = [f for f in uploaded_files if os.path.splitext(f.name)[1].lower() == ".pdf"]
    step_list = [f for f in uploaded_files if os.path.splitext(f.name)[1].lower() in [".step", ".stp"]]
    
    if pdf_list:
        uploaded_pdf = pdf_list[-1]
    if step_list:
        uploaded_step = step_list[-1]

    current_files_sig = sorted([uploaded_pdf.name if uploaded_pdf else "", uploaded_step.name if uploaded_step else ""])
    if current_files_sig != st.session_state.active_files_sig:
        st.session_state.ber_result = None
        st.session_state.operations_list = []
        st.session_state.local_saved_dir = None
        st.session_state.remote_saved_dir = None
        st.session_state.save_status_msg = None
        st.session_state.active_files_sig = current_files_sig

# --- Stämpelmall & Körknapp ---
col_mall, col_btn = st.columns([2, 3])

with col_mall:
    if not os.path.exists(TEMPLATES_DIR):
        os.makedirs(TEMPLATES_DIR)
    templates = [f for f in os.listdir(TEMPLATES_DIR) if f.endswith('.py')]
    selected_template = st.selectbox("Stämpelmall:", templates if templates else ["Ingen mall"], label_visibility="collapsed")

with col_btn:
    run_btn = st.button("🚀 Kör Komplett Beredning", type="primary", use_container_width=True)

st.markdown("---")

# --- Bearbetning ---
if run_btn:
    if not uploaded_pdf or not uploaded_step:
        st.error("⚠️ Du måste ladda upp BÅDE en PDF-ritning och en STEP-fil.")
    else:
        with st.spinner("Analyserar ritning, identifierar tillverkningsmetod och beräknar material..."):
            # 1. AI-avläsning
            doc = fitz.open(stream=uploaded_pdf.getvalue(), filetype="pdf")
            pdf_text = "".join([page.get_text() + "\n" for page in doc])
            doc.close()

            ai_data = analyze_drawing_with_ai(uploaded_pdf.name, pdf_text)

            # Operationslista
            raw_ops = ai_data.get("Operationer", [
                {"Op": "Op 10", "Maskin": "Kapsåg", "Beskrivning": "Kapa råmaterial"},
                {"Op": "Op 20", "Maskin": "CNC Bearbetning", "Beskrivning": "Bearbetning"}
            ])
            st.session_state.operations_list = [
                {"id": str(uuid.uuid4()), "Op": op.get("Op", f"Op {(idx+1)*10}"), "Maskin": op.get("Maskin", ""), "Beskrivning": op.get("Beskrivning", "")}
                for idx, op in enumerate(raw_ops)
            ]

            # 2. Material, Benämning och Revision
            drawing_mat = ai_data.get("Material", "Okänt")
            benamning = ai_data.get("Benamning", "Okänd detalj")
            revision = ai_data.get("Revision", "-")
            active_densitet = get_density_from_material(drawing_mat)
            visat_material = drawing_mat

            # 3. STEP-analys
            os.makedirs(STEP_FOLDER, exist_ok=True)
            step_bytes = uploaded_step.getvalue()
            step_path = os.path.join(STEP_FOLDER, uploaded_step.name)
            with open(step_path, "wb") as f:
                f.write(step_bytes)

            svg_b64 = None
            try:
                cad = cq.importers.importStep(step_path)
                shape = cad.val()
                bb = shape.BoundingBox()
                dim_list = sorted([bb.xlen, bb.ylen, bb.zlen])
                dx, dy, dz = bb.xlen, bb.ylen, bb.zlen
                vol_cm3 = shape.Volume() / 1000.0
                weight_kg = (vol_cm3 * active_densitet) / 1000.0

                ai_form = str(ai_data.get("Formtyp", "")).strip().capitalize()
                if ai_form == "Plåt" or ("plåt" in str(ai_data.get("Krav", "")).lower() or "laser" in str(ai_data.get("Operationer", "")).lower()):
                    shape_type = "Plåt"
                elif ai_form == "Rundstång" or "rund" in drawing_mat.lower() or abs(dim_list[0] - dim_list[1]) < 1.0:
                    shape_type = "Rundstång"
                else:
                    shape_type = "Block"

                if shape_type == "Plåt":
                    t = dim_list[0]
                    w = dim_list[1] + 5.0
                    l = dim_list[2] + 5.0
                    raw_vol_cm3 = (t * w * l) / 1000.0
                    raw_weight_kg = (raw_vol_cm3 * active_densitet) / 1000.0
                    fardigmatt_str = f"t={dim_list[0]:.1f} × {dim_list[1]:.1f} × {dim_list[2]:.1f} mm"
                    ramatt_str = f"Plåt t={t:.1f} ({w:.0f} × {l:.0f} mm)"

                elif shape_type == "Rundstång":
                    diameter = dim_list[1]
                    length = dim_list[2]
                    raw_dia = diameter + 5.0
                    raw_len = length + 5.0
                    raw_vol_cm3 = (math.pi * ((raw_dia / 2.0) ** 2) * raw_len) / 1000.0
                    raw_weight_kg = (raw_vol_cm3 * active_densitet) / 1000.0
                    fardigmatt_str = f"Ø{diameter:.1f} × {length:.1f} mm"
                    ramatt_str = f"Ø{raw_dia:.1f} × {raw_len:.1f} mm (Rundstång)"

                else:
                    raw_dx, raw_dy, raw_dz = dx + 5.0, dy + 5.0, dz + 5.0
                    raw_vol_cm3 = (raw_dx * raw_dy * raw_dz) / 1000.0
                    raw_weight_kg = (raw_vol_cm3 * active_densitet) / 1000.0
                    fardigmatt_str = f"{dx:.1f} × {dy:.1f} × {dz:.1f} mm"
                    ramatt_str = f"{raw_dx:.1f} × {raw_dy:.1f} × {raw_dz:.1f} mm (Block)"

                scrap_kg = max(0.0, raw_weight_kg - weight_kg)

                art_nr = ai_data.get("Artikelnummer", "Okänt")
                driven = ai_data.get("DrivnaVerktyg", True)
                jimotec_prefix = get_jimotec_code(visat_material, shape_type, dim_list, driven)
                jimotec_full_artnr = f"{jimotec_prefix}-{art_nr}"

                # 3D SVG-vy
                svg_path = os.path.join(STEP_FOLDER, "preview.svg")
                exporters.export(
                    cad,
                    svg_path,
                    opt={
                        "width": 280,
                        "height": 200,
                        "marginLeft": 10,
                        "marginTop": 10,
                        "projectionDir": (1.2, 1.5, 1.0),
                        "showAxes": False,
                        "strokeWidth": 1.0,
                        "strokeColor": (0, 74, 153),
                        "hiddenColor": (215, 215, 215)
                    }
                )
                if os.path.exists(svg_path):
                    with open(svg_path, "rb") as svg_file:
                        svg_b64 = base64.b64encode(svg_file.read()).decode("utf-8")

            except Exception as e:
                st.error(f"Kunde inte läsa STEP-filen: {e}")
                st.stop()

            # 4. PDF Stämpling
            os.makedirs(OUTPUT_FOLDER, exist_ok=True)
            stamped_name = f"Beredd_{uploaded_pdf.name}"
            stamped_path = os.path.join(OUTPUT_FOLDER, stamped_name)

            if selected_template and selected_template != "Ingen mall":
                tmpl_path = os.path.join(TEMPLATES_DIR, selected_template)
                spec = importlib.util.spec_from_file_location("dynamic_template", tmpl_path)
                tmpl_mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(tmpl_mod)
                doc = fitz.open(stream=uploaded_pdf.getvalue(), filetype="pdf")
                tmpl_mod.apply_template(doc, LOGO_PATH)
                doc.save(stamped_path)
                doc.close()
            else:
                with open(stamped_path, "wb") as f:
                    f.write(uploaded_pdf.getvalue())

            with open(stamped_path, "rb") as f_stamped:
                stamped_pdf_bytes = f_stamped.read()

            # Spara komplett data i session state
            st.session_state.ber_result = {
                "jimotec_full_artnr": jimotec_full_artnr,
                "art_nr": art_nr,
                "benamning": benamning,
                "revision": revision,
                "ai_data": ai_data,
                "visat_material": visat_material,
                "densitet": active_densitet,
                "fardigmatt_str": fardigmatt_str,
                "weight_kg": weight_kg,
                "ramatt_str": ramatt_str,
                "raw_weight_kg": raw_weight_kg,
                "scrap_kg": scrap_kg,
                "svg_b64": svg_b64,
                "stamped_name": stamped_name,
                "stamped_path": stamped_path,
                "stamped_pdf_bytes": stamped_pdf_bytes,
                "step_name": uploaded_step.name,
                "step_bytes": step_bytes
            }

# --- Visa Resultat ---
if st.session_state.ber_result and uploaded_files:
    res = st.session_state.ber_result

    # RAD 1: Ritningsdata & 3D-Vy
    res_col1, res_col2, res_col3 = st.columns([1.5, 1.4, 1.3])

    with res_col1:
        st.markdown("#### 📋 Ritningsdata")
        st.markdown(f"**Jimotec Artnr:** <span style='font-size:1.15rem; color:#d9381e; font-weight:bold;'>{res['jimotec_full_artnr']}</span>", unsafe_allow_html=True)
        st.markdown(f"**Benämning:** **{res['benamning']}**")
        st.markdown(f"**Ritningsnr:** `{res['art_nr']}` &nbsp;&nbsp; *(Revision: **{res['revision']}**)*")
        st.markdown(f"**Material på ritning:** **{res['visat_material']}** &nbsp;&nbsp; *(Densitet: **{res['densitet']:.2f} g/cm³**)*")
        st.markdown(f"**Ytbehandling:** {res['ai_data'].get('Ytbehandling', 'Ingen')}")
        st.markdown(f"**Krav:** {res['ai_data'].get('Krav', 'Inga')}")

    with res_col2:
        st.markdown("#### ⚖️ Mått & Volym")
        st.markdown(f"**Material:** **{res['visat_material']}** (*{res['densitet']:.2f} g/cm³*)")
        st.markdown(f"**Detaljvikt:** **{res['weight_kg']:.3f} kg** ({res['weight_kg']*1000:.1f} g)")
        st.markdown(f"**Färdigmått:** {res['fardigmatt_str']}")
        st.markdown(f"**Råmått:** {res['ramatt_str']}")
        st.markdown(f"**Råmaterialvikt:** **{res['raw_weight_kg']:.3f} kg**")

    with res_col3:
        st.markdown("#### 🧊 3D-Vy")
        if res["svg_b64"]:
            st.markdown(
                f'<div style="background:#ffffff; border:1px solid #d0d7de; border-radius:8px; padding:6px; text-align:center;">'
                f'<img src="data:image/svg+xml;base64,{res["svg_b64"]}" style="max-width:100%; height:auto;" />'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            st.caption("Ingen bild tillgänglig.")

    st.markdown("---")

    # RAD 2: Materiallista & Operationsplan
    tab_mat, tab_ops = st.columns([1, 1.4])

    with tab_mat:
        st.markdown("#### 📦 Materiallista / Inköpsunderlag")
        mat_data = {
            "Parameter": ["Jimotec Artnr", "Benämning", "Ritningsnr", "Revision", "Materialval", "Densitet", "Färdigmått", "Råmått (Sågsnitt)", "Ämnesvikt (Inköp)", "Detaljvikt (Färdig)", "Spånförlust"],
            "Specifikation": [
                res["jimotec_full_artnr"],
                str(res["benamning"]),
                str(res["art_nr"]),
                str(res["revision"]),
                str(res["visat_material"]),
                f"{res['densitet']:.2f} g/cm³",
                res["fardigmatt_str"],
                res["ramatt_str"],
                f"{res['raw_weight_kg']:.3f} kg",
                f"{res['weight_kg']:.3f} kg",
                f"{res['scrap_kg']:.3f} kg ({((res['scrap_kg']/res['raw_weight_kg'])*100):.1f} %)"
            ]
        }
        st.dataframe(pd.DataFrame(mat_data), use_container_width=True, hide_index=True)

    with tab_ops:
        st.markdown("#### 🛠️ Operationslista (Beredning)")
        
        delete_idx = None
        insert_after_idx = None

        for idx, op in enumerate(st.session_state.operations_list):
            op_id = op["id"]
            c_op, c_mask, c_besk, c_ins, c_del = st.columns([1.1, 2.1, 4.2, 0.7, 0.7])
            
            with c_op:
                op_val = st.text_input(f"op_{op_id}", value=op["Op"], label_visibility="collapsed", key=f"f_op_{op_id}")
            with c_mask:
                mask_val = st.text_input(f"mask_{op_id}", value=op["Maskin"], label_visibility="collapsed", key=f"f_mask_{op_id}")
            with c_besk:
                besk_val = st.text_input(f"besk_{op_id}", value=op["Beskrivning"], label_visibility="collapsed", key=f"f_besk_{op_id}")
            with c_ins:
                if st.button("➕", key=f"ins_{op_id}", help="Infoga rad under denna"):
                    insert_after_idx = idx
            with c_del:
                if st.button("🗑️", key=f"del_{op_id}", help="Ta bort denna rad"):
                    delete_idx = idx

            op["Op"] = op_val
            op["Maskin"] = mask_val
            op["Beskrivning"] = besk_val

        # Ta bort rad
        if delete_idx is not None:
            del st.session_state.operations_list[delete_idx]
            st.rerun()

        # Infoga rad
        if insert_after_idx is not None:
            new_item = {
                "id": str(uuid.uuid4()),
                "Op": f"Op {(insert_after_idx + 2) * 10}",
                "Maskin": "CNC / Verkstad",
                "Beskrivning": "Ny operation"
            }
            st.session_state.operations_list.insert(insert_after_idx + 1, new_item)
            st.rerun()

        # Lägg till på slutet
        st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
        if st.button("➕ Lägg till ny operation på slutet", use_container_width=True):
            next_num = (len(st.session_state.operations_list) + 1) * 10
            st.session_state.operations_list.append({
                "id": str(uuid.uuid4()),
                "Op": f"Op {next_num}",
                "Maskin": "CNC / Verkstad",
                "Beskrivning": "Ny operation"
            })
            st.rerun()

    st.markdown("---")

    # RAD 3: Spara och Öppna
    clean_artnr = re.sub(r'[\\/*?:"<>|]', '_', str(res["jimotec_full_artnr"])).strip()
    
    col_save, col_dl = st.columns([1.3, 1])

    with col_save:
        if st.button(f"💾 Spara till Artikelregister ({clean_artnr})", type="primary", use_container_width=True, key=f"save_btn_{clean_artnr}"):
            # 1. Skapa lokal mapp
            local_save_dir = os.path.join(BASE_DIR, "Klara_Beredningar", clean_artnr)
            os.makedirs(local_save_dir, exist_ok=True)

            # Skapa servermapp direkt på Y:
            remote_save_dir = os.path.join(r"Y:\Artikelregister", clean_artnr)
            try:
                os.makedirs(remote_save_dir, exist_ok=True)
            except Exception:
                pass

            # Generera TXT Underlag
            txt_content = (
                f"JIMOTEC PRODUKTIONSBEREDNING\n"
                f"====================================\n\n"
                f"Jimotec Artnr:     {res['jimotec_full_artnr']}\n"
                f"Benämning:         {res['benamning']}\n"
                f"Ritningsnr:        {res['art_nr']}\n"
                f"Revision:          {res['revision']}\n"
                f"Material:          {res['visat_material']} (Densitet: {res['densitet']:.2f} g/cm3)\n"
                f"Ytbehandling:      {res['ai_data'].get('Ytbehandling', 'Ingen')}\n"
                f"Krav / Notering:   {res['ai_data'].get('Krav', 'Inga')}\n\n"
                f"Färdigmått:        {res['fardigmatt_str']}\n"
                f"Detaljvikt:        {res['weight_kg']:.3f} kg\n"
                f"Råmått:            {res['ramatt_str']}\n"
                f"Ämnesvikt (Inköp): {res['raw_weight_kg']:.3f} kg\n"
                f"Spånförlust:       {res['scrap_kg']:.3f} kg ({((res['scrap_kg']/res['raw_weight_kg'])*100):.1f} %)\n\n"
                f"OPERATIONSPLAN\n"
                f"------------------------------------\n"
            )
            for op in st.session_state.operations_list:
                txt_content += f"{op['Op']:<10} | {op['Maskin']:<20} | {op['Beskrivning']}\n"

            # Skriv TXT
            with open(os.path.join(local_save_dir, "Underlag_Beredning.txt"), "w", encoding="utf-8") as tf:
                tf.write(txt_content)
            try:
                with open(os.path.join(remote_save_dir, "Underlag_Beredning.txt"), "w", encoding="utf-8") as tf:
                    tf.write(txt_content)
            except Exception:
                pass

            # Skriv PDF
            pdf_bytes = res.get("stamped_pdf_bytes")
            if not pdf_bytes and os.path.exists(res.get("stamped_path", "")):
                with open(res["stamped_path"], "rb") as f_in:
                    pdf_bytes = f_in.read()
            if pdf_bytes:
                with open(os.path.join(local_save_dir, res["stamped_name"]), "wb") as f_out:
                    f_out.write(pdf_bytes)
                try:
                    with open(os.path.join(remote_save_dir, res["stamped_name"]), "wb") as f_out:
                        f_out.write(pdf_bytes)
                except Exception:
                    pass

            # Skriv STEP
            step_bytes = res.get("step_bytes")
            if not step_bytes and os.path.exists(os.path.join(STEP_FOLDER, res.get("step_name", ""))):
                with open(os.path.join(STEP_FOLDER, res["step_name"]), "rb") as f_in:
                    step_bytes = f_in.read()
            if step_bytes:
                with open(os.path.join(local_save_dir, res["step_name"]), "wb") as f_out:
                    f_out.write(step_bytes)
                try:
                    with open(os.path.join(remote_save_dir, res["step_name"]), "wb") as f_out:
                        f_out.write(step_bytes)
                except Exception:
                    pass

            st.session_state.local_saved_dir = local_save_dir
            st.session_state.remote_saved_dir = remote_save_dir
            st.session_state.save_status_msg = f"✅ Beredningen har sparats direkt till Y:\\Artikelregister\\{clean_artnr}!"
            st.rerun()

        # Meddelande och knappar
        if st.session_state.save_status_msg:
            st.success(st.session_state.save_status_msg)

        if st.session_state.remote_saved_dir:
            col_o1, col_o2 = st.columns(2)
            with col_o1:
                if st.button("📂 Öppna på Y: (Server)", use_container_width=True):
                    subprocess.Popen(f'explorer.exe "{st.session_state.remote_saved_dir}"')
            with col_o2:
                if st.button("📂 Öppna Lokal Mapp (C:)", use_container_width=True):
                    subprocess.Popen(f'explorer.exe "{st.session_state.local_saved_dir}"')

    with col_dl:
        with open(res["stamped_path"], "rb") as f:
            st.download_button(
                label=f"⬇️ Ladda ner stämplad ritning",
                data=f,
                file_name=res["stamped_name"],
                mime="application/pdf",
                use_container_width=True
            )