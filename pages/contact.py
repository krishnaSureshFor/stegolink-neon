# pages/contact.py
import streamlit as st

def render():
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.header("📩 Contact Us")
    st.markdown("""
    **Need help or want to collaborate?**

    - **Email:** your-email@example.com  
    - **GitHub:** https://github.com/yourprofile  
    - **Twitter / Insta:** @yourhandle

    Leave a message:
    """, unsafe_allow_html=True)

    name = st.text_input("Name")
    email = st.text_input("Email")
    msg = st.text_area("Message")

    if st.button("Send Message"):
        if not name or not email or not msg:
            st.error("Please fill all fields.")
        else:
            st.success("Thanks — message (local demo) received! (This is a demo; wire to an email service to send.)")

    st.markdown("</div>", unsafe_allow_html=True)
