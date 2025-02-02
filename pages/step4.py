from ast import literal_eval
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st
from opencage.geocoder import OpenCageGeocode
import base64
import requests
from PIL import Image
from io import BytesIO
import math
from src.scripts.movieLensUtils import load_locations_csv, search_in_ml_latest_by_name, search_in_ml_hundred_by_id, \
    load_links_data, create_X, give_me_data, search_in_ml_latest_by_id
from src.scripts.recommender import MovieRecommender
from src.scripts.gpt_recommender import get_recommendations_from_GPT
from src.scripts.geocodingUtils import fromat_loctions_for_graphhopper, request_routes_for_locations, haversine

st.set_page_config(initial_sidebar_state="collapsed", layout="wide")

distance_radius = 75

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


def get_movie_info_by_movieID(movie_id, api_key="<insert your key>"):
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
    api_key = '<insert your key>'
    geocoder = OpenCageGeocode(api_key)
    result = geocoder.geocode(address)
    if result and len(result):
        latitude = result[0]['geometry']['lat']
        longitude = result[0]['geometry']['lng']
        return latitude, longitude
    else:
        # garching:
        return 48.2488721, 11.6532477


def filter_based_on_distance(locations_array, city):
    geocoded_data = []
    city_lat, city_lon = get_lat_lon(city)
    # print(city, city_lat, city_lon)
    for item in locations_array:
        print("address ",item['address'])
        lat, lon = get_lat_lon(item['address'])
        distance = haversine(lat, lon, city_lat, city_lon)
        if distance < distance_radius:
            print("adding ", item['address'])
            geocoded_data.append({
                "latitude": lat,
                "longitude": lon,
                "tags": item['tags'],
                "movieId": item['movieId'],
                "address":item['address'],
                "imgUrl":item['imgUrl'],                
            })
    return geocoded_data



locations_csv = load_locations_csv()
example_dict = [{"address": "Baker Street Underground Station Undergound Ltd, Marylebone Rd, London NW1 5LJ",
                 "tags": "Sherlock Holmes Street"},
                {"address": "Praed St, London W2 1HU",
                 "tags": "Paddington Bear"},
                {"address": "85 Albert Embankment, London SE11 5AW",
                 "tags": "Sky Fall"}
                ]
mr = None

# TODO: change these if blocks for proper navigation
# if 'mr_object' not in st.session_state:  # change to 'not in' and create new object for mr/ but why tho (see later)
# data, movie_titles = give_me_data()
# df = data.iloc[:, :3]
# df = df.rename(columns={df.columns[1]: 'movie_id'})
# X, user_mapper, movie_mapper, user_inv_mapper, movie_inv_mapper = create_X(df)    
mr = MovieRecommender()

if 'city' not in st.session_state and 'country' not in st.session_state:  # go back to step1
    city = 'Chicago'
    country = 'USA'
else:
    city, country = st.session_state['city'], st.session_state['country']

if 'if_update' not in st.session_state:
    st.session_state['if_update'] = True
else:
    st.session_state['if_update'] = True

if 'recs' not in st.session_state:  # change to 'not in' and redirect to step 2
    recs = [50, 174, 181, 79, 96, 56, 172, 204, 121, 195]
    # Star Wars (1977), Raiders of the Lost Ark (1981), Return of the Jedi (1983),
    #  Fugitive, The (1993), Terminator 2: Judgment Day (1991), Pulp Fiction (1994),
    # Empire Strikes Back, The (1980), Back to the Future (1985), Independence Day (ID4) (1996),
    # Terminator, The (1984)
else:
    recs = st.session_state['recs']
    recs_names = st.session_state['recs_names']

if 'selected_recs' in st.session_state:
    selected_recs = st.session_state['selected_recs']
    # print("seleceted")
    # print(arecs)
    # print(recs)
    if selected_recs:
        recs = selected_recs
    # print(recs_names)

recs_dict = {}
filtered_recs = []

for i in recs:
    movie_details = search_in_ml_latest_by_id(i)
    # print(movie_details)
    # if len(movie_details["title"].values) == 0:
    #     continue
    # other_movie_details = search_in_ml_latest_by_name(movie_details["title"].values[0])
    # print(other_movie_details)
    # if len(other_movie_details["movieId"].values) > 0:
    filtered_recs.append(movie_details["movieId"].values[0])
    recs_dict[movie_details["movieId"].values[0]] = movie_details["title"].values[0]

# print("_",city,"_")
# print(recs_dict)
if mr:
    example_dict = mr.filter_dataframe(locations_csv, filtered_recs, city)
    # print("string filter")
    # print("filtered_str",len(mr.filter_dataframe(locations_csv, filtered_recs, city)))
    # print("dict ",example_dict)

print("whole",len(example_dict))

geocoded_data = []
for item in example_dict:
    # print(item)
    lat, lon = get_lat_lon(item['address'])

    geocoded_data.append({
        "latitude": lat,
        "longitude": lon,
        "tags": item['tags'],
        "movieId": item['movieId'],
        "imgUrl" : item['imgUrl'],
        'address': item['address']
    })
