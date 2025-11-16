# ----------------- couple_card.py -----------------
import streamlit as st
from PIL import Image
import tempfile, base64, requests, os, time
from stego.simple_lsb import hide_text
from urllib.parse import quote_plus


IMGBB_API_KEY = os.environ.get("IMGBB_API_KEY", "")


def upload_to_imgbb(path):
    if not IMGBB_API_KEY:
        st.error("⚠️ ImgBB key not found in environment variable IMGBB_API_KEY")
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
            st.error("ImgBB upload error:")
            st.code(res)
            return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None



def render():

    # Load theme
    try:
        with open("static/love.css", "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        pass

    st.markdown("<h1 class='love-title'>💖 Create Your Memory Card</h1>", unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    # -------------------------------------
    #         Upload main picture
    # -------------------------------------
    main = st.file_uploader("Upload Main Picture", type=["png", "jpg", "jpeg"])

    if main:
        st.image(main, caption="Main Picture", width=250)

    # -------------------------------------
    #         Upload extra 5 pictures
    # -------------------------------------
    extras = st.file_uploader(
        "Upload 5 Extra Pictures",
        accept_multiple_files=True,
        type=["png", "jpg", "jpeg"]
    )

    # ------------------------------------------------
    #     THUMBNAIL PREVIEW OF EXTRA IMAGES (new)
    # ------------------------------------------------
    if extras:
        st.markdown("""
        <div style='font-size:1.1rem; font-weight:600; margin-top:10px;'>
            Extra Photos Preview
        </div>
        """, unsafe_allow_html=True)

        thumb_cols = st.columns(3)

        # Show thumbnails in 3xN responsive grid
        for i, img_file in enumerate(extras):
            col = thumb_cols[i % 3]
            with col:
                try:
                    img = Image.open(img_file)
                    img.thumbnail((120, 120))
                    st.image(img, use_column_width=False)
                except:
                    pass

        # Big preview if clicked
        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("Tap a Photo to Preview")

        click_cols = st.columns(3)
        for i, img_file in enumerate(extras):
            col = click_cols[i % 3]
            if col.button(f"Preview {i+1}"):
                try:
                    st.image(Image.open(img_file), caption=f"Photo {i+1}", width=330)
                except:
                    st.warning("Could not open preview.")



    # -------------------------------------
    #         Message + Expiry
    # -------------------------------------
    msg = st.text_area("Enter Your Message ❤️")
    expiry = st.selectbox("Expiry Time", ["10 Minutes", "1 Hour", "1 Day", "7 Days"])

    generate = st.button("Generate Memory Card ❤️", use_container_width=True)

    if generate:
        # Validate inputs
        if not main:
            st.error("Upload main picture.")
            return
        if not extras or len(extras) != 5:
            st.error("Upload exactly 5 extra images.")
            return
        if not msg:
            st.error("Enter a message.")
            return

        # Save main image and encode message
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        Image.open(main).convert("RGB").save(tmp.name)

        encoded_path = "encoded_memory.png"

        try:
            hide_text(tmp.name, msg, encoded_path)
        except Exception as e:
            st.error(f"Encoding failed: {e}")
            return

        st.info("Uploading Your Beautiful Pictures... 💞")

        # Upload main image to ImgBB
        main_url = upload_to_imgbb(encoded_path)
        if not main_url:
            return

        # Upload extras
        extra_urls = []
        for e in extras:
            t = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            Image.open(e).convert("RGB").save(t.name)
            url = upload_to_imgbb(t.name)
            if not url:
                return
            extra_urls.append(url)

        # Compute expiry timestamp
        now = int(time.time())
        expiry_map = {
            "10 Minutes": 600,
            "1 Hour": 3600,
            "1 Day": 86400,
            "7 Days": 604800
        }
        expire_ts = now + expiry_map.get(expiry, 3600)

        # Encode message
        encoded_msg = quote_plus(msg.strip())

        # Create public link
        base = st.secrets.get("APP_BASE_URL") if "APP_BASE_URL" in st.secrets else ""
        if base:
            view_url = (
                f"{base}?view=1&img={main_url}"
                f"&a1={extra_urls[0]}&a2={extra_urls[1]}&a3={extra_urls[2]}"
                f"&a4={extra_urls[3]}&a5={extra_urls[4]}"
                f"&msg={encoded_msg}&exp={expire_ts}"
            )
        else:
            view_url = (
                f"?view=1&img={main_url}"
                f"&a1={extra_urls[0]}&a2={extra_urls[1]}&a3={extra_urls[2]}"
                f"&a4={extra_urls[3]}&a5={extra_urls[4]}"
                f"&msg={encoded_msg}&exp={expire_ts}"
            )

        st.success("🎉 Memory Card Created Successfully!")

        # View button
        st.markdown(
            f"<a href='{view_url}' target='_blank' class='love-button'>💌 View Memory Card</a>",
            unsafe_allow_html=True
        )

        # -----------------------------------------
        #           Share Buttons
        # -----------------------------------------
        wa = f"https://wa.me/?text=💖 Check this Memory Card: {view_url}"
        insta = view_url
        sms = f"sms:?body=Check this Memory Card ❤️ {view_url}"

        st.markdown(f"""
        <div style="display:flex; gap:12px; margin-top:14px;">
            <a href="{wa}" target="_blank"><button class="love-button">💬 WhatsApp</button></a>
            <a href="{insta}" target="_blank"><button class="love-button">📸 Instagram</button></a>
            <a href="{sms}" target="_blank"><button class="love-button">📱 Messages</button></a>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
