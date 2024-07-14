import streamlit as st
import json
import requests
from opencage.geocoder import OpenCageGeocode
import time

CITIES_FOLDER_PATH = "src/data/cities/"
city_list=[]

# get city and country name from json files
def get_country_fullname():
    file_path = CITIES_FOLDER_PATH + 'countries.json'
    country_data = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f_file:
            country_data = json.load(f_file)


    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        country_data = {}
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        country_data = {}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        country_data = {}
    return country_data


def get_city_name():
    country_data = get_country_fullname()
    file_path = CITIES_FOLDER_PATH + 'cities.json'
    try:
        with open(file_path, 'r', encoding='utf-8') as fcc_file:
            city_data = json.load(fcc_file)
            cities = {}
            country_list = []
            for entry in city_data:
                country_code = entry['country']
                if country_code in country_data.keys():
                    country_name = country_data[country_code]
                    if country_name:
                        city = entry['name']
                        if country_name not in country_list:
                            country_list.append(country_name)
                            cities[country_name] = [city]
                        else:
                            cities[country_name].append(city)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        cities = {}
        country_list = []
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        cities = {}
        country_list = []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        cities = {}
        country_list = []
    return country_list, cities


# get user location using ip
def get_ip():
    response = requests.get("https://api.ipify.org?format=json")
    ip = response.json()['ip']
    return ip


def get_location(ip):
    response = requests.get(f"https://ipinfo.io/{ip}/json")
    data = response.json()
    return data


def clear_session_state():
    st.session_state['city'] = ""
    st.session_state['country'] = ""


# given address string, output lat and lon
def get_lat_lon(address):
    api_key = '1d8774227563448b981d6712113b457e'
    geocoder = OpenCageGeocode(api_key)
    result = geocoder.geocode(address)
    if result and len(result):
        latitude = result[0]['geometry']['lat']
        longitude = result[0]['geometry']['lng']
        return latitude, longitude
    else:
        # garching:
        return 48.2488721, 11.6532477


def on_click(city, country):

    st.session_state['country'] = country
    st.session_state['city'] = city
    st.session_state['country_index'] = country_list.index(st.session_state['country'])
    st.session_state['city_index'] = cities[st.session_state['country']].index(st.session_state['city'])
    print("on click changed ", st.session_state['country_index'], st.session_state['country'])


def on_click_auto_location():
    ip = get_ip()
    location_data = get_location(ip)
    city = location_data.get('city', 'Unknown City')
    country_code = location_data.get('country', 'Unknown Country')
    country_data = get_country_fullname()
    country_full_name = country_data[country_code]
    st.session_state['country'] = country_full_name.strip()
    st.session_state['city'] = city.strip()
    st.session_state['country_index'] = country_list.index(st.session_state['country'])
    st.session_state['city_index'] = cities[st.session_state['country']].index(st.session_state['city'])


if 'city' not in st.session_state:
    st.session_state['city'] = ""

if 'country' not in st.session_state:
    st.session_state['country'] = ""

if 'city_index' not in st.session_state:
    st.session_state['city_index'] = 0

if 'country_index' not in st.session_state:
    st.session_state['country_index'] = 0

country_list, cities = get_city_name()

col1, col2 = st.columns([2, 1])

with col1:
    st.title("Step 1: choose your location")

        # Dropdown for countries
    selected_country = st.selectbox("🌎Select a Country", country_list, index=st.session_state['country_index'])

    # Dropdown for cities
    if selected_country:

        print("after ", selected_country)
        #
        city_list = cities[selected_country]

        if st.session_state['country'] != selected_country:
            st.session_state['city_index']=0

        selected_city = st.selectbox("🏰Select a City", city_list, index=st.session_state['city_index'])


    latitude, longitude = get_lat_lon(selected_city + ", " + selected_country)


with col2:
    st.button('📍Your position', on_click=on_click_auto_location)

    with st.container():
        st.subheader("Popular locations")
        st.button("London", on_click=on_click, args=["London", "United Kingdom"])
        st.button("Salzburg", on_click=on_click, args=["Salzburg", "Austria"])
        st.button("Paris", on_click=on_click, args=["Paris", "France"])
        st.button("Los Angeles", on_click=on_click, args=["Los Angeles", "United States"])
        st.button("New York City", on_click=on_click, args=["New York City", "United States"])

st.write(f"""
        You selected: {selected_city} in {selected_country}
        \nLongitude: {longitude}, Latitude: {latitude}
        """)
# with col2:
if st.button("Next"):
    st.session_state['city'] = selected_city
    st.session_state['country'] = selected_country
    st.switch_page("pages/step2.py")
