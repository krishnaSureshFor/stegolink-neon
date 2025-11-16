import streamlit as st
from stegano import lsb
from PIL import Image
import tempfile
import webbrowser
import os
import time

# ---------------- Page config ----------------
st.set_page_config(page_title="StegoLink — Neon Cyber", layout="wide", initial_sidebar_state="expanded")

# ---------------- Custom CSS + Animations ----------------
NEON_CSS = """
<style>
:root{
  --bg1: #0f1724;
  --bg2: #081223;
  --neon1: #00e6ff;
  --neon2: #b400ff;
  --accent: #7efc8d;
  --glass: rgba(255,255,255,0.04);
}

/* page background gradient + slow animated */
[data-testid="stAppViewContainer"] {
  background: radial-gradient(circle at 10% 10%, rgba(0,230,255,0.06), transparent 10%),
              radial-gradient(circle at 90% 90%, rgba(180,0,255,0.06), transparent 8%),
              linear-gradient(135deg, var(--bg1), var(--bg2));
  min-height: 100vh;
  background-size: 200% 200%;
  animation: bgShift 12s ease infinite;
  color: #e6f0ff;
}

/* subtle movement */
@keyframes bgShift {
  0% { background-position: 0% 0%; }
  50% { background-position: 100% 100%; }
  100% { background-position: 0% 0%; }
}

/* Glass card */
.trendy-card {
  background: rgba(255,255,255,0.03);
  border-radius: 16px;
  padding: 22px;
  border: 1px solid rgba(255,255,255,0.06);
  box-shadow: 0 8px 30px rgba(2,6,23,0.6), 0 0 18px rgba(0, 230, 255, 0.03) inset;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  transition: transform 0.45s cubic-bezier(.2,.8,.2,1), box-shadow 0.45s;
  transform: translateY(0px);
}

/* hover lift */
.trendy-card:hover {
  transform: translateY(-8px) scale(1.01);
  box-shadow: 0 20px 60px rgba(2,6,23,0.9), 0 0 48px rgba(0, 230, 255, 0.08);
}

/* Neon title */
h1 {
  text-align: center;
  font-size: 2.6rem;
  margin: 8px 0 18px 0;
  background: linear-gradient(90deg, var(--neon1), var(--neon2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 800;
}

/* subtitle */
.small {
  color: rgba(230,240,255,0.7);
  margin-top: -12px;
  margin-bottom: 18px;
  text-align:center;
}

/* Buttons */
.stButton>button {
  border-radius: 12px;
  padding: 10px 16px;
  font-weight: 700;
  border: none;
  background: linear-gradient(90deg, rgba(0,230,255,0.12), rgba(180,0,255,0.12));
  color: #e8f9ff;
  box-shadow: 0 6px 20px rgba(0,0,0,0.6), 0 0 20px rgba(0,230,255,0.03);
  transition: transform .18s ease, box-shadow .18s ease;
}

/* glowing primary style via class toggles in HTML below */
.btn-neon {
  background: linear-gradient(90deg, #00eaff, #9b36ff);
  color: white !important;
  box-shadow: 0 6px 30px rgba(155,54,255,0.18), 0 0 30px rgba(0,234,255,0.12);
}

/* subtle hover */
.stButton>button:hover {
  transform: translateY(-3px);
  box-shadow: 0 18px 40px rgba(0,0,0,0.65), 0 0 36px rgba(0,234,255,0.12);
}

/* input styles */
.stTextInput>div>div>input, .stFileUploader>div>div>input {
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.06) !important;
  background: rgba(255,255,255,0.02);
  color: #e6f0ff;
}

/* small neon accent line */
.accent-line {
  height: 4px;
  border-radius: 10px;
  background: linear-gradient(90deg, rgba(0,230,255,0.8), rgba(180,0,255,0.8));
  margin-bottom: 12px;
}

/* floating micro-card effect */
.float {
  animation: floaty 6s ease-in-out infinite;
}

@keyframes floaty {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-6px); }
  100% { transform: translateY(0px); }
}

/* result box */
.result {
  background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
  padding: 14px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.04);
  font-weight: 600;
}

/* small helpful text */
.helper {
  color: rgba(200,220,255,0.7);
  font-size: 0.92rem;
  margin-top: 8px;
}
</style>
"""

st.markdown(NEON_CSS, unsafe_allow_html=True)

# ---------------- Header ----------------
st.markdown("<h1>🛰️ StegoLink — Neon Cyber</h1>", unsafe_allow_html=True)
st.markdown('<div class="small">Hide secret links inside images • Modern neon UI • Encoder in sidebar • Decoder in main view</div>', unsafe_allow_html=True)
st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)

# ---------------- Layout columns ----------------
left, right = st.columns([1, 1], gap="large")

