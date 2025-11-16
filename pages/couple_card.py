import streamlit as st
from PIL import Image
import requests, base64, tempfile
from stego.simple_lsb import hide_text
import os

IMGBB_API_KEY = "YOUR_IMGBB_API_KEY"   # <---- IMPORTANT: ADD YOUR API KEY

# Load Private CSS
with open("static/love.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("<h1 class='love-title'>💖 Couple Memory Card Maker 💖</h1>", unsafe_allow_html=True)

# Inputs
main_image = st.file_uploader("Upload Main Picture", type=["png", "jpg", "jpeg"])
extra_images = st.file_uploader("Upload 5 Extra Pictures", accept_multiple_files=True, type=["png","jpg","jpeg"])
user_text = st.text_area("Enter your Love Message ❤️")
duration = st.selectbox("Link Expiration Duration", ["10 Minutes", "1 Hour", "1 Day", "7 Days"])

if st.button("Generate Love Card ❤️"):
    if not main_image or len(extra_images) != 5 or not user_text:
        st.error("Please upload ALL required images and message.")
    else:
        # Save and encode main image
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        Image.open(main_image).convert("RGB").save(tmp.name)

        encoded_path = "encoded_love.png"
        hide_text(tmp.name, user_text, encoded_path)

        # Upload all images to imgbb
        def upload_to_imgbb(path):
            with open(path, "rb") as f:
                encoded = base64.b64encode(f.read())
            url = "https://api.imgbb.com/1/upload"
            payload = {"key": IMGBB_API_KEY, "image": encoded}
            res = requests.post(url, payload)
            return res.json()["data"]["url"]

        card_image_url = upload_to_imgbb(encoded_path)

        extra_urls = []
        for img in extra_images:
            t = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            Image.open(img).convert("RGB").save(t.name)
            extra_urls.append(upload_to_imgbb(t.name))

        # Generate view link
        view_url = f"https://your-streamlit-app-url/?view=1&img={card_image_url}&a1={extra_urls[0]}&a2={extra_urls[1]}&a3={extra_urls[2]}&a4={extra_urls[3]}&a5={extra_urls[4]}&msg={user_text}&exp={duration}"

        st.success("Your Love Card is Ready! 💕")
        st.markdown(f"<a class='love-button' href='{view_url}' target='_blank'>💌 View Memory Card</a>", unsafe_allow_html=True)
