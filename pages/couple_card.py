# ----------------- couple_card.py -----------------
import streamlit as st
from PIL import Image
import tempfile, base64, requests, os, time
from stego.simple_lsb import hide_text
from urllib.parse import quote_plus


IMGBB_API_KEY = os.environ.get("IMGBB_API_KEY", "")


# --------------- Upload to ImgBB ---------------
def upload_to_imgbb(path):
    if not IMGBB_API_KEY:
        st.error("⚠️ ImgBB API key missing. Add IMGBB_API_KEY in Secrets.")
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



# ----------------- RENDER PAGE -----------------
def render():

    # Load theme
    try:
        with open("static/love.css", "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        pass

    st.markdown("<h1 class='love-title'>💖 Create Your Memory Card</h1>", unsafe_allow_html=True)

    st.markdown("<div class='love-card'>", unsafe_allow_html=True)

    # -------------------------------------------------
    # Main image
    # -------------------------------------------------
    main = st.file_uploader("Upload Main Picture", type=["png", "jpg", "jpeg"])

    if main:
        st.image(main, width=260)

    # -------------------------------------------------
    # Extra images
    # -------------------------------------------------
    extras = st.file_uploader("Upload 5 Extra Pictures",
                              accept_multiple_files=True,
                              type=["png", "jpg", "jpeg"])

    # ---------------------- Thumbnails ----------------------
    if extras:
        st.markdown("""
            <div style='font-size:1.1rem;font-weight:600;margin-top:12px;'>
                Extra Photo Preview
            </div>
        """, unsafe_allow_html=True)

        cols = st.columns(3)
        for i, f in enumerate(extras):
            img = Image.open(f)
            img.thumbnail((140, 140))
            cols[i % 3].image(img)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("Tap a Photo to Preview")

        prev_cols = st.columns(3)
        for i, f in enumerate(extras):
            if prev_cols[i % 3].button(f"Preview " + str(i+1)):
                st.image(Image.open(f), width=330)

    # -------------------------------------------------
    # Message + Expiry
    # -------------------------------------------------
    msg = st.text_area("Enter Your Message ❤️")
    expiry = st.selectbox(
        "Expiry Time",
        ["10 Minutes", "1 Hour", "1 Day", "7 Days"]
    )

    generate = st.button("Generate Memory Card ❤️", use_container_width=True)

    if generate:

        # Validate
        if not main:
            st.error("Upload main picture.")
            return
        if not extras or len(extras) != 5:
            st.error("Upload exactly 5 extra pictures.")
            return
        if not msg:
            st.error("Enter a message ❤️")
            return

        # Save main image
        tmp_main = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        Image.open(main).convert("RGB").save(tmp_main.name)

        # Encode message
        encoded_path = "encoded_memory.png"
        hide_text(tmp_main.name, msg, encoded_path)

        st.info("Uploading your pictures… 💞")

        # Upload main encoded image
        main_url = upload_to_imgbb(encoded_path)
        if not main_url:
            return

        # Upload extras
        extra_urls = []
        for f in extras:
            t = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            Image.open(f).convert("RGB").save(t.name)
            url = upload_to_imgbb(t.name)
            if not url:
                return
            extra_urls.append(url)

        # Expiry timestamp
        now = int(time.time())
        expiry_map = {
            "10 Minutes": 600,
            "1 Hour": 3600,
            "1 Day": 86400,
            "7 Days": 604800
        }
        exp_ts = now + expiry_map[expiry]

        encoded_msg = quote_plus(msg.strip())

        # Final viewer link
        base = st.secrets.get("APP_BASE_URL") if "APP_BASE_URL" in st.secrets else ""
        if base:
            view_url = (
                f"{base}?view=1&img={main_url}"
                f"&a1={extra_urls[0]}&a2={extra_urls[1]}&a3={extra_urls[2]}"
                f"&a4={extra_urls[3]}&a5={extra_urls[4]}"
                f"&msg={encoded_msg}&exp={exp_ts}"
            )
        else:
            view_url = (
                f"?view=1&img={main_url}"
                f"&a1={extra_urls[0]}&a2={extra_urls[1]}&a3={extra_urls[2]}"
                f"&a4={extra_urls[3]}&a5={extra_urls[4]}"
                f"&msg={encoded_msg}&exp={exp_ts}"
            )

        st.success("🎉 Memory Card Created Successfully!")

        # =========================================================
        #  SHARE ROW (NO JAVASCRIPT — 100% STREAMLIT SAFE)
        # =========================================================
        st.markdown("### 💕 Share Your Memory Card")

        col1, col2, col3 = st.columns(3)

        # View
        with col1:
            st.link_button("💌 View", view_url)

        # Copy link (Streamlit-safe)
        with col2:
            if st.button("📋 Copy Link"):
                st.session_state["copied_text"] = view_url
                st.success("Link copied! (Paste anywhere)")

        # WhatsApp
        with col3:
            wa = f"https://wa.me/?text=💖 Check this Memory Card: {view_url}"
            st.link_button("💬 WhatsApp", wa)

        col4, col5 = st.columns(2)

        # Instagram
        with col4:
            st.link_button("📸 Instagram", view_url)

        # SMS
        with col5:
            sms = f"sms:?body=Check this Memory Card ❤️ {view_url}"
            st.link_button("📱 SMS", sms)

    # Close love-card container
    st.markdown("</div>", unsafe_allow_html=True)
