import json
import string
import requests
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix


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


def dataframe_with_locations_and_TMDBid(dict_ele, movies_df, links_data):
    movie_name = dict_ele["name"]
    
    TMDB_deets = json.loads(get_movie_deets_from_TMDB(movie_name))
    # print(TMDB_deets)
    movie_df = pd.DataFrame({'title':[movie_name],'url':[dict_ele['url']],'count_in_TMDB':[TMDB_deets['total_results']]})
    movies_df = pd.concat([movies_df, movie_df], ignore_index=True)
    if movie_df.count_in_TMDB.values == 0:
        return None, movies_df
    try:
        tmdbId = TMDB_deets['results'][0]['id']
        
        movieId = find_movie_lens_id_fromTMDB_id(tmdbId, links_data)
        
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


def load_links_data():
    df = pd.read_csv("data/ml-latest/links.csv",dtype = {'movieId': str, 'imdbId': str, 'tmdbId': str})
    return df


def find_movie_lens_id_fromTMDB_id(TMDB_id, links_data):
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

def extract_movies_and_locations_from_json_file(file_path, ds_df, movies_df, links_data):
    dataset = json_to_dict(file_path)
    # cnt = 0

    for a in dataset:
        try:
        # if a == 'Amelie':
            df, movies_df = dataframe_with_locations_and_TMDBid(dataset[a], movies_df, links_data)
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


def search_in_ml_latest_by_name(movie_name):
    df = pd.read_csv("data/ml-latest/movies.csv")
    return df[df["title"] == movie_name]


def search_in_ml_hundred_by_id(movie_id):
    df = pd.read_csv('ml-100k/u.item', sep='|', encoding='latin-1', header=None,
                     names=['movie_id', 'title', 'release_date', 'video_release_date', 'IMDb_URL',
                            'unknown', 'Action', 'Adventure', 'Animation', 'Children', 'Comedy', 'Crime',
                            'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery',
                            'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'])
    df.movie_id = df.movie_id.astype(str)
    # print(df[df.movie_id == str(movie_id)])
    return df[df["movie_id"] == str(movie_id)]


def create_X(df):
    """
    Generates a sparse matrix from ratings dataframe.

    Args:
        df: pandas dataframe containing 3 columns (userId, movieId, rating)

    Returns:
        X: sparse matrix
        user_mapper: dict that maps user id's to user indices
        user_inv_mapper: dict that maps user indices to user id's
        movie_mapper: dict that maps movie id's to movie indices
        movie_inv_mapper: dict that maps movie indices to movie id's
    """
    M = df['user_id'].nunique()
    N = df['movie_id'].nunique()

    user_mapper = dict(zip(np.unique(df["user_id"]), list(range(M))))
    movie_mapper = dict(zip(np.unique(df["movie_id"]), list(range(N))))

    user_inv_mapper = dict(zip(list(range(M)), np.unique(df["user_id"])))
    movie_inv_mapper = dict(zip(list(range(N)), np.unique(df["movie_id"])))

    user_index = [user_mapper[i] for i in df['user_id']]
    item_index = [movie_mapper[i] for i in df['movie_id']]

    X = csr_matrix((df["rating"], (user_index,item_index)), shape=(M,N))

    return X, user_mapper, movie_mapper, user_inv_mapper, movie_inv_mapper


def give_me_data():
    # Load the datase
    ratings = pd.read_csv('ml-100k/u.data', sep='\t', names=['user_id', 'item_id', 'rating', 'timestamp'])
    # Load the movies dataset with appropriate column names
    movies = pd.read_csv('ml-100k/u.item', sep='|', encoding='latin-1', header=None,
                        names=['movie_id', 'title', 'release_date', 'video_release_date', 'IMDb_URL',
                                'unknown', 'Action', 'Adventure', 'Animation', 'Children', 'Comedy', 'Crime',
                                'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery',
                                'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'])
    
    movie_titles = dict(zip(movies['movie_id'], movies['title']))

    data = pd.merge(ratings, movies, left_on='item_id', right_on='movie_id')

    data['same_ids'] = data['item_id'] == data['movie_id']

    # Check if all rows have the same values
    all_same_values = data['same_ids'].all()

    data.drop(columns=['same_ids'], inplace=True)

    data.drop(columns=['item_id'], inplace=True)

# Reorder columns to place 'movie_id' at the third position
    columns_order = [data.columns[0], 'movie_id'] + [col for col in data.columns if col not in ['movie_id', data.columns[0]]]
    data = data[columns_order]

    return data, movie_titles

def load_locations_csv():
    locations = pd.read_csv("string_locations.csv")
    locations.columns = ['movieId','imgUrl','tags','address']
    return locations


def search_in_ml_hundred_by_name(movie_name):
    df = pd.read_csv('ml-100k/u.item', sep='|', encoding='latin-1', header=None,
                     names=['movie_id', 'title', 'release_date', 'video_release_date', 'IMDb_URL',
                            'unknown', 'Action', 'Adventure', 'Animation', 'Children', 'Comedy', 'Crime',
                            'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery',
                            'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'])
    df.movie_id = df.movie_id.astype(str)
    return df[df["title"] == movie_name]


def search_in_ml_latest_by_id(movie_id):
    df = pd.read_csv("data/ml-latest/movies.csv")
    print(df)
    return df[df["movieId"] == str(movie_id)]

def give_me_n_cold_start_movies(n=15):
    df = pd.read_csv("ml-100k-cleaned/cold_start_movies.csv")
    return df.head(n)["movieId"].values
