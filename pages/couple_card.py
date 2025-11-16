# ----------------- couple_card.py -----------------
import streamlit as st
from PIL import Image
import tempfile, base64, requests, os, time
from stego.simple_lsb import hide_text
from urllib.parse import quote_plus


IMGBB_API_KEY = os.environ.get("IMGBB_API_KEY", "")


def upload_to_imgbb(path):
    if not IMGBB_API_KEY:
        st.error("⚠️ ImgBB key not found. Add IMGBB_API_KEY in secrets/settings.")
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

    # Load pink theme
    try:
        with open("static/love.css", "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        pass

    st.markdown("<h1 class='love-title'>💖 Create Your Memory Card</h1>", unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    # -------------------------------------------------
    # Upload main picture
    # -------------------------------------------------
    main = st.file_uploader("Upload Main Picture", type=["png", "jpg", "jpeg"])

    if main:
        st.image(main, caption="Main Picture", width=260)

    # -------------------------------------------------
    # Upload extra pictures
    # -------------------------------------------------
    extras = st.file_uploader(
        "Upload 5 Extra Pictures",
        accept_multiple_files=True,
        type=["png", "jpg", "jpeg"]
    )

    # --------------------------------------------------------
    #     Show thumbnails preview (3×2 grid)
    # --------------------------------------------------------
    if extras:
        st.markdown("""
            <div style='font-size:1.1rem; font-weight:600; margin-top:10px;'>
                Extra Photos Preview
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
            if prev_cols[i % 3].button(f"Preview {i+1}"):
                st.image(Image.open(f), width=330)


    # --------------------------------------------------------
    # Message + Expiry Duration
    # --------------------------------------------------------
    msg = st.text_area("Enter Your Message ❤️")
    expiry = st.selectbox("Expiry Time", ["10 Minutes", "1 Hour", "1 Day", "7 Days"])

    # --------------------------------------------------------
    # Generate Memory Card
    # --------------------------------------------------------
    generate = st.button("Generate Memory Card ❤️", use_container_width=True)

    if generate:

        # Validate inputs
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

        # Encode message into main picture
        encoded_path = "encoded_memory.png"
        try:
            hide_text(tmp_main.name, msg, encoded_path)
        except Exception as e:
            st.error(f"Encoding failed: {e}")
            return

        st.info("Uploading your pictures… this may take a few seconds 💞")

        # Upload main encoded picture
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

        # Expiry timestamp
        now = int(time.time())
        expiry_map = {
            "10 Minutes": 600,
            "1 Hour": 3600,
            "1 Day": 86400,
            "7 Days": 604800
        }
        exp_ts = now + expiry_map.get(expiry, 3600)

        # Encode message
        encoded_msg = quote_plus(msg.strip())

        # Public viewer link
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

        # --------------------------------------------------------
        #          VIEW + SHARE + COPY (ALL IN SAME ROW)
        # --------------------------------------------------------
        st.markdown(f"""
        <div style="
            display:flex;
            flex-wrap:wrap;
            gap:10px;
            justify-content:center;
            margin-top:20px;
        ">
            <!-- VIEW BUTTON -->
            <a href="{view_url}" target="_blank">
                <button class="love-button">💌 View Memory Card</button>
            </a>

            <!-- COPY BUTTON -->
            <button class="love-button" onclick="copyToClipboard()">📋 Copy Link</button>

            <!-- WHATSAPP -->
            <a href="https://wa.me/?text=💖 Check this Memory Card: {view_url}" target="_blank">
                <button class="love-button">💬 WhatsApp</button>
            </a>

            <!-- INSTAGRAM -->
            <a href="{view_url}" target="_blank">
                <button class="love-button">📸 Instagram</button>
            </a>

            <!-- SMS -->
            <a href="sms:?body=Check this Memory Card ❤️ {view_url}" target="_blank">
                <button class="love-button">📱 Messages</button>
            </a>
        </div>

        <script>
        function copyToClipboard() {
            navigator.clipboard.writeText("{view_url}");
            alert("✔ Link copied to clipboard!");
        }
        </script>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