# print("compare datas now for ", city)
# print(mr.filter_dataframe(locations_csv, filtered_recs, city))
# print(filter_based_on_distance(example_dict, city))
# geocoded_data = filter_based_on_distance(example_dict, city)
# print("filtered_coor",len(geocoded_data))
st.title('Results: Recommended Movie Locations')
# Create Pydeck map
if geocoded_data:#geocoded_data
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


    icon_image_base64 = encode_image("src/data/img/location-pin.png")
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
    print(data)

    deck_layers = []
    city_lat, city_lon = get_lat_lon(city)

    icon_layer = pdk.Layer(
        type="IconLayer",
        data=data,
        get_icon="icon_data",
        get_size=4,
        size_scale=15,
        get_position="coordinates",
        pickable=True,
    )

    deck_layers.append(icon_layer)
    
    formatted_locations = fromat_loctions_for_graphhopper(data)
            # try:
    available_route, routes_dataset = request_routes_for_locations(formatted_locations[0:5], city_lon, city_lat)


    #routes_dataset = []
    # print( available_route)
    # print("got here",len(routes_dataset))

    if available_route:
        # routes_dataset = routes_dataset[0:5]
        path_layer = pdk.Layer(
            "PathLayer",
            data=routes_dataset,
            get_path='path',
            # get_width=100,
            # get_color='[231, 77, 62, 200]',
            get_color='[0, 194, 255, 200]',
            pickable=True,
            auto_highlight=True,
            width_min_pixels=3,
        )
        deck_layers.append(path_layer)
            # r.update()

    # print( deck_layers)

    tooltip = {"html": "{tags}"}

    r = pdk.Deck(
        map_style='mapbox://styles/mapbox/streets-v11',
        initial_view_state=initial_view_state,
        layers=deck_layers,
        tooltip=tooltip,
    )
    col1, col2 = st.columns([2, 2])
    with col1:
        # map
        #places_map = st.pydeck_chart(r, use_container_width=True)
        places_map = st.pydeck_chart(r)
        # if st.button("Give me my route"):
            

    with col2:
        # address information
        with st.container(height=350, border=True):
            ind = 0
            for item in geocoded_data:
                with st.container(border=True):
                    img_col, name_col = st.columns([1,3])
                    with img_col:
                        st.image(resize_image(item['imgUrl'], (200, 120)))          
                    with name_col:
                        address_split = item["address"].split(",")
                        if len(address_split) > 2:
                            new_address = ",".join(address_split[0:2])
                        else:
                            new_address = item["address"]
                        
                        # st.subheader(new_address)
                        # st.image(resize_image(item['imgUrl'], (200, 120)))

                        st.markdown(f'''
                        <h4>{new_address}</h4>
                        <p style="color:grey;">In {recs_dict[item["movieId"]]},  {item["tags"]}</p>
                        ''', unsafe_allow_html=True)
                        # st.write("In " + recs_dict[item["movieId"]] + ", ", item["tags"])                        
                        if st.button("Quiz on this place!", key=ind):
                            st.session_state["questionnaire_location"] = item["address"]
                            st.switch_page("pages/stepExtra.py")
                ind = ind+1
                    # st.write(item["tags"])

    heading1, heading2 = st.columns([5, 1])

    with heading1:
        st.subheader("Movies you selected!", divider='rainbow')

        movies_per_row = 5
    len_rows = len(filtered_recs) // movies_per_row
    actual_cut = len(filtered_recs) / movies_per_row
    item_left = range(len_rows * movies_per_row, len(filtered_recs))
    if len_rows == actual_cut:
        for row in range(len_rows):
            carousal_cols = st.columns([1] * movies_per_row)# change
            for i in range(movies_per_row):
                with carousal_cols[i]:
                    item = row * movies_per_row + i
                    with st.container(height=320, border=True):
                        if load_image(filtered_recs[item]):
                            st.image(load_image(filtered_recs[item]))
                        st.write(recs_dict[filtered_recs[item]])
    else:
        for row in range(len_rows):
            carousal_cols = st.columns([1] * movies_per_row)# change
            for i in range(movies_per_row):
                with carousal_cols[i]:
                    item = row * movies_per_row + i
                    with st.container(height=320, border=True):
                        if load_image(filtered_recs[item]):
                            st.image(load_image(filtered_recs[item]))
                        st.write(recs_dict[filtered_recs[item]])
        last_row = st.columns([1] * movies_per_row)# change
        for i in range(len(item_left)):
            with last_row[i]:
                item = item_left[i]
                with st.container(height=320, border=True):
                    if load_image(filtered_recs[item]):
                        st.image(load_image(filtered_recs[item]))
                    st.write(recs_dict[filtered_recs[item]])

