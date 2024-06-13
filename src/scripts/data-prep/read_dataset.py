import json
import string
import requests
import pandas as pd
import os


DATA_FILEPATH = "../../src/data/"
MOVIE_LENS_FILEPATH = DATA_FILEPATH+"ml-latest/"
LOCATIONS_FILEPATH = DATA_FILEPATH+"locations-json/"

def load_links_data():
    df = pd.read_csv(MOVIE_LENS_FILEPATH+"links.csv")
    # df = pd.read_csv("../../")
    df.movieId = df.movieId.astype(str)
    df.imdbId = df.imdbId.astype(str)
    df.tmdbId = df.tmdbId.astype(str)
    return df

def TMDB_movie_search_by_name(movie_name):
    url = "https://api.themoviedb.org/3/search/movie?query="+movie_name+"&include_adult=false&language=en-US&page=1"

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIzZWFmM2VmMDQ1MGY4MjZkMzA3YWQ4NDU4M2UxOWI3OCIsInN1YiI6IjViMTYyZjhlOTI1MTQxNzg0ZTAxMWQ0YyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.fjEuCJ5gceqP438QrE2T4lnXKvBORuf4EGPAr6bLRQM"
    }

    response = requests.get(url, headers=headers)
    return response.text

def get_movie_deets_from_TMDB(movie_name):
    movie_name = movie_name.replace("-", " ")
    return  TMDB_movie_search_by_name(movie_name)

def count_key_value_pairs(json_file_path):
    """
    Reads a JSON file and returns the total number of key-value pairs in the top-level object.

    Args:
        json_file_path (str): The path to the JSON file.

    Returns:
        int: The total number of key-value pairs.
    """

    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            return len(data) 
    except FileNotFoundError:
        print(f"Error: File '{json_file_path}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in file '{json_file_path}'.")
        return None

def count_all_locations(json_file_path):
    """
    Reads a JSON file and returns the total number of key-value pairs in the top-level object.

    Args:
        json_file_path (str): The path to the JSON file.

    Returns:
        int: The total number of key-value pairs.
    """

    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            location_cnt = 0
            for i in data:
                location_cnt += len(data[i]['imgMovieLocation'])
            return location_cnt 
    except FileNotFoundError:
        print(f"Error: File '{json_file_path}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in file '{json_file_path}'.")
        return None

def json_to_dict(json_file_path):
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"Error: File '{json_file_path}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in file '{json_file_path}'.")
        return None

def dataframe_with_locations_and_TMDBid(dict_ele, movies_df):
    movie_name = dict_ele["name"]
    
    TMDB_deets = json.loads(get_movie_deets_from_TMDB(movie_name))
    # print(TMDB_deets)
    movie_df = pd.DataFrame({'title':[movie_name],'url':[dict_ele['url']],'count_in_TMDB':[TMDB_deets['total_results']]})
    movies_df = pd.concat([movies_df, movie_df], ignore_index=True)
    if movie_df.count_in_TMDB.values == 0:
        return None, movies_df
    try:
        tmdbId = TMDB_deets['results'][0]['id']
        
        movieId = find_movie_lens_id_fromTMDB_id(tmdbId)
        
        #TODO: add movieId as col, fix the df creation command and run the script for all letters
        if len(movieId) == 0:
            raise Exception("movieId not found")
        
        df = pd.DataFrame(data=dict_ele)
        df.rename(columns={'name':"movieId"}, inplace=True)
        df.movieId = movieId.values[0]
        df.drop('url', axis=1, inplace=True)
        return df, movies_df
    except Exception as e:
        print(movie_name, e)
        return None, movies_df

links_data = load_links_data()

def find_movie_lens_id_fromTMDB_id(TMDB_id):
    TMDB_id = str(TMDB_id) + ".0"
    return links_data[links_data['tmdbId'] == TMDB_id]['movieId']
    

def find_dataset_len():
    g_tot = 0
    for letter in string.ascii_lowercase:
        file_path = f"name/{letter}.json"  # Replace with your actual file path
        key_value_count = count_key_value_pairs(file_path)
        if key_value_count is not None:
            print(f"Number of key-value pairs: {key_value_count}")
            g_tot += key_value_count
        break


    file_path = f"name/0.json"  # Replace with your actual file path
    key_value_count = count_key_value_pairs(file_path)
    g_tot += key_value_count

    return g_tot
# Example usage

def extract_movies_and_locations_from_json_file(file_path, ds_df, movies_df):
    dataset = json_to_dict(file_path)
    # cnt = 0

    for a in dataset:
        try:
        # if a == 'Amelie':
            df, movies_df = dataframe_with_locations_and_TMDBid(dataset[a], movies_df)
            ds_df = pd.concat([df,ds_df])
        # cnt +=1
        # if cnt == 5:
        #     break
        except Exception as e:
            print(a, e)

    # print(ds_df)
    # print(movies_df)
    return ds_df, movies_df



  # Replace with your actual file path


g_tot = 0
ds_df = pd.DataFrame(columns=[ 'movieId', 'imgUrl','imgMovieLocation','imgRealLocation'])
movies_df = pd.DataFrame(columns=[ 'title', 'url','count_in_TMDB'])

for letter in string.ascii_lowercase:
    # if letter == 'e':
    file_path = LOCATIONS_FILEPATH+f"{letter}.json"  # Replace with your actual file path
    g_tot += count_all_locations(file_path)   
    ds_df, movies_df = extract_movies_and_locations_from_json_file(file_path, ds_df, movies_df)

file_path = LOCATIONS_FILEPATH+f"0.json"
ds_df, movies_df = extract_movies_and_locations_from_json_file(file_path, ds_df, movies_df)
g_tot += count_all_locations(file_path)
print("you should have ",g_tot)
print("you got ", ds_df.shape[0])
# print(ds_df)
# print(movies_df)
ds_df.to_csv(DATA_FILEPATH+'string_locations.csv', index=False)
movies_df.to_csv(DATA_FILEPATH+'movies_added.csv', index=False)




