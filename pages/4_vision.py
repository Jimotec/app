import os
import streamlit as st
from google import genai
from google.genai import types

# 1. Konfigurera sidan för Vision
st.set_page_config(page_title="Vision & AI - Jimotec AB", layout="wide")

# Dölj standardmenyn i sidopanelen för att matcha app.py
st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("👁️ Vision & AI-Analys")
st.write("Ställ frågor om Jimotecs framtid, analysera flödesscheman från Miro eller ladda upp ritningar.")

# 2. Hämta API-nyckel säkert
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("Ingen Gemini API-nyckel hittades. Kontrollera att GEMINI_API_KEY är inställd.")
    st.stop()

client = genai.Client(api_key=api_key)

# 3. Ladda in sammanställd kontext från alla affärsplanssidor och underlag
def ladda_foretagsdata():
    kontext = ""
    pages_dir = "pages"
    if os.path.exists(pages_dir):
        for file in sorted(os.listdir(pages_dir)):
            if file.endswith(".py") and file != "4_vision.py":
                path = os.path.join(pages_dir, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        kontext += f"\n--- DATA FRÅN {file} ---\n" + f.read()
                except Exception:
                    pass
    return kontext

foretagsdata = ladda_foretagsdata()

system_instruction = f"""
Du är en AI-assistent integrerad under Vision för Jimotec AB. 
Din uppgift är att hjälpa till med strategisk analys, visioner, tolkning av Miro-flödesscheman, processer och ritningar.
Använd alltid Jimotecs interna underlag som bakgrund för dina svar.

HÄR ÄR JIMOTECS INTERNA UNDERLAG OCH STRATEGI:
{foretagsdata}
"""

# 4. Hantera chatthistorik i Streamlit
if "vision_messages" not in st.session_state:
    st.session_state.vision_messages = []

# Visa tidigare meddelanden
for message in st.session_state.vision_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Filuppladdning i sidopanelen för bilder/exporter från Miro
with st.sidebar:
    st.header("📌 Vision & Bildanalys")
    uploaded_file = st.file_uploader("Ladda upp bild/flödesschema (PNG, JPG)", type=["png", "jpg", "jpeg"])
    
    if st.button("Rensa chatthistorik"):
        st.session_state.vision_messages = []
        st.rerun()

# 6. Chatt-input
if user_prompt := st.chat_input("Skriv din fråga eller analysbegäran här..."):
    # Spara och visa användarens meddelande
    st.session_state.vision_messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Förbered innehållet till Gemini
    contents = []
    
    # Om en bild bifogats i sidopanelen
    if uploaded_file is not None:
        image_bytes = uploaded_file.getvalue()
        mime_type = uploaded_file.type
        contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
        user_prompt = f"[BILD BIFOGAD: {uploaded_file.name}] " + user_prompt

    contents.append(user_prompt)

    # Generera svar
    with st.chat_message("assistant"):
        with st.spinner("Analyserar..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.3
                    )
                )
                st.markdown(response.text)
                st.session_state.vision_messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Ett fel uppstod vid analysen: {e}")
