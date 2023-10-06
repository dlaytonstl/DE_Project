import requests
import json
import pandas as pd

class MovieDataFetcher:
    def __init__(self, api_key, bearer_key):
        self.api_key = api_key
        self.bearer_key = bearer_key

    def get_now_playing_movies(self):
        # Construct the URL
        url = "https://api.themoviedb.org/3/movie/now_playing?language=en-US&page=1"

        # Define the headers with the API key
        
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # Send the HTTP GET request
        response = requests.get(url, headers=headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            data_about_movies = response.json()
            return data_about_movies
        else:
            print(f"API request failed with status code {response.status_code}")
            return response

    def create_now_playing_dataframe(self):
        movie_data = self.get_now_playing_movies()

        if movie_data is not None:
            # Normalize the JSON data into a DataFrame
            df = pd.json_normalize(movie_data, 'results')
            return df
        else:
            return None
        
        
    def create_tmdb_movie_dataframe(self):
        # Use self.bearer_key instead of bearer_key
        now_playing_url = f'https://api.themoviedb.org/3/movie/now_playing?api_key={self.bearer_key}&language=en-US&page=1'
        response = requests.get(now_playing_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            movie_data = response.json()
            movie_df = pd.DataFrame(columns=["ID", "Title", "Directors", "Overview", "Release Date", "Revenue", "Popularity", "Runtime", "Genres"])

            for movie in movie_data.get("results", []):
                movie_id = movie.get("id")
                movie_details_url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={self.bearer_key}&language=en-US&append_to_response=credits,videos,images'
                movie_details_response = requests.get(movie_details_url)

                if movie_details_response.status_code == 200:
                    movie_details = movie_details_response.json()
                    movie_title = movie_details.get("title")
                    directors = [crew["name"] for crew in movie_details.get("credits", {}).get("crew", []) if crew["job"] == "Director"]
                    overview = movie_details.get("overview")
                    release_date = movie_details.get("release_date")
                    revenue = movie_details.get("revenue")
                    popularity = movie_details.get("popularity")
                    runtime = movie_details.get("runtime")
                    genres = [genre["name"] for genre in movie_details.get("genres", [])]

                    movie_df = movie_df.append({"ID": movie_id,
                                                "Title": movie_title,
                                                "Directors": ', '.join(directors),
                                                "Overview": overview,
                                                "Release Date": release_date,
                                                "Popularity": popularity,
                                                "Revenue": revenue,
                                                "Runtime": runtime,
                                                "Genres": ', '.join(genres)},
                                            ignore_index=True)
                else:
                    print(f"Failed to fetch movie details for movie ID {movie_id}")
        else:
            print(f"API request failed with status code {response.status_code}")

        return movie_df
        
    def create_actor_tmdb_dataframe(self):
        # Step 1: Make an initial API call to get the list of now playing movies
        now_playing_url = f'https://api.themoviedb.org/3/movie/now_playing?api_key={self.bearer_key}&language=en-US&page=1'
        response = requests.get(now_playing_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            movie_data = response.json()
            
            # Step 2: Create an empty DataFrame with columns
            movie_cast_df = pd.DataFrame(columns=["movie_id", "actor_name", "character", "gender", "popularity"])
            
            # Step 3: For each movie, fetch all the information using its ID and append it to the DataFrame
            for movie in movie_data.get("results", []):
                movie_id = movie.get("id")
                
                # Make an API call to fetch all the information about the movie using the movie_id
                movie_cast_url = f'https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={self.bearer_key}'
                movie_cast_response = requests.get(movie_cast_url)
                
                if movie_cast_response.status_code == 200:
                    movie_cast = movie_cast_response.json()
                    
                    movie_cast = movie_cast.get("cast",[])[:5]
                    
                    for actor in movie_cast:
                        # Extract relevant information
                        gender = actor.get("gender")
                        actor_name = actor.get("name")
                        popularity = actor.get("popularity")
                        character = actor.get("character")
                        
                        # Append movie information to the DataFrame
                        movie_cast_df = movie_cast_df.append({"movie_id": movie_id,
                                                    "actor_name": actor_name,
                                                    "character": character,
                                                    "gender": gender,
                                                    "popularity": popularity
                                                    },
                                                ignore_index=True)
                else:
                    print(f"Failed to fetch movie details for movie ID {movie_id}")
        else:
            print(f"API request failed with status code {response.status_code}")

        # Display the DataFrame
        return movie_cast_df
        
        
        
        

if __name__ == "__main__":
    # Replace 'YOUR_API_KEY' with your actual API key
    api_key = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI0ZGMwNzhkM2QxZTkzOGI0NzMyMWExOTY3M2E3MWI1NSIsInN1YiI6IjYzY2IwYzBjZWEzOTQ5MDA5NjlkYjg3ZiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.ofMNS0JTGVIWpDBugAh5hJ-0514dmVehfpDkVLidBHQ"
    bearer_key = "4dc078d3d1e938b47321a19673a71b55"
    # Create an instance of the MovieDataFetcher class
    movie_fetcher = MovieDataFetcher(api_key, bearer_key)

    now_playing_df = movie_fetcher.create_now_playing_dataframe()
    movie_info = movie_fetcher.create_tmdb_movie_dataframe()
    actor_info = movie_fetcher.create_actor_tmdb_dataframe()

    if now_playing_df is not None:
        # Print or use the DataFrame as needed
        print(now_playing_df)
        print(movie_info)
        print(actor_info)
        