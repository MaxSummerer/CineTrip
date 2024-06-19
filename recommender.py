from sklearn.neighbors import NearestNeighbors
import numpy as np

class MovieRecommender:
    def __init__(self, X, movie_titles, movie_mapper, movie_inv_mapper):
        self.X = X.T  # Transpose here once instead of in each call
        self.movie_titles = movie_titles
        self.movie_mapper = movie_mapper
        self.movie_inv_mapper = movie_inv_mapper

    def find_similar_movies(movie_ids, movie_titles, X, movie_mapper, movie_inv_mapper, k, metric='cosine'):
        """
        Finds k-nearest neighbours for a given list of movie ids.

        Args:
            movie_ids: list of ids of the movies of interest
            X: user-item utility matrix
            k: number of similar movies to retrieve
            metric: distance metric for kNN calculations

        Output: returns list of k similar movie IDs
        """
        X = X.T
        neighbour_ids = []
        movie_title = []
        movie_rec = []

        # Convert to dense format if X is sparse
        if hasattr(X, "toarray"):
            X = X.toarray()

        # Get the vectors for each movie ID
        movie_indices = [movie_mapper[movie_id] for movie_id in movie_ids]
        movie_vecs = [X[movie_ind] for movie_ind in movie_indices]

        # Compute the average vector
        avg_movie_vec = np.mean(movie_vecs, axis=0).reshape(1, -1)

        # use k+1 since kNN output includes the movieId of interest
        kNN = NearestNeighbors(n_neighbors=k+len(movie_ids), algorithm="brute", metric=metric)
        kNN.fit(X)
        neighbours = kNN.kneighbors(avg_movie_vec, return_distance=False).flatten()

        # Extract movie IDs, ignoring the input movie IDs
        for neighbour in neighbours:
            if len(neighbour_ids) >= k:
                break
            if movie_inv_mapper[neighbour] not in movie_ids:
                neighbour_ids.append(movie_inv_mapper[neighbour])

        ## This part might need some modification when merged with UI.
        # Display what Movies are liked:
        for i in movie_ids:
            movie_title.append(movie_titles[i])
        print(f"Because you liked {', '.join(movie_title)}:")
        
        # Display what Movies are recommended
        for i in neighbour_ids:
            movie_rec.append(movie_titles[i])
        print(f"We recommend {', '.join(movie_rec)}:")
        return neighbour_ids


    def filter_dataframe(df, movie_ids, location=None):
        '''
        df: pd dataframe
        movie_ids: list
        location: str

        Output:
        Filtered dataframe df including
        [movie_id, location_url, location_ref, city/country, area/street, location]
        '''
        # Filter based on movie_ids
        filtered_df = df[df['movieId'].isin(movie_ids)]

        # Filter based on location if provided
        if location is not None:
            location_filtered_df = filtered_df[filtered_df['city/country'] == location]
            # If no matching location is found, show all locations of the filtered DataFrame
            if location_filtered_df.empty:
                print(f"No matching location found for '{location}'. Showing all locations.")
                return filtered_df
            else:
                return location_filtered_df

        return filtered_df