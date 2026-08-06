import streamlit as st
import streamlit.components.v1 as components

# CSS som drar upp hela blocket mot toppen av sidan
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem !important;
    }
    .cover-box {
        position: relative;
        margin-top: -20px;
    }
    .cover-box::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 85px;
        background-color: white;
        z-index: 999;
    }
    </style>
""", unsafe_allow_html=True)

# Din publika webblänk från Google Docs
pub_url = "https://docs.google.com/document/d/e/2PACX-1vSdpzfOs5cAVb1y5Ymj8RoAhF_ggtgPVW_soLJQuVmS814SYneNluSO4G9TSMjJArANLzovqY-cdZ6a/pub"
edit_url = "https://docs.google.com/document/d/1Mw5XxUYOIcBO7DxZyUXVNYxTcPB4M63oEmpcBtLKGjI/edit?tab=t.0"

# Visar dokumentet i lådan
st.markdown('<div class="cover-box">', unsafe_allow_html=True)
components.iframe(pub_url, height=600, scrolling=True)
st.markdown('</div>', unsafe_allow_html=True)

st.write("---")

# Knapp för att redigera i Google Docs
st.markdown(
    f'<a href="{edit_url}" target="_blank"><button style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; font-weight: bold;">Öppna och redigera i Google Docs</button></a>',
    unsafe_allow_html=True
)
