# ------------------------------ app.py ------------------------------
import streamlit as st
from urllib.parse import unquote_plus
import time
import os

# Import page modules
from pages import hide_link_page, couple_card, contact

st.set_page_config(
    page_title="StegoLink",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load global neon glass theme
try:
    with open("static/neon.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass


# ---------------------------------------------------------
#        PUBLIC VIEW (Memory Card opened via link)
# ---------------------------------------------------------
query = st.experimental_get_query_params()
if "view" in query:
    try:
        with open("static/love.css", "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        pass

    img = query.get("img", [""])[0]
    a1 = query.get("a1", [""])[0]
    a2 = query.get("a2", [""])[0]
    a3 = query.get("a3", [""])[0]
    a4 = query.get("a4", [""])[0]
    a5 = query.get("a5", [""])[0]
    raw_msg = query.get("msg", [""])[0]
    exp = query.get("exp", ["0"])[0]

    st.markdown("<h1 class='love-title'>💖 Your Memory Card 💖</h1>", unsafe_allow_html=True)

    # --------- Expiration check ---------
    now = int(time.time())
    try:
        exp_ts = int(exp)
    except:
        exp_ts = now + 10

    if exp_ts < now:
        st.error("This memory card link has expired.")
        st.stop()

    # --------- Render content ---------
    if img:
        st.image(img, use_column_width=True)
    else:
        st.warning("Main image missing.")

    try:
        msg = unquote_plus(raw_msg)
        st.markdown(f"""
        <div style='background:rgba(255,255,255,0.20);
                    padding:18px;border-radius:12px;
                    margin-top:12px;font-size:1.2rem;'>
            {msg}
        </div>
        """, unsafe_allow_html=True)
    except:
        pass

    st.subheader("Extra Moments 💞")
    extra_urls = [u for u in [a1, a2, a3, a4, a5] if u]

    if extra_urls:
        st.image(extra_urls, width=230)
    else:
        st.info("No extra images found.")

    st.stop()


# ---------------------------------------------------------
#          TOP MENU (Single Clean Version)
# ---------------------------------------------------------
st.markdown("""
<div style="display:flex; gap:22px; justify-content:center; margin-top:22px; margin-bottom:30px;">
    <button onclick="window.location.href='/?page=hide'" class="menu-btn">Hide Link</button>
    <button onclick="window.location.href='/?page=couple'" class="menu-btn">Secret Love Card</button>
    <button onclick="window.location.href='/?page=contact'" class="menu-btn">Contact Us</button>
</div>
""", unsafe_allow_html=True)

# Read active page from URL
page = st.experimental_get_query_params().get("page", ["hide"])[0]
st.session_state.page = page


# ---------------------------------------------------------
#                       ROUTER
# ---------------------------------------------------------
if page == "hide":
    hide_link_page.render()
elif page == "couple":
    couple_card.render()
else:
    contact.render()