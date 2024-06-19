import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st
from opencage.geocoder import OpenCageGeocode
import base64


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


# given a dict of movie location and tags, the map with all info will be shown in this page
example_dict = [{"address": "Baker Street Underground Station Undergound Ltd, Marylebone Rd, London NW1 5LJ",
                 "tags": "Sherlock Holmes Street"},
                {"address": "Praed St, London W2 1HU",
                 "tags": "Paddington Bear"},
                {"address": "85 Albert Embankment, London SE11 5AW",
                 "tags": "Sky Fall"}
                ]

geocoded_data = []
for item in example_dict:
    lat, lon = get_lat_lon(item['address'])

    geocoded_data.append({
        "latitude": lat,
        "longitude": lon,
        "tags": item['tags']
    })

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
        with st.container(height=350,border=True):
            for item in example_dict:
                with st.container(border=True):
                    st.write(item["address"])
                    st.write(item["tags"])

else:
    st.write("No geocoded data available.")
