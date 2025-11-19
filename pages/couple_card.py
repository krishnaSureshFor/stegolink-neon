import streamlit as st
from PIL import Image
import tempfile, base64, requests, os, time
from stego.simple_lsb import hide_text
from urllib.parse import quote_plus

IMGBB_API_KEY = os.environ.get("IMGBB_API_KEY", "")


def upload_to_imgbb(path):
    if not IMGBB_API_KEY:
        st.error("⚠️ ImgBB API key missing.")
        return None

    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    url = "https://api.imgbb.com/1/upload"
    payload = {"key": IMGBB_API_KEY, "image": encoded}

    try:
        res = requests.post(url, data=payload, timeout=20).json()
        if res.get("success"):
            return res["data"]["url"]
        return None
    except Exception as e:
        st.error(f"Upload error: {e}")
        return None



def render():

    # Load Love Theme CSS
    try:
        with open("static/love.css", "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        pass

    st.markdown("<h1 class='love-title'>💖 Create Your Memory Card</h1>", unsafe_allow_html=True)
    st.markdown("<div class='love-card'>", unsafe_allow_html=True)

    main = st.file_uploader("Upload Main Picture", type=["png", "jpg", "jpeg"])

    if main:
        st.image(main, width=260)

    extras = st.file_uploader(
        "Upload 5 Extra Pictures",
        accept_multiple_files=True,
        type=["png", "jpg", "jpeg"]
    )

    if extras:
        st.markdown("<h4>Extra Preview</h4>", unsafe_allow_html=True)
        cols = st.columns(3)
        for i, f in enumerate(extras):
            img = Image.open(f)
            img.thumbnail((140, 140))
            cols[i % 3].image(img)

    msg = st.text_area("Enter Your Message ❤️")
    expiry = st.selectbox(
        "Expiry Time",
        ["10 Minutes", "1 Hour", "1 Day", "7 Days"]
    )

    if st.button("Generate Memory Card ❤️"):

        if not main:
            st.error("Upload main picture.")
            return
        if not extras or len(extras) != 5:
            st.error("Upload exactly 5 extra pictures.")
            return
        if not msg:
            st.error("Enter a message.")
            return

        t_main = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        Image.open(main).convert("RGB").save(t_main.name)

        encoded_path = "encoded_memory.png"
        hide_text(t_main.name, msg, encoded_path)

        st.info("Uploading… 💞")

        main_url = upload_to_imgbb(encoded_path)
        if not main_url:
            return

        extra_urls = []
        for f in extras:
            t = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            Image.open(f).convert("RGB").save(t.name)
            up = upload_to_imgbb(t.name)
            if not up:
                return
            extra_urls.append(up)

        now = int(time.time())
        expiry_map = {
            "10 Minutes": 600,
            "1 Hour": 3600,
            "1 Day": 86400,
            "7 Days": 604800,
        }
        exp_ts = now + expiry_map[expiry]

        enc_msg = quote_plus(msg.strip())

        base = st.secrets.get("APP_BASE_URL", "")
        if base:
            url = (
                f"{base}?view=1&img={main_url}"
                f"&a1={extra_urls[0]}&a2={extra_urls[1]}&a3={extra_urls[2]}"
                f"&a4={extra_urls[3]}&a5={extra_urls[4]}"
                f"&msg={enc_msg}&exp={exp_ts}"
            )
        else:
            url = (
                f"?view=1&img={main_url}"
                f"&a1={extra_urls[0]}&a2={extra_urls[1]}&a3={extra_urls[2]}"
                f"&a4={extra_urls[3]}&a5={extra_urls[4]}"
                f"&msg={enc_msg}&exp={exp_ts}"
            )

        st.success("🎉 Memory Card Created!")

        st.link_button("💌 View Card", url)

    st.markdown("</div>", unsafe_allow_html=True)
