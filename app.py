import streamlit as st
from PIL import Image
import tempfile, os, webbrowser
from stego.simple_lsb import hide_text, reveal_text

st.set_page_config(page_title="StegoLink Neon Glass", layout="wide")

# Load CSS
with open("static/neon.css", "r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("<h1>🛰️ StegoLink — Glassmorphism Edition</h1>", unsafe_allow_html=True)

# ------------------- SIDEBAR: ENCODER -------------------
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

# ------------------- MAIN PANEL: DECODER -------------------
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.header("🔓 Decode Hidden Text")

encoded_upload = st.file_uploader("Upload encoded PNG", type=["png"])

decode_pressed = st.button("Decode Now")
reset_pressed = st.button("Reset")

if reset_pressed:
    st.experimental_rerun()

if decode_pressed:
    if encoded_upload:
        t = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        Image.open(encoded_upload).convert("RGB").save(t.name)

        result = reveal_text(t.name)

        if not result:
            st.error("No hidden text found.")
        else:
            # hide extracted text if it's a link
            if result.startswith("http://") or result.startswith("https://"):
                st.success("Link extracted successfully!")
                
                # button instead of showing raw URL
                if st.button("🔗 Open Link"):
                    webbrowser.open_new_tab(result)

                # auto-open
                try:
                    webbrowser.open_new_tab(result)
                except:
                    pass

            else:
                st.success("Extracted Text:")
                st.code(result)
    else:
        st.error("Please upload an encoded PNG.")

st.markdown("</div>", unsafe_allow_html=True)
