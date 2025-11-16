# pages/hide_link_page.py
import streamlit as st
from PIL import Image
import tempfile, webbrowser, os
from stego.simple_lsb import hide_text, reveal_text

def render():
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("🔐 Hide Link — Encoder & Decoder")

    # Two-column layout: left = encoder, right = decoder
    left, right = st.columns([1,1], gap="large")

    # ---------- ENCODER (left) ----------
    with left:
        st.markdown("### 🔏 Encoder")
        cover = st.file_uploader("Cover image (PNG preferred)", type=["png"], key="enc_cover")
        secret = st.text_input("Enter text/link to hide", key="enc_text")
        encode_btn = st.button("Encode & Generate", key="encode_btn")

        if encode_btn:
            if not cover or not secret:
                st.error("Please upload a cover PNG and enter text.")
            else:
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                Image.open(cover).convert("RGB").save(tmp.name)

                out_path = os.path.join(os.getcwd(), "hidden_output.png")
                try:
                    hide_text(tmp.name, secret, out_path)
                    st.success("✔ Hidden image created.")
                    st.image(out_path, caption="Encoded Preview", use_column_width=True)
                    with open(out_path, "rb") as f:
                        st.download_button("⬇ Download encoded PNG", f, file_name="hidden_output.png")
                except Exception as e:
                    st.error(f"Encoding failed: {e}")

    # ---------- DECODER (right) ----------
    with right:
        st.markdown("### 🔓 Decoder")
        encoded = st.file_uploader("Upload encoded PNG to decode", type=["png"], key="dec_file")
        decode_btn = st.button("Decode Now", key="decode_now")
        reset_btn = st.button("Reset", key="decoder_reset")

        if reset_btn:
            st.experimental_rerun()

        if decode_btn:
            if not encoded:
                st.error("Please upload an encoded PNG first.")
            else:
                tmp2 = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                Image.open(encoded).convert("RGB").save(tmp2.name)

                try:
                    text = reveal_text(tmp2.name)
                    if not text:
                        st.error("No hidden text found.")
                    else:
                        # If it's a link -> hide raw text, show open button and auto-open
                        if text.startswith(("http://","https://")):
                            st.success("✔ Link extracted!")
                            # Show themed button
                            if st.button("🔗 Open Link", key="open_link_btn"):
                                webbrowser.open_new_tab(text)
                            # try automatic open (may be blocked in some hosts)
                            try:
                                webbrowser.open_new_tab(text)
                                st.info("Tried to open link in a new tab.")
                            except:
                                pass
                        else:
                            st.success("Extracted Text:")
                            st.code(text)
                except Exception as e:
                    st.error(f"Decoding failed: {e}")

    st.markdown("</div>", unsafe_allow_html=True)
