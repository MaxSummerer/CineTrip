# cineTrip
Discover a whole new way to plan your travels with CineTrip, the innovative web-app that curates personalized tour trips based on your location and favorite movies. Whether you're a film buff dreaming of visiting iconic movie locations or an adventurer looking to explore destinations inspired by your beloved films, CineTrip has got you covered.
## project and codebase setup
refer to insatllation guide

## project structure
group07
├── MovieRecommender.ipynb 
├── README.md
├── RecommenderNN.ipynb
├── best_model_try2.h5
├── installation guide
├── main.py
├── pages
│   ├── python files for each UI page
├── requirements.txt
├── src
│   ├── README.md
│   ├── data (hosts all the data used in the application)
│   │   ├── cities
│   │   │   ├── cities and countries in JSON format
│   │   ├── cold_start_movies.csv
│   │   ├── dowloads.txt
│   │   ├── img
│   │   │   ├── Images being used in the project
│   │   ├── locations-json
│   │   │   ├── locations dataset in json files
│   │   ├── ml-100k
│   │   │   ├── ML 100k dataset used for initital developent and model exploration
│   │   ├── ml-100k-cleaned
│   │   │   ├── files kept for backward compatability
│   │   ├── ml-latest
│   │   │   ├── Latest and the biggest MovieLens dataset
│   │   ├── movie_embeddings.npy
│   │   ├── movies_added.csv
│   │   ├── semi_structured_locations.csv
│   │   └── string_locations.csv
│   ├── models
│   └── scripts
│       ├── utlity, batch and notebook files used during the whole timeline