else:
    st.write("GPT reccomendations available.")
    # recs_names = ["Inception", "Top Gun", "Mission Impossible"]

    GPT_locations = get_recommendations_from_GPT(city,recs_names)
    
    


    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()


    icon_image_base64 = encode_image("src/data/img/location-pin.png")
    icon_image_data = f"data:image/png;base64,{icon_image_base64}"
    icon_data = {
        "url": icon_image_data,
        "width": 128,
        "height": 128,
        "anchorY": 128,
    }
    # print("routing",len(data))
    if len(GPT_locations.keys()) == 1:

        print("good")
        data = [
        {
            "coordinates": [data['longitude_latitude'].split(", ")[0], data['longitude_latitude'].split(", ")[1]],
            "tags": data['locationRef'],
            "icon_data": icon_data,
            "movieId": ind,
            "title": data['movie_name'],
            "address": data["location"]+", "+data['area_street']+", "+data['city_country'],
            "tags": data['locationRef']
        }
        for ind, data in enumerate(GPT_locations[list(GPT_locations.keys())[0]])
    ]
    else:
        data = [
        {
            "coordinates": [GPT_locations['longitude_latitude'].split(", ")[0], GPT_locations['longitude_latitude'].split(", ")[1]],
            "tags": GPT_locations['locationRef'],
            "icon_data": icon_data,
            "movieId": 0,
            "title": GPT_locations['movie_name'],
            "address": GPT_locations["location"]+", "+GPT_locations['area_street']+", "+GPT_locations['city_country'],
            "tags": GPT_locations['locationRef']
        }
    ]
    initial_view_state = pdk.ViewState(
        latitude=data[0]['coordinates'][1],
        longitude=data[0]['coordinates'][0],
        zoom=11,
        pitch=0,
        height=350, width=600
    )

    deck_layers = []
    city_lat, city_lon = get_lat_lon(city)

    if False:#len(data) > 1
        formatted_locations = fromat_loctions_for_graphhopper(data)
        available_route, routes_dataset = request_routes_for_locations(formatted_locations, city_lon, city_lat)
        # print( available_route)
        # print("got here",len(routes_dataset))

        if available_route:
            # routes_dataset[0:5]
            path_layer = pdk.Layer(
                "PathLayer",
                data=routes_dataset,
                get_path='path',
                # get_width=100,
                # get_color='[231, 77, 62, 200]',
                get_color='[0, 194, 255, 200]',
                pickable=True,
                auto_highlight=True,
                width_min_pixels=3,
            )
            deck_layers.append(path_layer)

    icon_layer = pdk.Layer(
        type="IconLayer",
        data=data,
        get_icon="icon_data",
        get_size=4,
        size_scale=15,
        get_position="coordinates",
        pickable=True,
    )

    deck_layers.append(icon_layer)

    # print( deck_layers)

    tooltip = {"html": "{tags}"}

    r = pdk.Deck(
        map_style='mapbox://styles/mapbox/streets-v11',
        initial_view_state=initial_view_state,
        layers=deck_layers,
        tooltip=tooltip,
    )
    GPTcol1, GPTcol2 = st.columns([2, 2])
    with GPTcol1:
        # map
        #places_map = st.pydeck_chart(r, use_container_width=True)
        places_map_gpt = st.pydeck_chart(r)

    with GPTcol2:
        # address information
        with st.container(height=350, border=True):
            ind = 0
            for item in data:
                with st.container(border=True):
                    img_col, name_col = st.columns([1,3])
                    # with img_col:
                        # st.image(resize_image(item['imgUrl'], (200, 120)))          
                    with name_col:
                        address_split = item["address"].split(",")
                        if len(address_split) > 2:
                            new_address = ",".join(address_split[0:2])
                        else:
                            new_address = item["address"]
                        
                        # st.subheader(new_address)
                        # st.image(resize_image(item['imgUrl'], (200, 120)))

                        st.markdown(f'''
                        <h4>{new_address}</h4>
                        <p style="color:grey;">In {item["title"]},  {item["tags"]}</p>
                        ''', unsafe_allow_html=True)
                        # st.write("In " + recs_dict[item["movieId"]] + ", ", item["tags"])                        
                        if st.button("Quiz on this place!", key=ind):
                            st.session_state["questionnaire_location"] = item["address"]
                            st.switch_page("pages/stepExtra.py")
                ind = ind+1
                    # st.write(item["tags"])

    

st.subheader("Not satisfied with the results?", divider="rainbow")
col1, col2 = st.columns(2)
with col1:
    if st.button("Change your location"):
        data=[]
        geocoded_data = []
        st.session_state.idx=0
        st.session_state['likes']=[]
        st.session_state['dislikes'] = []
        st.session_state['didntWatch'] = []
        st.session_state["show"] = -1
        st.switch_page("pages/step1.py")
with col2:
    if st.button("Choose the movies again"):
        data=[]
        geocoded_data = []
        st.session_state.idx=0
        st.session_state['likes'] = []
        st.session_state['dislikes'] = []
        st.session_state['didntWatch'] = []
        st.session_state["show"] = -1
        st.switch_page("pages/step2.py")


