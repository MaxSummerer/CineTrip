import os
import requests
from PIL import Image
from io import BytesIO
import streamlit as st
import pandas as pd
import time

from recommender import MovieRecommender

from movieLensUtils import search_in_ml_latest_by_name, load_links_data, search_in_ml_hundred_by_id, create_X, give_me_data, give_me_n_cold_start_movies


# given a movie name list and their information will be shown in this page
movie_name_list = [
    "Inception",
    "Harry Potter",
    "Tenet",
    "Iron Man",
    "The King's Speech"
]

movie_id_list = [x for x in give_me_n_cold_start_movies(5) if x not in [50, 181, 121] ]
# these 3 movies are not in ml-latest dataset, so have removed from cold start list, should fix 
# movies are Star wars, return of the jedi, independence day

# resize the image
def resize_image(url, size=(500, 550)):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img.thumbnail(size)
    return img

# like and unlike counting
if 'idx' not in st.session_state:
    st.session_state.idx = 0

if 'likes' not in st.session_state:
    st.session_state['likes'] = []

if 'recs' not in st.session_state:
    st.session_state['recs'] = None

if 'recs_names' not in st.session_state:
    st.session_state['recs_names'] = None

if 'mr_object' not in st.session_state:
    st.session_state['mr_object'] = None


def load_image(index):
    movie_json = get_movie_info_by_movieID(movie_id_list[index])
    img_url = movie_json['Poster']
    img = resize_image(img_url)
    return img


def next_image():
    st.session_state.idx += 1

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

def get_movie_info(movie_name, api_key="9dc353f6"):
    url = f"http://www.omdbapi.com/?t={movie_name}&plot=full&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error"}

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

def calculate_recommendations():
    data, movie_titles = give_me_data()
    df = data.iloc[:, :3]
    df = df.rename(columns={df.columns[1]: 'movie_id'})
    X, user_mapper, movie_mapper, user_inv_mapper, movie_inv_mapper = create_X(df)    
    mr = MovieRecommender(X, movie_titles ,movie_mapper, movie_inv_mapper) # TODO: from here!!
    st.session_state['mr_object'] = mr
    # print(type(X), type(user_mapper), type(user_inv_mapper), type(movie_mapper), type(movie_inv_mapper))
    recommended_movie_ids, recommended_movies_names = mr.find_similar_movies(st.session_state['likes'],movie_titles, X, movie_mapper, movie_inv_mapper, 10)
    print(recommended_movies_names)
    html_content = f"""
    <div style="max-width: 600px; max-height: 350px; overflow-x: hidden; overflow-y: auto; border: 1px solid #ccc; padding: 10px;">
    {recommended_movies_names}
    """
    st.session_state['recs'] = recommended_movie_ids
    st.session_state['recs_names'] = recommended_movies_names
    # st.markdown(html_content, unsafe_allow_html=True)
    # time.sleep(30)



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
            # like_list.append(0)
            if st.session_state.idx >= len(movie_id_list):
                st.session_state.idx = 0
                calculate_recommendations()
                st.switch_page("pages/step3.py")
            st.rerun()

    with col3:
        if st.button("like"):
            st.session_state.idx += 1
            # like_list.append(1)
            st.session_state['likes'].append(movie_id_list[st.session_state.idx-1])
            if st.session_state.idx >= len(movie_id_list):
                st.session_state.idx = 0
                calculate_recommendations()
                st.switch_page("pages/step3.py")
            st.rerun()

# movie info
with right_column:
    movie_json = get_movie_info_by_movieID(movie_id_list[st.session_state.idx])
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

# print(st.session_state['city'])