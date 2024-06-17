import os
import requests
from PIL import Image
from io import BytesIO
import streamlit as st

# given a movie name list and their information will be shown in this page
movie_name_list = [
    "Inception",
    "Harry Potter",
    "Tenet",
    "Iron Man",
    "The King's Speech"
]

# resize the image
def resize_image(url, size=(500, 550)):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img.thumbnail(size)
    return img

# like and unlike counting
if 'idx' not in st.session_state:
    st.session_state.idx = 0

def load_image(index):
    movie_json = get_movie_info(movie_name_list[index])
    img_url = movie_json['Poster']
    img = resize_image(img_url)
    return img


def next_image():
    st.session_state.idx += 1


def get_movie_info(movie_name, api_key="9dc353f6"):
    url = f"http://www.omdbapi.com/?t={movie_name}&plot=full&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error"}


st.title("Step2: choose the movie")
left_column, right_column = st.columns([1, 2])
with left_column:
    # Display the current movie poster
    current_image = load_image(st.session_state.idx)
    st.image(current_image)
    col1, col2, col3 = st.columns([1.5, 1, 1.5])

    with col1:
        if st.button("Unlike"):
            st.session_state.idx += 1
            if st.session_state.idx >= len(movie_name_list):
                st.session_state.idx = 0
                st.switch_page("pages/step3.py")
            st.rerun()

    with col3:
        if st.button("like"):
            st.session_state.idx += 1
            if st.session_state.idx >= len(movie_name_list):
                st.session_state.idx = 0
                st.switch_page("pages/step3.py")
            st.rerun()

# movie info
with right_column:
    movie_json = get_movie_info(movie_name_list[st.session_state.idx])
    if movie_json:

        html_content = f"""
        <div style="max-width: 600px; max-height: 350px; overflow-x: hidden; overflow-y: auto; border: 1px solid #ccc; padding: 10px;">
        <h2>{movie_json['Title']}</h2>
        <p style="margin-bottom: 10px;"><strong>Rating: {movie_json['imdbRating']}   |   Year: {movie_json['Year']}   |   Region: {movie_json['Country']}</strong></p>
        
        <p>{movie_json['Plot']}</p>
        
        <ul>
            <li><strong>Genre:</strong> {movie_json['Genre']}</li>
            <li><strong>Director:</strong> {movie_json['Director']}</li>
            <li><strong>Actors:</strong> {movie_json['Actors']}</li>
        </ul>
        """

    st.markdown(html_content, unsafe_allow_html=True)

