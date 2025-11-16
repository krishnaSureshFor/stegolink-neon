# pages/couple_card.py
import streamlit as st
from PIL import Image
import tempfile, base64, requests, os, time
from stego.simple_lsb import hide_text
from urllib.parse import quote_plus

# Set your ImgBB API key here OR set environment variable IMGBB_API_KEY
IMGBB_API_KEY = os.environ.get("IMGBB_API_KEY", "")  # set in your host env or replace here directly

def upload_to_imgbb(path):
    """Upload image file to ImgBB and return image URL. Returns None on failure."""
    if not IMGBB_API_KEY:
        st.error("ImgBB API key not configured. Set environment variable IMGBB_API_KEY or edit the script.")
        return None
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": IMGBB_API_KEY,
        "image": encoded
    }
    try:
        res = requests.post(url, data=payload, timeout=30)
        data = res.json()
        if data.get("success"):
            return data["data"]["url"]
        else:
            st.error("ImgBB upload failed.")
            st.code(data)
            return None
    except Exception as e:
        st.error(f"ImgBB request error: {e}")
        return None

def render():
    # load love.css for this page
    try:
        with open("static/love.css", "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

    st.markdown("<div style='text-align:center;'><h1>💖 Couple Memory Card Maker</h1></div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom:8px; color:rgba(255,255,255,0.9)'>Upload one main picture + 5 extras. Enter a message and choose expiry duration.</div>", unsafe_allow_html=True)
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    main_image = st.file_uploader("Main Picture (will contain hidden message)", type=["png","jpg","jpeg"], key="cc_main")
    extras = st.file_uploader("Extra Pictures (upload exactly 5)", accept_multiple_files=True, type=["png","jpg","jpeg"], key="cc_extras")
    message = st.text_area("Enter your love message", max_chars=1000, key="cc_text")
    duration = st.selectbox("Link expiration", ["10 Minutes","1 Hour","1 Day","7 Days"], key="cc_duration")

    generate = st.button("Generate Memory Card ❤️")

    if generate:
        # validation
        if not main_image:
            st.error("Please upload the main picture.")
            return
        if not extras or len(extras) != 5:
            st.error("Please upload exactly 5 extra images.")
            return
        if not message:
            st.error("Please enter a message.")
            return
        if not IMGBB_API_KEY:
            st.error("ImgBB API key is not configured. Set IMGBB_API_KEY env var or edit the file.")
            return

        # Save main image and encode message
        tmp_main = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        Image.open(main_image).convert("RGB").save(tmp_main.name)
        encoded_path = os.path.join(os.getcwd(), "encoded_love.png")
        try:
            hide_text(tmp_main.name, message, encoded_path)
        except Exception as e:
            st.error(f"Encoding failed: {e}")
            return

        st.info("Uploading images (this may take a few seconds)...")

        main_url = upload_to_imgbb(encoded_path)
        if not main_url:
            return

        extra_urls = []
        for i, f in enumerate(extras):
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            Image.open(f).convert("RGB").save(tmp.name)
            url = upload_to_imgbb(tmp.name)
            if not url:
                st.error("Failed uploading one of the extra images.")
                return
            extra_urls.append(url)

        # compute expiry timestamp
        now = int(time.time())
        dur_map = {"10 Minutes": 10*60, "1 Hour": 60*60, "1 Day": 24*3600, "7 Days": 7*24*3600}
        exp_ts = now + dur_map.get(duration, 24*3600)

        # build view link (URL encode message)
        encoded_msg = quote_plus(message)
        base_url = st.secrets.get("APP_BASE_URL") if "APP_BASE_URL" in st.secrets else None
        # If you host on Streamlit Cloud, set APP_BASE_URL to your app's URL, e.g. https://your-app.streamlit.app
        if base_url:
            view_url = f"{base_url}?view=1&img={main_url}&a1={extra_urls[0]}&a2={extra_urls[1]}&a3={extra_urls[2]}&a4={extra_urls[3]}&a5={extra_urls[4]}&msg={encoded_msg}&exp={exp_ts}"
        else:
            # fallback -- use current page with query params (works when served on same URL)
            view_url = f"?view=1&img={main_url}&a1={extra_urls[0]}&a2={extra_urls[1]}&a3={extra_urls[2]}&a4={extra_urls[3]}&a5={extra_urls[4]}&msg={encoded_msg}&exp={exp_ts}"

        st.success("Your Memory Card is ready!")
        st.markdown(f"<a href='{view_url}' target='_blank' class='love-button'>💌 View Memory Card</a>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
