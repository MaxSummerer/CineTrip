import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

from src.scripts.movieLensUtils import search_in_ml_latest_by_name, load_links_data, search_in_ml_hundred_by_id, \
    create_X, give_me_data, give_me_n_cold_start_movies

movie_id_list = [x for x in give_me_n_cold_start_movies(15) if x not in [50, 181, 121]]

if 'show' not in st.session_state:
    st.session_state["show"] = -1


def resize_image(url, size=(500, 550)):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img.thumbnail(size)
    return img


def load_image(movieId):
    # print(movieId)
    movie_json = get_movie_info_by_movieID(movieId)
    # print(movie_json)
    if 'Poster' in movie_json and movie_json['Poster'] != 'N/A':
        img_url = movie_json['Poster']
        # print("hi ",img_url)
        img = resize_image(img_url)
        return img
    else:
        return None


def get_imdbID_by_movieId(movie_id):
    movie_details = search_in_ml_hundred_by_id(movie_id)
    # print(movie_details["title"].values[0])
    other_movie_details = search_in_ml_latest_by_name(movie_details["title"].values[0])
    # print(other_movie_details)
    if len(other_movie_details["movieId"].values) == 0:
        print("isssue with ", movie_details["title"].values[0])
        return None
    other_movie_id = other_movie_details["movieId"].values[0]
    # print(other_movie_id)
    links_data = load_links_data()
    other_movie_id = str(other_movie_id)
    imdbId = links_data[links_data['movieId'] == other_movie_id]['imdbId']
    # print(movie_id, "imdb le lo", imdbId.values[0])
    return imdbId.values[0]


def get_movie_info_by_movieID(movie_id, api_key="9dc353f6"):
    movie_imdbID = get_imdbID_by_movieId(movie_id)
    # print(type(movie_imdbID))
    url = f"http://www.omdbapi.com/?i=tt{movie_imdbID}&plot=full&apikey={api_key}"

    response = requests.get(url)
    # print(response)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error"}



colm1, colm2 = st.columns([1, 1])
with colm1:
    st.title("View your selections")
with colm2:
    if st.button("✨Show recommendations"):
        st.switch_page("pages/step4.py")

if 'likes' in st.session_state and 'dislikes' in st.session_state and 'didntWatch' in st.session_state:

    st.markdown(
        """
        <style>
        .stButton button {
            width: 170px;
            height: 90px;
        .centered {
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns([1, 1, 1, 1.5])

    index = 0
    with col1:
        st.markdown('<h2 class="centered">Likes</h2>', unsafe_allow_html=True)
        for id in st.session_state['likes']:
            movie_details = search_in_ml_hundred_by_id(id)
            movie_name = movie_details["title"].values[0]
            if st.button(movie_name, key=index):
                st.session_state["show"] = id
            index = index + 1

    with col2:
        st.markdown('<h2 class="centered">Dislikes</h2>', unsafe_allow_html=True)
        for id in st.session_state['dislikes']:
            movie_details = search_in_ml_hundred_by_id(id)
            movie_name = movie_details["title"].values[0]
            if st.button(movie_name, key=index):
                st.session_state["show"] = id
            index = index + 1
    with col3:
        st.markdown('<h2 class="centered">Didn\'t watch</h2>', unsafe_allow_html=True)
        for id in st.session_state['didntWatch']:
            movie_details = search_in_ml_hundred_by_id(id)
            movie_name = movie_details["title"].values[0]
            if st.button(movie_name, key=index):
                st.session_state["show"] = id
            index = index + 1

    with col4:
        with st.container(height=600, border=True):
            if st.session_state["show"] != -1 and load_image(st.session_state["show"]):
                st.image(load_image(st.session_state["show"]))
                movie_json = get_movie_info_by_movieID(st.session_state["show"])
                if movie_json:
                    html_content = f"""
                            <div style="max-width: 700px; max-height: 350px; overflow-x: hidden; overflow-y: auto; border: 1px solid #ccc; padding: 10px;">
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
