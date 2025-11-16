import streamlit as st
from urllib.parse import unquote_plus
import time

st.set_page_config(
    page_title="StegoLink",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from pages import hide_link_page, couple_card, contact

# Load neon CSS
try:
    with open("static/neon.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass


# --------------------- PUBLIC VIEW PAGE ---------------------
query = st.experimental_get_query_params()
if "view" in query:
    try:
        with open("static/love.css") as f:
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

    # expiration check
    now = int(time.time())
    try:
        exp_ts = int(exp)
    except:
        exp_ts = now + 10

    if exp_ts < now:
        st.error("This link has expired.")
        st.stop()

    st.image(img, use_column_width=True)

    message = unquote_plus(raw_msg)
    st.markdown(
        f"<div style='padding:15px;border-radius:12px;background:rgba(255,255,255,0.25)'>{message}</div>",
        unsafe_allow_html=True,
    )

    extra = [a for a in [a1, a2, a3, a4, a5] if a]
    st.subheader("Extra Moments 💞")
    st.image(extra, width=220)

    st.stop()



# -------------- WORKING TOP MENU (STREAMLIT BUTTONS) --------------
col1, col2, col3 = st.columns([1,1,1])

with col1:
    if st.button("Hide Link"):
        st.session_state.page = "hide"
        st.experimental_set_query_params(page="hide")

with col2:
    if st.button("Secret Love Card"):
        st.session_state.page = "couple"
        st.experimental_set_query_params(page="couple")

with col3:
    if st.button("Contact Us"):
        st.session_state.page = "contact"
        st.experimental_set_query_params(page="contact")


# determine page
page = st.experimental_get_query_params().get("page", ["hide"])[0]
st.session_state.page = page



# ------------------------- PAGE ROUTER -------------------------
if page == "hide":
    hide_link_page.render()

elif page == "couple":
    couple_card.render()

else:
    contact.render()
