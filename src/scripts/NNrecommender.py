import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
# from keras.models import Model
# from keras.layers import Input, Embedding, Flatten, Dense, concatenate
# from keras.optimizers import Adam
# from keras.preprocessing.sequence import pad_sequences
# from keras.callbacks import EarlyStopping, ReduceLROnPlateau
# from keras.regularizers import l2
# from keras.callbacks import Callback, ModelCheckpoint
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import MinMaxScaler
# from keras.models import load_model
from tensorflow.keras.models import load_model
import pickle
import matplotlib.pyplot as plt


def save_history(history, filename='training_history.pkl'):
    with open(filename, 'wb') as file:
        pickle.dump(history.history, file)

def load_history(filename='training_history.pkl'):
    with open(filename, 'rb') as file:
        return pickle.load(file)

def save_movie_embeddings(movie_embeddings, filename='movie_embeddings.pkl'):
    with open(filename, 'wb') as file:
        pickle.dump(movie_embeddings, file)

def load_movie_embeddings(filename='movie_embeddings.pkl'):
    with open(filename, 'rb') as file:
        return pickle.load(file)

# Load the dataset
def load_data():
    # Define the column names explicitly
    columns_ratings = ['user_id', 'movie_id', 'rating', 'timestamp']
    # Define the column names explicitly
    columns_movies = ['movie_id', 'title', 'genres']
    # Read the CSV file, specifying the column names and skipping the first row
    ratings = pd.read_csv('src/data/ml-latest/ratings.csv', sep=',', names=columns_ratings, skiprows=1)
    # ratings = pd.read_csv('ml-latest/ratings.csv', sep='\t', names=['user_id', 'movie_id', 'rating', 'timestamp'])
    movies = pd.read_csv('src/data/ml-latest/movies.csv',  sep=',', names=columns_movies, skiprows=1)
    # Keep only the movie_id and title columns
    movies = movies[['movie_id', 'title']]
    return ratings, movies
    
# Standardize the ratings
def standardize_ratings(train_ratings, val_ratings):
    scaler = MinMaxScaler()

    train_ratings['rating'] = scaler.fit_transform(train_ratings[['rating']])
    val_ratings['rating'] = scaler.transform(val_ratings[['rating']])

    return train_ratings, val_ratings, scaler

# Unstandardize the ratings
def unstandardize_ratings(ratings, scaler):
  ratings = np.array(ratings).reshape(-1, 1)
  return scaler.inverse_transform(ratings).flatten()

# Preprocess the data
def preprocess_data(ratings, movies):
    user_ids = ratings['user_id'].unique().tolist()
    user_id_to_index = {x: i for i, x in enumerate(user_ids)}
    movie_ids = ratings['movie_id'].unique().tolist()
    movie_id_to_index = {x: i for i, x in enumerate(movie_ids)}

    ratings['user_id'] = ratings['user_id'].map(user_id_to_index)
    ratings['movie_id'] = ratings['movie_id'].map(movie_id_to_index)

    num_users = len(user_ids)
    num_movies = len(movie_ids)

    return ratings, num_users, num_movies, user_id_to_index, movie_id_to_index

# Generate movie embeddings
def get_movie_embeddings(model, num_movies):
    movie_layer = model.get_layer('movie_embedding')
    print("1")
    movie_weights = movie_layer.get_weights()[0]
    print("2")
    return movie_weights

# Find similar movies using learned embeddings
def find_similar_movies_nn(movie_ids_like, movie_ids_dislike, movie_embeddings, movie_id_to_index, movie_index_to_id,k=10):

    movie_indices_like = [movie_id_to_index[movie_id] for movie_id in movie_ids_like]
    movie_indices_dislike = [movie_id_to_index[movie_id] for movie_id in movie_ids_dislike]

    movie_vecs_like = movie_embeddings[movie_indices_like]
    movie_vecs_dislike = movie_embeddings[movie_indices_dislike]

    avg_movie_vec_like = np.mean(movie_vecs_like, axis=0)

    avg_movie_vec_dislike = np.mean(movie_vecs_dislike, axis=0)

    adjusted_movie_vec = avg_movie_vec_like - 0.5 * (avg_movie_vec_dislike)

    similarities = np.dot(movie_embeddings, adjusted_movie_vec)

    similar_indices = np.argsort(similarities)[::-1]

    similar_movie_ids = [movie_index_to_id[idx] for idx in similar_indices if
                         idx not in movie_indices_like and idx not in movie_indices_dislike][:k]

    return similar_movie_ids


def provide_recommendations_for(movie_ids = [1, 2, 3]):
    ratings, movies = load_data()
    ratings, num_users, num_movies, user_id_to_index, movie_id_to_index = preprocess_data(ratings, movies)
    # print("1")

    movie_index_to_id = {v: k for k, v in movie_id_to_index.items()}
    # print("2")

    # model = build_model(num_users, num_movies)
    model = load_model('best_model_try2.h5', compile=False)
    print("3")
    # history = train_model(model, ratings)

    movie_embeddings = get_movie_embeddings(model, num_movies)
    print("4")
    # Example movie_ids for which to find similar movies
    # movie_ids = [1, 2, 3]  # Example movie IDs liked by the user

    similar_movie_ids = find_similar_movies_nn(movie_ids, movie_embeddings, movie_id_to_index, movie_index_to_id)
    # print(f"Similar movies: {similar_movie_ids}")

    return similar_movie_ids

# provide_recommendations_for()