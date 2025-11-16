import streamlit as st
from PIL import Image
import tempfile, os, webbrowser
from stego.simple_lsb import hide_text, reveal_text

st.set_page_config(page_title="StegoLink Glass", layout="wide")

# Load CSS
with open("static/neon.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Title
st.markdown("<h1 style='text-align:center; margin-top:20px;'>🛰️ StegoLink — Glassmorphism Edition</h1>", unsafe_allow_html=True)

# -------------------------- SIDEBAR --------------------------
st.sidebar.markdown("<h3>🔏 Encode Text Into PNG</h3>", unsafe_allow_html=True)

cover = st.sidebar.file_uploader("Upload Cover PNG", type=["png"])
secret = st.sidebar.text_input("Enter text/link to hide")

if st.sidebar.button("Encode"):
    if cover and secret:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        Image.open(cover).convert("RGB").save(tmp.name)

        out = "hidden_output.png"
        hide_text(tmp.name, secret, out)

        st.sidebar.success("✔ Encoded successfully!")
        st.sidebar.download_button("Download PNG", open(out, "rb"), "hidden_output.png")
    else:
        st.sidebar.error("Upload PNG + Enter text.")

# -------------------------- MAIN PANEL --------------------------
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.subheader("🔓 Decode Hidden Text")

encoded = st.file_uploader("Upload encoded PNG", type=["png"], key="decode")

col1, col2 = st.columns(2)
decode_btn = col1.button("Decode Now")
reset_btn = col2.button("Reset")

if reset_btn:
    st.experimental_rerun()

if decode_btn:
    if encoded:
        tmp2 = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        Image.open(encoded).convert("RGB").save(tmp2.name)

        text = reveal_text(tmp2.name)

        if not text:
            st.error("No hidden text found.")
        else:
            # If it's a link → button only (hidden text)
            if text.startswith(("http://", "https://")):
                st.success("✔ Link extracted!")
                if st.button("Open Link"):
                    webbrowser.open_new_tab(text)

                # Auto open try:
                try:
                    webbrowser.open_new_tab(text)
                except:
                    pass

            else:
                st.success("Extracted Text:")
                st.code(text)
    else:
        st.error("Upload image first.")

st.markdown("</div>", unsafe_allow_html=True)
