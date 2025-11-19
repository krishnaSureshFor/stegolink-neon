import streamlit as st
from urllib.parse import unquote_plus
import time
import os

from pages import hide_link_page, couple_card, contact

st.set_page_config(
    page_title="StegoLink",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load global neon theme
try:
    with open("static/neon.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass


# ======================================================================
#  PUBLIC VIEW MODE (Memory Card Viewer)
# ======================================================================
query = st.experimental_get_query_params()
if "view" in query:

    # Load viewer CSS (critical!)
    try:
        with open("static/viewer.css", "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.write("Viewer CSS error:", e)

    # Read URL params
    main_img = query.get("img", [""])[0]
    extras = [
        query.get("a1", [""])[0],
        query.get("a2", [""])[0],
        query.get("a3", [""])[0],
        query.get("a4", [""])[0],
        query.get("a5", [""])[0],
    ]
    all_pics = [main_img] + [x for x in extras if x]

    raw_msg = query.get("msg", [""])[0]
    expiry_raw = query.get("exp", ["0"])[0]

    # Validate expiry
    now = int(time.time())
    try:
        expiry_ts = int(expiry_raw)
    except:
        expiry_ts = now + 60

    if expiry_ts < now:
        st.error("This memory card link has expired.")
        st.stop()

    # Decode message text
    message = unquote_plus(raw_msg)

    # Prepare index
    if "viewer_index" not in st.session_state:
        st.session_state.viewer_index = 0

    nav = query.get("nav", [""])[0]
    total = len(all_pics)

    if nav == "prev":
        st.session_state.viewer_index = (st.session_state.viewer_index - 1) % total
        st.experimental_set_query_params(view="1")

    elif nav == "next":
        st.session_state.viewer_index = (st.session_state.viewer_index + 1) % total
        st.experimental_set_query_params(view="1")

    current_pic = all_pics[st.session_state.viewer_index]

    # ================================================================
    #  FIXED MARKDOWN BLOCK — viewer-wrap + heading TOGETHER
    # ================================================================
    st.markdown(
        """
<div class='viewer-wrap'>
    <div class='viewer-heading'>💖 Your Memory Card 💖</div>
""",
        unsafe_allow_html=True
    )

    # ================================================================
    #  IMAGE + ARROWS SECTION
    # ================================================================
    st.markdown(
        f"""
<div class="viewer-card">

    <div class="nav-arrow left-arrow"
         onclick="window.location.search='view=1&nav=prev'">⬅</div>

    <div class="nav-arrow right-arrow"
         onclick="window.location.search='view=1&nav=next'">➡</div>

    <img src="{current_pic}">
</div>
""",
        unsafe_allow_html=True
    )

    # ================================================================
    #  MESSAGE SECTION
    # ================================================================
    st.markdown(
        f"""
<div class="text-box">
    {message}
</div>
""",
        unsafe_allow_html=True
    )

    # ================================================================
    #  EMOJI SHOWER SECTION
    # ================================================================
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
""",
        unsafe_allow_html=True
    )

    # Close viewer-wrap DIV
    st.markdown("</div>", unsafe_allow_html=True)

    st.stop()


# ======================================================================
#  NORMAL MODE (HOME MENU)
# ======================================================================
c1, c2, c3 = st.columns([1, 1, 1])

with c1:
    if st.button("Hide Link"):
        st.session_state.page = "hide"
        st.experimental_set_query_params(page="hide")

with c2:
    if st.button("Secret Love Card"):
        st.session_state.page = "couple"
        st.experimental_set_query_params(page="couple")

with c3:
    if st.button("Contact Us"):
        st.session_state.page = "contact"
        st.experimental_set_query_params(page="contact")

page = st.experimental_get_query_params().get("page", ["hide"])[0]

if page == "hide":
    hide_link_page.render()
elif page == "couple":
    couple_card.render()
else:
    contact.render()
