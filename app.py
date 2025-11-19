import streamlit as st
from urllib.parse import unquote_plus
import time
import os

from pages import hide_link_page, couple_card, contact

# -----------------------------------------------------
# Streamlit configuration
# -----------------------------------------------------
st.set_page_config(
    page_title="StegoLink",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------
# Global Neon Theme
# -----------------------------------------------------
try:
    with open("static/neon.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass


# =====================================================================
#  PUBLIC VIEW MODE (MEMORY CARD VIEWER)
# =====================================================================
query = st.query_params        # NEW API (NO DEPRECATION)

if "view" in query:

    # -------------------------
    # Load viewer.css
    # -------------------------
    try:
        with open("static/viewer.css", "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.markdown(f"<div style='color:red'>CSS LOAD ERROR: {e}</div>", unsafe_allow_html=True)

    # -------------------------
    # Extract URL parameters
    # -------------------------
    main_img = query.get("img", "")
    extras = [
        query.get("a1", ""),
        query.get("a2", ""),
        query.get("a3", ""),
        query.get("a4", ""),
        query.get("a5", ""),
    ]
    extras = [x for x in extras if x]
    all_pics = [main_img] + extras

    message = query.get("msg", "")
    expiry_raw = query.get("exp", "0")

    # -------------------------
    # Expiry validation
    # -------------------------
    now = int(time.time())
    try:
        expiry_ts = int(expiry_raw)
    except:
        expiry_ts = now + 60

    if expiry_ts < now:
        st.error("This memory card link has expired.")
        st.stop()

    # -------------------------
    # Navigation index
    # -------------------------
    if "viewer_index" not in st.session_state:
        st.session_state.viewer_index = 0

    nav = query.get("nav", "")
    total = len(all_pics)

    if nav == "prev":
        st.session_state.viewer_index = (st.session_state.viewer_index - 1) % total
        st.query_params = {"view": "1"}

    elif nav == "next":
        st.session_state.viewer_index = (st.session_state.viewer_index + 1) % total
        st.query_params = {"view": "1"}

    current_pic = all_pics[st.session_state.viewer_index]

    # ==================================================================
    # Viewer Layout  (DO NOT SPLIT THE FIRST HTML BLOCK)
    # ==================================================================
    st.markdown(
        """
<div class='viewer-wrap'>
    <div class='viewer-heading'>💖 Your Memory Card 💖</div>
""",
        unsafe_allow_html=True
    )

    # -------------------------
    # Image + Arrows
    # -------------------------
    st.markdown(
        f"""
<div class="viewer-card">

    <div class="nav-arrow left-arrow"
         onclick="window.location.search='?view=1&nav=prev'">⬅</div>

    <div class="nav-arrow right-arrow"
         onclick="window.location.search='?view=1&nav=next'">➡</div>

    <img src="{current_pic}">
</div>
""",
        unsafe_allow_html=True
    )

    # -------------------------
    # Message box
    # -------------------------
    st.markdown(
        f"""
<div class="text-box">
    {message}
</div>
""",
        unsafe_allow_html=True
    )

    # -------------------------
    # Emoji shower
    # -------------------------
    st.markdown(
        """
<div class="emoji-bar">
    <span class="emoji-btn" onclick="makeShower('❤️')">❤️</span>
    <span class="emoji-btn" onclick="makeShower('😘')">😘</span>
    <span class="emoji-btn" onclick="makeShower('💕')">💕</span>
</div>

<script>
function makeShower(emoji) {
    for(let i=0; i<12; i++){
        let node = document.createElement("div");
        node.classList.add("falling-emoji");
        node.style.left = (Math.random()*80+10) + "%";
        node.innerHTML = emoji;
        document.body.appendChild(node);
        setTimeout(() => { node.remove(); }, 1400);
    }
}
</script>

</div>   <!-- closes viewer-wrap -->
""",
        unsafe_allow_html=True
    )

    st.stop()   # END VIEWER MODE


# =====================================================================
#  MAIN MENU (NORMAL MODE)
# =====================================================================

c1, c2, c3 = st.columns([1, 1, 1])

with c1:
    if st.button("Hide Link"):
        st.query_params = {"page": "hide"}

with c2:
    if st.button("Secret Love Card"):
        st.query_params = {"page": "couple"}

with c3:
    if st.button("Contact Us"):
        st.query_params = {"page": "contact"}

page = st.query_params.get("page", "hide")

# =====================================================================
#  ROUTER
# =====================================================================

if page == "hide":
    hide_link_page.render()

elif page == "couple":
    couple_card.render()

else:
    contact.render()
