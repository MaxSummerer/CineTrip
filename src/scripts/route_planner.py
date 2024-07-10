import requests
import json
import pandas as pd
import pydeck as pdk

url = "https://graphhopper.com/api/1/vrp"

query = {
  "key": "2a7eb34e-cedd-4215-9f6f-71459f92a694"
}

my_locations = [{'coordinates': [-118.45174, 33.98029], 'tags': " Jerry Maguire's beachfront home/office (undergoing a bit of renovation)", 'movieId': 1393},
                {'coordinates': [-118.36174, 34.09001], 'tags': ' Jerry gets the sack from Bob Sugar', 'movieId': 1393}, {'coordinates': [-118.382524, 33.8938781], 'tags': " Dorothy's modest little bungalow", 'movieId': 1393}, {'coordinates': [-118.39647, 34.02112], 'tags': ' Jerry and Dorothy blur the line between an office meeting and a first date', 'movieId': 1393}]

my_loc = []
ind = 0
for i in my_locations:
    loc_dict = {}
    loc_dict['id'] = str(ind)
    loc_dict['name'] = i["tags"]
    loc_dict['address'] = {"location_id":f"{i['coordinates'][0]}_{i['coordinates'][1]}",
                           "lon": i['coordinates'][0],
                           "lat": i['coordinates'][1]
                           }
    loc_dict['size'] = [1]
    my_loc.append(loc_dict)
    ind = ind + 1
print(my_loc)
payload = {
  "vehicles": [
    {
      "vehicle_id": "vehicle-1",
      "type_id": "cargo-bike",
      "start_address": {
        "location_id": "la",
        "lon": -118.242766, 
        "lat": 34.0536909
      },
    #   "earliest_start": 1554804329,
    #   "latest_end": 1554808329,
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
#   "services": [
#     {
#       "id": "s-1",
#       "name": "visit-Joe",
#       "address": {
#         "location_id": "13.375854_52.537338",
#         "lon": 13.375854,
#         "lat": 52.537338
#       },
#       "size": [
#         1
#       ],
#     },
#     {
#       "id": "s-2",
#       "name": "serve-Peter",
#       "address": {
#         "location_id": "13.393364_52.525851",
#         "lon": 13.393364,
#         "lat": 52.525851
#       },
#       "size": [
#         1
#       ]
#     },
#     {
#       "id": "s-3",
#       "name": "visit-Michael",
#       "address": {
#         "location_id": "13.416882_52.523543",
#         "lon": 13.416882,
#         "lat": 52.523543
#       },
#       "size": [
#         1
#       ]
#     },
#     {
#       "id": "s-4",
#       "name": "do nothing",
#       "address": {
#         "location_id": "13.395767_52.514038",
#         "lon": 13.395767,
#         "lat": 52.514038
#       },
#       "size": [
#         1
#       ]
#     }
#   ],
  "services": my_loc,

#   "shipments": [
#     {
#       "id": "7fe77504-7df8-4497-843c-02d70b6490ce",
#       "name": "pickup and deliver pizza to Peter",
#       "priority": 1,
#       "pickup": {
#         "address": {
#           "location_id": "13.387613_52.529961",
#           "lon": 13.387613,
#           "lat": 52.529961
#         }
#       },
#       "delivery": {
#         "address": {
#           "location_id": "13.380575_52.513614",
#           "lon": 13.380575,
#           "lat": 52.513614
#         }
#       },
#       "size": [
#         1
#       ],
#       "required_skills": [
#         "physical strength"
#       ]
#     }
#   ],
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

response = requests.post(url, json=payload, headers=headers, params=query)

data = response.json()

if data['status'] == 'finished':
    print(data['solution']['routes'][0]['points'])
    paths = data['solution']['routes'][0]['points']
    print(len(paths))
    indexx = 0
    return_data = []
    for i in paths:
        # print(len(i['coordinates']))
        ele_dict = {}
        ele_dict['name'] = f"path{indexx}"
        ele_dict['color'] = "#fec76fff"
        ele_dict['path'] = i['coordinates']
        return_data.append(ele_dict)
        indexx = indexx +1
    
    with open('data.json', 'w') as f:
        json.dump(return_data, f)
    pd.DataFrame(return_data).to_csv('data2.csv', index=False)

    layers = [
    pdk.Layer(
        "PathLayer",
        data=pd.DataFrame(return_data),
        get_path='path',
        # get_width=200,
        get_color='[254, 199, 111, 240]',
        # pickable=True,
        # auto_highlight=True,
        width_min_pixels=5,
        ),
]

    view_state = pdk.ViewState(longitude=-118.45174, latitude= 33.98029, zoom=10)

    pdk.Deck(
        [layers],
        initial_view_state=view_state
    ).to_html("tri.html", open_browser=True)

    
    