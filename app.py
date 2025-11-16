# ------------------------------ app.py ------------------------------
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

# Load neon theme
try:
    with open("static/neon.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass


# ---------------------------------------------------------
# PUBLIC VIEW MODE (Memory Card Viewer)
# ---------------------------------------------------------
query = st.experimental_get_query_params()
if "view" in query:

    # Load couple-theme CSS
    try:
        with open("static/love.css", "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        pass

    # Read parameters
    img = query.get("img", [""])[0]
    extras = [
        query.get("a1", [""])[0],
        query.get("a2", [""])[0],
        query.get("a3", [""])[0],
        query.get("a4", [""])[0],
        query.get("a5", [""])[0],
    ]
    all_pics = [img] + [x for x in extras if x]

    raw_msg = query.get("msg", [""])[0]
    exp = query.get("exp", ["0"])[0]

    # Check link expiration
    now = int(time.time())
    try:
        exp_ts = int(exp)
    except:
        exp_ts = now + 60

    if exp_ts < now:
        st.error("This memory card link has expired.")
        st.stop()

    # Decode message
    message = unquote_plus(raw_msg)

    # --------------------------------------------------------
    # MOBILE-FRIENDLY VIEWER CSS
    # --------------------------------------------------------
    st.markdown("""
    <style>

    .viewer-wrap {
        width: 100%;
        max-width: 380px;
        margin: auto;
        text-align: center;
        padding-top: 12px;
    }

    .viewer-heading {
        width: 88%;
        margin: auto;
        background: rgba(255,255,255,0.25);
        padding: 14px;
        border-radius: 50px;
        font-size: 1.35rem;
        font-weight: 700;
        box-shadow: 0 8px 20px rgba(0,0,0,0.18);
    }

    .viewer-card {
        margin-top: 16px;
        width: 100%;
        height: 420px;
        max-width: 360px;
        background: rgba(255,255,255,0.25);
        border-radius: 28px;
        overflow: hidden;
        position: relative;
        box-shadow: 0 10px 35px rgba(0,0,0,0.25);
    }

    .viewer-card img {
        width: 100%;
        height: 420px;
        object-fit: cover;
    }

    .text-box {
        margin-top: 14px;
        background: rgba(255,255,255,0.22);
        padding: 14px;
        border-radius: 14px;
        font-size: 1.1rem;
        font-weight: 600;
        line-height: 1.4;
    }

    .nav-arrow {
        width: 50px;
        height: 50px;
        background: rgba(255,255,255,0.65);
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 26px;
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        box-shadow: 0 5px 18px rgba(0,0,0,0.25);
        cursor: pointer;
    }

    .left-arrow { left: -26px; }
    .right-arrow { right: -26px; }

    .emoji-bar {
        display: flex;
        justify-content: center;
        gap: 22px;
        margin-top: 20px;
    }

    .emoji-btn {
        font-size: 34px;
        cursor: pointer;
        transition: 0.15s;
    }

    .emoji-btn:active {
        transform: scale(1.25);
    }

    @keyframes fall {
        0% { transform: translateY(-20px); opacity: 1; }
        100% { transform: translateY(500px); opacity: 0; }
    }

    .falling-emoji {
        position: fixed;
        top: -10px;
        left: 50%;
        font-size: 32px;
        animation: fall 1.4s linear forwards;
        z-index: 9999;
    }

    @media (max-width: 480px) {
        .viewer-card { height: 360px; }
        .viewer-card img { height: 360px; }
    }

    </style>
    """, unsafe_allow_html=True)


    # --------------------------------------------------------
    # PAGE STRUCTURE
    # --------------------------------------------------------
    st.markdown("<div class='viewer-wrap'>", unsafe_allow_html=True)

    # Heading
    st.markdown("<div class='viewer-heading'>💖 Your Memory Card 💖</div>", unsafe_allow_html=True)

    # INITIAL INDEX
    if "viewer_index" not in st.session_state:
        st.session_state.viewer_index = 0

    total = len(all_pics)

    # ARROWS (Python buttons)
    lw, _, rw = st.columns([1,6,1])

    with lw:
        if st.button("⬅"):
            st.session_state.viewer_index = (st.session_state.viewer_index - 1) % total

    with rw:
        if st.button("➡"):
            st.session_state.viewer_index = (st.session_state.viewer_index + 1) % total

    current_pic = all_pics[st.session_state.viewer_index]

    # MAIN IMAGE CARD
    st.markdown(f"""
        <div class='viewer-card'>
            <img src="{current_pic}">
        </div>
    """, unsafe_allow_html=True)

    # MESSAGE BELOW PICTURE (YOUR REQUEST)
    st.markdown(f"""
        <div class='text-box'>
            {message}
        </div>
    """, unsafe_allow_html=True)

    # EMOJI SHOWER
    st.markdown("""
    <div class='emoji-bar'>
        <span class='emoji-btn' onclick="makeShower('❤️')">❤️</span>
        <span class='emoji-btn' onclick="makeShower('😘')">😘</span>
        <span class='emoji-btn' onclick="makeShower('💕')">💕</span>
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
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.stop()


# ---------------------------------------------------------
# TOP NAVIGATION MENU
# ---------------------------------------------------------
c1, c2, c3 = st.columns([1,1,1])

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


# ---------------------------------------------------------
# ROUTER
# ---------------------------------------------------------
if page == "hide":
    hide_link_page.render()
elif page == "couple":
    couple_card.render()
else:
    contact.render()
