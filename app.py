# app.py
import streamlit as st
from urllib.parse import unquote_plus
import os

# router pages (local imports)
from pages import hide_link_page, couple_card, contact

st.set_page_config(page_title="StegoLink", layout="wide", initial_sidebar_state="collapsed")

# Load global neon css
try:
    with open("static/neon.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("static/neon.css not found — please add it to your repo.")

# --------------- Public view (Memory Card) via query params ---------------
# Query params: view=1 & img, a1..a5, msg, exp (expiry epoch seconds)
query = st.experimental_get_query_params()
if "view" in query:
    img = query.get("img", [""])[0]
    a1 = query.get("a1", [""])[0]
    a2 = query.get("a2", [""])[0]
    a3 = query.get("a3", [""])[0]
    a4 = query.get("a4", [""])[0]
    a5 = query.get("a5", [""])[0]
    raw_msg = query.get("msg", [""])[0]
    exp = query.get("exp", [""])[0]

    # load love.css for themed view
    try:
        with open("static/love.css", "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

    st.markdown("<h1 style='text-align:center; margin-top:18px;'>💖 Your Memory Card 💖</h1>", unsafe_allow_html=True)

    # expiry check
    try:
        exp_ts = int(exp)
    except Exception:
        exp_ts = None

    import time
    now = int(time.time())
    if exp_ts and exp_ts < now:
        st.error("This memory card link has expired.")
        st.stop()

    # Show main encoded image
    if img:
        st.image(img, use_column_width=True, caption="Your Encoded Memory Image 💕")
    else:
        st.warning("No main image provided in link.")

    # Show message (decoded) under image
    try:
        message = unquote_plus(raw_msg)
        st.markdown(f"<div style='margin-top:12px; padding:14px; border-radius:10px; background: rgba(255,255,255,0.06);'>{message}</div>", unsafe_allow_html=True)
    except Exception:
        st.write("")

    st.subheader("Your Extra Moments 💞")
    extra = [u for u in (a1, a2, a3, a4, a5) if u]
    if extra:
        st.image(extra, width=220, caption=[""] * len(extra))
    else:
        st.info("No extra images provided.")

    st.stop()  # stop further rendering (public view handled)


# ------------------ TOP MENU (Single Clean Version) ------------------

st.markdown("""
<div style="display:flex; gap:22px; justify-content:center; margin-top:18px; margin-bottom:25px;">
    <button onclick="window.location.href='/?page=hide'" class="menu-btn">Hide Link</button>
    <button onclick="window.location.href='/?page=couple'" class="menu-btn">Secret Love Card</button>
    <button onclick="window.location.href='/?page=contact'" class="menu-btn">Contact Us</button>
</div>
""", unsafe_allow_html=True)

# read page from query parameter
page = st.experimental_get_query_params().get("page", ["hide"])[0]
st.session_state.page = page
# Router render
if st.session_state.page == "hide":
    hide_link_page.render()
elif st.session_state.page == "couple":
    couple_card.render()
else:
    contact.render()
