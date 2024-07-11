import streamlit as st
import json
import requests
from opencage.geocoder import OpenCageGeocode

CITIES_FOLDER_PATH = "src/data/cities/"


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


if 'city' not in st.session_state:
    st.session_state['city'] = ""

if 'country' not in st.session_state:
    st.session_state['country'] = ""

country_list, cities = get_city_name()

col1, col2 = st.columns([5, 1])

with col1:
    st.title("Step 1: choose your location")
with col2:
    if st.button('📍Your position'):
        ip = get_ip()
        location_data = get_location(ip)
        city = location_data.get('city', 'Unknown City')
        country_code = location_data.get('country', 'Unknown Country')
        country_data = get_country_fullname()
        country_full_name = country_data[country_code]
        st.session_state['city'] = city.strip()
        st.session_state['country'] = country_full_name.strip()

country_index = 0
city_index = 0
country_full_name = ""

if st.session_state['country'] and st.session_state['city'] and st.session_state['country'] != "":
    try:
        # country_data = get_country_fullname()
        # country_full_name = country_data[st.session_state['country']]
        # st.session_state['country'] = country_full_name
        country_index = country_list.index(st.session_state['country'])
    except ValueError:
        country_index = 0

# Dropdown for countries
selected_country = st.selectbox("🌎Select a Country", country_list, index=country_index, on_change=clear_session_state)
# Dropdown for cities
if selected_country:

    city_list = cities[selected_country]
    try:
        if st.session_state['country'] and st.session_state['city'] and st.session_state['city'] != "":
            city_index = cities[st.session_state['country']].index(st.session_state['city'])
    except ValueError:
        city_index = 0

    selected_city = st.selectbox("🏰Select a City", city_list, index=city_index, on_change=clear_session_state)
else:
    selected_city = st.selectbox("🏰Select a City", [], on_change=clear_session_state)

latitude, longitude = get_lat_lon(selected_city + ", " + selected_country)
st.session_state['city'] = selected_city
st.session_state['country'] = selected_country

st.write(f"""
        You selected: {selected_city} in {selected_country}
        \nLongitude: {longitude}, Latitude: {latitude}
        """)
# with col2:
if st.button("Next"):
    # st.session_state['city'] = selected_city
    # st.session_state['country'] = selected_country

    st.switch_page("pages/step2.py")
