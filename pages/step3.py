import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st
from opencage.geocoder import OpenCageGeocode
import base64
import requests
from PIL import Image
from io import BytesIO
from movieLensUtils import load_locations_csv, search_in_ml_latest_by_name, search_in_ml_hundred_by_id, load_links_data
from recommender import MovieRecommender


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
    links_data = load_links_data()
    # print("running ", movie_id, type(movie_id))
    imdbId = links_data[links_data['movieId'] == str(movie_id)]['imdbId']
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

def get_lat_lon(address):
    api_key = '8ff0d285a2074146b399833d726fc5af'
    geocoder = OpenCageGeocode(api_key)
    result = geocoder.geocode(address)
    if result and len(result):
        latitude = result[0]['geometry']['lat']
        longitude = result[0]['geometry']['lng']
        return latitude, longitude
    else:
        # garching:
        return 48.2488721, 11.6532477

locations_csv = load_locations_csv()
example_dict = [{"address": "Baker Street Underground Station Undergound Ltd, Marylebone Rd, London NW1 5LJ",
                 "tags": "Sherlock Holmes Street"},
                {"address": "Praed St, London W2 1HU",
                 "tags": "Paddington Bear"},
                {"address": "85 Albert Embankment, London SE11 5AW",
                 "tags": "Sky Fall"}
                ]
mr = None
if 'mr_object' in st.session_state: # change to 'not in' and create new object for mr/ but why tho (see later)
    mr = st.session_state['mr_object']

if 'city' not in st.session_state and 'country' not in st.session_state: # go back to step1
    city = 'Los Angeles'
    country = 'USA'
else:
    city, country = st.session_state['city'], st.session_state['country']


if 'recs' not in st.session_state: # change to 'not in' and redirect to step 2
    recs = [50, 174, 181, 79, 96, 56, 172, 204, 121, 195]
    # Star Wars (1977), Raiders of the Lost Ark (1981), Return of the Jedi (1983),
    #  Fugitive, The (1993), Terminator 2: Judgment Day (1991), Pulp Fiction (1994),
    # Empire Strikes Back, The (1980), Back to the Future (1985), Independence Day (ID4) (1996), 
    # Terminator, The (1984)
else:   
    recs = st.session_state['recs']
    recs_names = st.session_state['recs_names']
    # recs_dict = dict(zip(recs, recs_names))
    # print(recs_dict)
recs_dict = {}
filtered_recs = []
# print("hello")
for i in recs:
    
    # print("hi",i)
    movie_details = search_in_ml_hundred_by_id(i)
    # print(movie_details)
    if len(movie_details["title"].values) == 0:
        continue
    other_movie_details = search_in_ml_latest_by_name(movie_details["title"].values[0])
    # print(other_movie_details)
    if len(other_movie_details["movieId"].values) > 0:
        filtered_recs.append(other_movie_details["movieId"].values[0])
        recs_dict[other_movie_details["movieId"].values[0]] = movie_details["title"].values[0]

# print("_",city,"_")
print(recs_dict)

example_dict = mr.filter_dataframe(locations_csv, filtered_recs, city )
    
print(len(example_dict))

geocoded_data = []
for item in example_dict:
    lat, lon = get_lat_lon(item['address'])

    geocoded_data.append({
        "latitude": lat,
        "longitude": lon,
        "tags": item['tags'],
        "movieId" : item['movieId']
    })
# print(geocoded_data)
st.title('Results: recommended Locations')
# Create Pydeck map
if geocoded_data:
    initial_view_state = pdk.ViewState(
        latitude=geocoded_data[0]['latitude'],
        longitude=geocoded_data[0]['longitude'],
        zoom=11,
        pitch=0,
        height=350, width=600
    )


    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()


    icon_image_base64 = encode_image("data/img/location-pin.png")
    icon_image_data = f"data:image/png;base64,{icon_image_base64}"
    icon_data = {
        "url": icon_image_data,
        "width": 128,
        "height": 128,
        "anchorY": 128,
    }
    data = [
        {
            "coordinates": [data['longitude'], data['latitude']],
            "tags": data['tags'],
            "icon_data": icon_data,
            "movieId": data['movieId']
        }
        for data in geocoded_data
    ]
    icon_layer = pdk.Layer(
        type="IconLayer",
        data=data,
        get_icon="icon_data",
        get_size=4,
        size_scale=15,
        get_position="coordinates",
        pickable=True,
    )

    tooltip = {"html": "{tags}"}

    r = pdk.Deck(
        map_style='mapbox://styles/mapbox/streets-v11',
        initial_view_state=initial_view_state,
        layers=[icon_layer],
        tooltip=tooltip,
    )
    col1,col2=st.columns([2,1])
    with col1:
        # map
        st.pydeck_chart(r, use_container_width=True)
    with col2:
        # address information
        with st.container(height=350, border=True):
            for item in example_dict:
                with st.container(border=True):
                    st.write(item["address"])
                    st.image(resize_image(item['imgUrl'], (200, 120)))
                    st.write("In "+recs_dict[item["movieId"]]+", ",item["tags"])
                    
                    # st.write(item["tags"])

                    

    heading1, heading2 = st.columns([5, 1])


    with heading1:
        st.subheader("These are the movies that we think you like!", divider='rainbow')
    # next_col1, next_col2 =st.columns([1,8])
    # with next_col2:
    #     # address information
        
    #     for item in recs_dict.keys():
    #         with st.container(height=250,border=True):
    #             if load_image(item):
    #                 st.image(load_image(item))
    #             st.write(recs_dict[item])
    #             # st.write(item["tags"])
    #             # st.write("In "+recs_dict[item["movieId"]]+", ",item["tags"])
    # cols = st.columns([1]*len(filtered_recs))

    # for item in range(len(filtered_recs)):
    #     with cols[item]:
    #         with st.container(height=250,border=True):
    #             if load_image(filtered_recs[item]):
    #                 st.image(load_image(filtered_recs[item]))
    #             st.write(recs_dict[filtered_recs[item]])

    len_rows = len(filtered_recs) // 4
    actual_cut = len(filtered_recs) / 4
    item_left = range(len_rows * 4,len(filtered_recs))
    if len_rows == actual_cut:
        for row in range(len_rows):
            carousal_cols = st.columns([1,1,1,1])
            for i in range(4):
                with carousal_cols[i]:
                    item = row* 4 + i
                    with st.container(height=320,border=True):
                        if load_image(filtered_recs[item]):
                            st.image(load_image(filtered_recs[item]))
                        st.write(recs_dict[filtered_recs[item]])
    else:
        for row in range(len_rows):
            carousal_cols = st.columns([1,1,1,1])
            for i in range(4):
                with carousal_cols[i]:
                    item = row* 4 + i
                    with st.container(height=320,border=True):
                        if load_image(filtered_recs[item]):
                            st.image(load_image(filtered_recs[item]))
                        st.write(recs_dict[filtered_recs[item]])
        last_row = st.columns([1,1,1,1])      
        for i in range(len(item_left)):
            with last_row[i]:
                item = item_left[i]
                with st.container(height=320,border=True):
                    if load_image(filtered_recs[item]):
                        st.image(load_image(filtered_recs[item]))
                    st.write(recs_dict[filtered_recs[item]])

else:
    st.write("No geocoded data available.")
