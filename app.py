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


# --------------- Top horizontal menu (single-file routing) ---------------
# custom menu bar (centered)
st.markdown("""
<div style="display:flex; gap:18px; justify-content:center; align-items:center; margin-top:12px; margin-bottom:18px;">
  <button id="btn-hide" onclick="window.streamlitRun && window.streamlitRun('menu_hide')" class="menu-btn">Hide Link</button>
  <button id="btn-couple" onclick="window.streamlitRun && window.streamlitRun('menu_couple')" class="menu-btn">Secret Love Card</button>
  <button id="btn-contact" onclick="window.streamlitRun && window.streamlitRun('menu_contact')" class="menu-btn">Contact Us</button>
</div>
<script>
  // Add a small bridge so Streamlit knows button presses (fallback)
  window.streamlitRun = function(action) {
    const kernel = window.parent;
    // fallback: we can't directly call Streamlit from JS in all runtimes.
    // Buttons below (st.button) will be used instead.
    return true;
  }
</script>
""", unsafe_allow_html=True)

# Fallback actual buttons in columns so clicks work reliably in Streamlit
col1, col2, col3 = st.columns([1,1,1])
with col1:
    if st.button("Hide Link"):
        st.session_state.page = "hide"
with col2:
    if st.button("Secret Love Card"):
        st.session_state.page = "couple"
with col3:
    if st.button("Contact Us"):
        st.session_state.page = "contact"

if "page" not in st.session_state:
    st.session_state.page = "hide"

# Router render
if st.session_state.page == "hide":
    hide_link_page.render()
elif st.session_state.page == "couple":
    couple_card.render()
else:
    contact.render()
