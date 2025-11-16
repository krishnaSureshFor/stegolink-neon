# ----------------- couple_card.py -----------------
import streamlit as st
from PIL import Image
import tempfile, base64, requests, os, time
from stego.simple_lsb import hide_text
from urllib.parse import quote_plus


IMGBB_API_KEY = os.environ.get("IMGBB_API_KEY", "")


def upload_to_imgbb(path):
    if not IMGBB_API_KEY:
        st.error("⚠️ ImgBB API key missing. Add IMGBB_API_KEY in Streamlit Secrets.")
        return None

    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    url = "https://api.imgbb.com/1/upload"
    payload = {"key": IMGBB_API_KEY, "image": encoded}

    try:
        res = requests.post(url, data=payload, timeout=25).json()
        if res.get("success"):
            return res["data"]["url"]
        else:
            st.error("ImgBB upload failed:")
            st.code(res)
            return None
    except Exception as e:
        st.error(f"Upload error: {e}")
        return None



def render():

    # Load love theme
    try:
        with open("static/love.css", "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        pass

    st.markdown("<h1 class='love-title'>💖 Create Your Memory Card</h1>", unsafe_allow_html=True)

    st.markdown("<div class='love-card'>", unsafe_allow_html=True)

    # -------------------------------------------------
    # Main picture
    # -------------------------------------------------
    main = st.file_uploader("Upload Main Picture", type=["png", "jpg", "jpeg"])

    if main:
        st.image(main, caption="Main Picture", width=260)

    # -------------------------------------------------
    # Extra pictures
    # -------------------------------------------------
    extras = st.file_uploader(
        "Upload 5 Extra Pictures",
        accept_multiple_files=True,
        type=["png", "jpg", "jpeg"]
    )

    # ---------------------- THUMBNAILS ----------------------
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

        preview_cols = st.columns(3)
        for i, f in enumerate(extras):
            if preview_cols[i % 3].button(f"Preview {i+1}"):
                st.image(Image.open(f), width=330)

    # -------------------------------------------------
    # Message + expiry
    # -------------------------------------------------
    msg = st.text_area("Enter Your Message ❤️")
    expiry = st.selectbox("Expiry Time", ["10 Minutes", "1 Hour", "1 Day", "7 Days"])

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

        # Save main
        tmp_main = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        Image.open(main).convert("RGB").save(tmp_main.name)

        # Encode text
        encoded_path = "encoded_memory.png"
        try:
            hide_text(tmp_main.name, msg, encoded_path)
        except Exception as e:
            st.error(f"Encoding failed: {e}")
            return

        st.info("Uploading your pictures… 💞")

        # Upload main
        main_url = upload_to_imgbb(encoded_path)
        if not main_url:
            return

        # Upload extras
        extra_urls = []
        for f in extras:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            Image.open(f).convert("RGB").save(tmp.name)
            url = upload_to_imgbb(tmp.name)
            if not url:
                return
            extra_urls.append(url)

        # Expiry
        now = int(time.time())
        expiry_map = {
            "10 Minutes": 600,
            "1 Hour": 3600,
            "1 Day": 86400,
            "7 Days": 604800
        }
        exp_ts = now + expiry_map.get(expiry, 600)

        # Encode message
        encoded_msg = quote_plus(msg.strip())

        # Final link
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

        # ----------------------------
        # SUCCESS UI
        # ----------------------------
        st.success("🎉 Memory Card Created Successfully!")

        # ----------------------------
        # VIEW & SHARE ROW
        # ----------------------------
        st.markdown(f"""
        <style>
        .share-btn {{
            background: linear-gradient(90deg,#ff0066,#ff4f9f);
            padding: 12px 20px;
            border-radius: 12px;
            border: none;
            color: #fff !important;
            font-weight: 700;
            cursor: pointer;
            font-size: 15px;
            text-decoration: none !important;
            display:inline-block;
            box-shadow: 0 8px 25px rgba(255,0,120,0.35);
        }}
        </style>

        <div style="
            display:flex;
            flex-wrap:wrap;
            gap:10px;
            justify-content:center;
            margin-top:20px;
        ">

            <a href="{view_url}" target="_blank" class="share-btn">
                💌 View Memory Card
            </a>

            <button class="share-btn" onclick="copyToClipboard()">
                📋 Copy Link
            </button>

            <a href="https://wa.me/?text=💖 Check this Memory Card: {view_url}"
               target="_blank" class="share-btn">
                💬 WhatsApp
            </a>

            <a href="{view_url}" target="_blank" class="share-btn">
                📸 Instagram
            </a>

            <a href="sms:?body=Check this Memory Card ❤️ {view_url}"
               target="_blank" class="share-btn">
                📱 Messages
            </a>

        </div>

        <script>
        function copyToClipboard() {{
            navigator.clipboard.writeText("{view_url}");
            alert("✔ Link copied to clipboard!");
        }}
        </script>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
