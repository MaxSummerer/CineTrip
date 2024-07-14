import streamlit as st
import base64
import requests
from PIL import Image
from io import BytesIO
import pandas as pd
import numpy as np

st.set_page_config(initial_sidebar_state="collapsed", layout="wide")

IMG_FOLDER_PATH = "src/data/img/"


def resize_image(url, size=(500, 550)):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img.thumbnail(size)
    return img


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()


icon_image_path = IMG_FOLDER_PATH + "cine_logo.png"
col11, col12, col13 = st.columns([4, 5, 1])

with col11:
    st.title("Welcome to CineTrip!")

with col13:
    st.image(icon_image_path, width=100)

col21, col22, col23 = st.columns([1, 1, 1])
with col21:
    with st.container(height=320, border=True):
        st.markdown("""
        **What is CineTrip?**

        Discover a whole new way to plan your travels with CineTrip, the innovative web-app that curates personalized tour trips based on your location and favorite movies. Whether you're a film buff dreaming of visiting iconic movie locations or an adventurer looking to explore destinations inspired by your beloved films, CineTrip has got you covered.
        """)
with col22:
    with st.container(height=320, border=True):
        st.markdown("""
        **How to use?**
        
        Simply input your location and select movies you love, and let CineTrip craft a unique travel itinerary that brings your cinematic fantasies to life. From the bustling streets of New York featured in countless classics to the enchanting landscapes of Middle-earth, CineTrip turns your movie dreams into unforgettable travel experiences.
        
        **Step 1: Choose Your Location**
        
        You can either select any place in the world or use our auto-localization feature to find your current position. This flexibility ensures that CineTrip can cater to both your dream destinations and your immediate surroundings.

        **Step 2: Rate Your Movies**
        
        Browse through a curated list of movies and rate them with "like," "didn't watch," or "unlike." Your preferences help us understand your tastes and interests.

        **Step 3: Get Your Personalized Tour**
        
        Based on your movie choices and location, CineTrip will recommend an amazing movie location tour.
        """)
with col23:
    with st.container(height=320, border=True):
        st.markdown("""
        **About Team 7 CineTrip**
        
        Team members:
        
        Maanav Khungar
        
        Maximilian Summerer
        
        Lan Wang
        
        """)

if st.button("✨Let's start!"):
    st.switch_page("pages/step1.py")

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(
        np.random.randn(12, 5), columns=["a", "b", "c", "d", "e"]
    )


