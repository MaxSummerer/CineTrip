import streamlit as st
import base64
import requests
from PIL import Image
from io import BytesIO

IMG_FOLDER_PATH = "src/data/img/"

def resize_image(url, size=(500, 550)):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img.thumbnail(size)
    return img

def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
# homepage
icon_image_path = IMG_FOLDER_PATH+"cine_logo.png"
# st.image(icon_image_path)
st.title("Welcome to CineTrip!")
if st.button("Let's start"):
    st.switch_page("pages/step1.py")


