import openai
import json
import regex as re

# Initialize OpenAI API client
client = openai.OpenAI(api_key='sk-proj-PxRpylslPas4pRZUSALzT3BlbkFJwJRGg5P63EFGH9Q0FHYa')


def create_recommendation(location, movies, perimeter=75):
    # Expect a list as input to change to str
    movies_str = ", ".join(movies)

    prompt = f"""
    Based on the user's current location '{location}', preferred movies: '{movies_str}' 
    (Use the preffered movies as matchmaker to understand what kind of genres the user likes to recommend similar movies,
     that are actually shoot in the city stated), 
    recommend 8 movie set locations in exactly the city or perimeter of {perimeter} kilometer of the city.
    The output should be in JSON format and include the following details:
    - movie name
    - year
    - genres
    - main actors
    - IMDb URL
    - city/country
    - area/street
    - location
    - longitude/latitude
    - description of the movie
    - Description of the scene that played at the scene

    Format the output in JSON as follows:
    [
    {{
        "movie_name": "Movie Name",
        "year": "Year",
        "genres": ["Genre1", "Genre2"],
        "main_actors": ["Actor1", "Actor2"],
        "imdb_url": "https://www.imdb.com/title/ttXXXXXXX/",
        "city_country": "City, Country",
        "area_street": "Area/Street",
        "location": "Specific Location",
        "longitude_latitude": "Longitude, Latitude",
        "movie_description": "Description",
        "locationRef": "Description"
    }}
    ...
    {{
        "movie_name": "Movie Name",
        "year": "Year",
        "genres": ["Genre1", "Genre2"],
        "main_actors": ["Actor1", "Actor2"],
        "imdb_url": "https://www.imdb.com/title/ttXXXXXXX/",
        "city_country": "City, Country",
        "area_street": "Area/Street",
        "location": "Specific Location",
        "longitude_latitude": "Longitude, Latitude",
        "movie_description": "Description",
        "locationRef": "Description"
    }}
    ]
    """

    print(prompt)

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        n=1,
        stop=None,
        temperature=0.7
    )

    response = json.loads(completion.choices[0].message.content)

    return response


def main():
    location = "Munich"
    movies = ["Inception", "Top Gun", "Mission Impossible"]
    interests = ["Castles", "Restaurants", "High Society"]
    perimeter = 75
    recommendation = create_recommendation(location, movies, perimeter)

    if recommendation:
        # Print the extracted JSON data
        print("Here are your recommendations in JSON format:")
        print(recommendation)
        print(json.dumps(recommendation, indent=4))
    else:
        print("Failed to generate recommendations")


if __name__ == "__main__":
    main()