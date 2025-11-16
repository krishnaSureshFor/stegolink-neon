import streamlit as st
from PIL import Image
import tempfile, os
from stego.simple_lsb import hide_text, reveal_text

# Page config
st.set_page_config(page_title="StegoLink Neon Glass", layout="wide")

# Load CSS
with open("static/neon.css", "r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Title
st.markdown("<h1>🛰️ StegoLink — Glassmorphism Edition</h1>", unsafe_allow_html=True)

# ---- SIDEBAR (ENCODER) ----
st.sidebar.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.sidebar.header("🔏 Encode Text Into PNG")

cover = st.sidebar.file_uploader("Upload Cover PNG", type=["png"])
secret_text = st.sidebar.text_input("Enter text/link to hide")

if st.sidebar.button("Encode & Generate"):
    if cover and secret_text:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        Image.open(cover).convert("RGB").save(tmp.name)

        output_path = "hidden_output.png"
        hide_text(tmp.name, secret_text, output_path)

        st.sidebar.success("✔ Hidden data embedded!")
        with open(output_path, "rb") as f:
            st.sidebar.download_button("⬇ Download Encoded PNG", f, "hidden_output.png")
    else:
        st.sidebar.error("Upload PNG and enter text first.")

st.sidebar.markdown("</div>", unsafe_allow_html=True)


# ---- MAIN PANEL (DECODER) ----
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.header("🔓 Decode Hidden Text")

encoded_upload = st.file_uploader("Upload encoded PNG", type=["png"])

if st.button("Decode Now"):
    if encoded_upload:
        t = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        Image.open(encoded_upload).convert("RGB").save(t.name)

        result = reveal_text(t.name)
        st.success("Extracted text:")
        st.code(result)

        if result.startswith("http"):
            st.markdown(f"[Open Link]({result})")

    else:
        st.error("Please upload an encoded PNG.")

st.markdown("</div>", unsafe_allow_html=True)
