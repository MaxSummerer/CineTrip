import json
import string
import requests
import pandas as pd

from movieLensUtils import load_links_data, count_all_locations, extract_movies_and_locations_from_json_file


links_data = load_links_data()

g_tot = 0
ds_df = pd.DataFrame(columns=[ 'movieId', 'imgUrl','imgMovieLocation','imgRealLocation'])
movies_df = pd.DataFrame(columns=[ 'title', 'url','count_in_TMDB'])

for letter in string.ascii_lowercase:
    # if letter == 'e':
    file_path = f"name/{letter}.json"  # Replace with your actual file path
    g_tot += count_all_locations(file_path)   
    ds_df, movies_df = extract_movies_and_locations_from_json_file(file_path, ds_df, movies_df, links_data)

file_path = f"name/0.json"
ds_df, movies_df = extract_movies_and_locations_from_json_file(file_path, ds_df, movies_df, links_data)
g_tot += count_all_locations(file_path)
print("you should have ",g_tot)
print("you got ", ds_df.shape[0])
# print(ds_df)
# print(movies_df)
ds_df.to_csv('string_locations.csv', index=False)
movies_df.to_csv('movies_added.csv', index=False)



# print(dataset['About-Time'])
# print(dataframe_with_locations_and_TMDBid(dataset['About-Time']))