# ---------- SIDEBAR (Encoder) ----------
with st.sidebar:
    st.markdown('<div class="trendy-card float">', unsafe_allow_html=True)
    st.markdown("### 🔏 Encode (Sidebar)")
    st.markdown('<div class="helper">Upload a PNG (recommended). Enter the text or URL to hide. Click Encode to generate a stego-image.</div>', unsafe_allow_html=True)
    cover_image = st.file_uploader("Cover image (PNG preferred)", type=["png", "jpg", "jpeg"])
    secret_text = st.text_input("Text / Link to hide")
    encode_btn = st.button("Encode & Generate", key="encode_btn")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- ENCODING LOGIC ----------
if 'encoded_path' not in st.session_state:
    st.session_state.encoded_path = None

if encode_btn:
    if not cover_image or not secret_text:
        st.sidebar.error("Please upload an image and enter text to hide.")
    else:
        try:
            # Save uploaded cover image to temp PNG (force PNG to preserve LSB)
            temp_cover = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            Image.open(cover_image).convert("RGBA").save(temp_cover.name, format="PNG")

            # Hide text
            encoded_img = lsb.hide(temp_cover.name, secret_text)
            out_path = os.path.join(os.getcwd(), "stego_output.png")
            encoded_img.save(out_path)
            st.session_state.encoded_path = out_path

            st.sidebar.success("✔ Hidden image created!")
            with open(out_path, "rb") as f:
                st.sidebar.download_button("⬇ Download encoded image", data=f, file_name="stego_link.png")
            st.sidebar.info("Tip: Use the exact downloaded PNG to decode (don't re-save or compress).")
        except Exception as e:
            st.sidebar.error(f"Encoding failed: {e}")

# ---------- MAIN VIEW (Decoder) ----------
with left:
    st.markdown('<div class="trendy-card float">', unsafe_allow_html=True)
    st.subheader("🔓 Decode (Main View)")
    st.markdown('<div class="helper">Upload an encoded image and press Decode. If the extracted text is a link, you can open it in a new tab.</div>', unsafe_allow_html=True)

    decode_upload = st.file_uploader("Upload encoded image to decode", type=["png", "jpg", "jpeg"], key="decode_uploader")
    decode_btn = st.button("Decode & Reveal", key="decode_btn")
    st.markdown("</div>", unsafe_allow_html=True)

    if decode_btn:
        if not decode_upload:
            st.error("Please upload an encoded image to decode.")
        else:
            try:
                temp_in = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                Image.open(decode_upload).convert("RGBA").save(temp_in.name, format="PNG")

                extracted = lsb.reveal(temp_in.name)
                if extracted is None:
                    st.error("❌ No hidden text found. Make sure image is original PNG produced by this tool and not compressed/edited.")
                else:
                    st.success("✔ Hidden text extracted:")
                    st.markdown(f'<div class="result">{st.session_state.get("last_extracted","") or extracted}</div>', unsafe_allow_html=True)
                    # store for re-use
                    st.session_state.last_extracted = extracted

                    # If looks like a link: present an open button and clickable link
                    if extracted.startswith(("http://", "https://")):
                        st.markdown(f'<div style="margin-top:10px;"><a href="{extracted}" target="_blank" style="text-decoration:none;"><button class="btn-neon">Open Link in New Tab</button></a></div>', unsafe_allow_html=True)
                        # Try to open programmatically (may be blocked on some deployments)
                        try:
                            webbrowser.open_new_tab(extracted)
                            st.info("Tried to open link in a new browser tab. If it did not open, click the button above.")
                        except:
                            st.warning("Auto-open blocked by environment — click the button above.")
                    else:
                        st.info("Extracted content is not a URL. Copy/paste or use it as needed.")
            except Exception as e:
                st.error(f"Decoding failed: {e}")

# ---------- Right column: preview & tips ----------
with right:
    st.markdown('<div class="trendy-card float">', unsafe_allow_html=True)
    st.subheader("🛰 Live Preview & Tips")
    # show last encoded image preview if available
    if st.session_state.encoded_path and os.path.exists(st.session_state.encoded_path):
        st.markdown("**Preview of last generated stego image**")
        st.image(st.session_state.encoded_path, use_column_width=True)
        st.markdown('<div class="helper">Downloaded file: <code>stego_link.png</code>. Keep this file unchanged to decode successfully.</div>', unsafe_allow_html=True)
    else:
        st.markdown("<div class='helper'>No encoded image in this session yet. Encode a link from the sidebar to see preview here.</div>", unsafe_allow_html=True)

    st.markdown("---", unsafe_allow_html=True)
    st.markdown("### ⚠️ Best Practices", unsafe_allow_html=True)
    st.markdown("""
    - ✅ Use **PNG** as cover image (lossless).  
    - ❌ Avoid re-saving or compressing (JPEG) after encoding — that destroys hidden bits.  
    - 🔐 For privacy, avoid hiding extremely sensitive data (this method is simple LSB).  
    - ⚙️ Want stronger secrecy? Ask to add password encryption (AES) before hiding.
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Footer ----------
st.markdown('<div style="text-align:center; margin-top:18px; color:rgba(200,220,255,0.6)">Made with ⚡ by you — Neon Cyber edition</div>', unsafe_allow_html=True)
