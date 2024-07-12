import requests
import json
import pandas as pd
import pydeck as pdk
import math

URL_GRAPHHOPPER = "https://graphhopper.com/api/1/vrp"

GRAPHHOPPER_API_KEY_QUERY = {
  "key": "2a7eb34e-cedd-4215-9f6f-71459f92a694"
}

# my_locations = [{'coordinates': [-118.45174, 33.98029], 'tags': " Jerry Maguire's beachfront home/office (undergoing a bit of renovation)", 'movieId': 1393},
#                 {'coordinates': [-118.36174, 34.09001], 'tags': ' Jerry gets the sack from Bob Sugar', 'movieId': 1393}, {'coordinates': [-118.382524, 33.8938781], 'tags': " Dorothy's modest little bungalow", 'movieId': 1393}, {'coordinates': [-118.39647, 34.02112], 'tags': ' Jerry and Dorothy blur the line between an office meeting and a first date', 'movieId': 1393}]


def fromat_loctions_for_graphhopper(ui_locations):
    graphopper_locations = []
    ind = 0
    for i in ui_locations:
        loc_dict = {}
        loc_dict['id'] = str(ind)
        loc_dict['name'] = i["tags"]
        loc_dict['address'] = {"location_id":f"{i['coordinates'][0]}_{i['coordinates'][1]}",
                            "lon": i['coordinates'][0],
                            "lat": i['coordinates'][1]
                            }
        loc_dict['size'] = [1]
        graphopper_locations.append(loc_dict)
        ind = ind + 1
    return graphopper_locations

def request_routes_for_locations(graphopper_locations, city_lon, city_lat):
    payload = {
    "vehicles": [
        {
        "vehicle_id": "vehicle-1",
        "type_id": "cargo-bike",
        "start_address": {
            "location_id": "la",
            "lon": city_lon, 
            "lat": city_lat
        },
        "max_jobs": 10
        }
    ],
    "vehicle_types": [
        {
        "type_id": "cargo-bike",
        "capacity": [
            10
        ],
        "profile": "bike"
        }
    ],
    "services": graphopper_locations,
    "objectives": [
        {
        "type": "min",
        "value": "completion_time"
        }
    ],
    "configuration": {
        "routing": {
        "calc_points": True,
        "snap_preventions": [
            "motorway",
            "trunk",
            "tunnel",
            "bridge",
            "ferry"
        ]
        }
    }
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(URL_GRAPHHOPPER, json=payload, headers=headers, params=GRAPHHOPPER_API_KEY_QUERY)

    data = response.json()

    if data['status'] == 'finished':
        # print(data['solution']['routes'][0]['points'])
        paths = data['solution']['routes'][0]['points']
        print(len(paths))
        ind = 0
        return_data = []
        for i in paths:
            # print(len(i['coordinates']))
            ele_dict = {}
            ele_dict['name'] = f"path{ind}"
            # ele_dict['color'] = "#fec76fff"
            ele_dict['path'] = i['coordinates']
            return_data.append(ele_dict)
            ind = ind +1
        
        
        print("got_routes",len(return_data))
        # with open('data.json', 'w') as f:
        #     json.dump(return_data, f)
        return True, pd.DataFrame(return_data)
    else:
        return False, None

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 

    # Radius of earth in kilometers is 6371
    km = 6371 * c
    return km        
    