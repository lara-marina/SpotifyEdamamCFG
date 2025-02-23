import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import os
from dotenv import load_dotenv

#load environment variables
load_dotenv("C:\\Users\\laram\\PycharmProjects\\pythonProject\\.env") # this was a ball ache to understand

print(os.getenv("spotify_client_id"))

#spotify api credentials
spotify_client_id = os.getenv("spotify_client_id")
spotify_client_secret = os.getenv("spotify_client_secret")
spotify_redirect_uri = "http://localhost:8080/callback" # for local testing

# Edamam API credentials
edamam_app_id = os.getenv("edamam_app_id")
edamam_app_key = os.getenv("edamam_app_key")

#debug
print(f"Spotify Client ID: {spotify_client_id}")
print(f"Spotify Client Secret: {spotify_client_secret}")
print(f"Edamam App ID: {edamam_app_id}")
print(f"Edamam App Key: {edamam_app_key}")

#map genres to recipe themes
genre_to_recipe = {
    'pop': 'dessert',
    'rock': 'BBQ',
    'classical': 'gourmet',
    'jazz': 'appetizers',
    'electronic': 'cocktails',
    'techno': 'cocktails',
    'country': 'american',
    'reggae': 'jamaican',
    'reggaeton': 'latin',
    'experimental': 'fusion'
}

# authenticate with spotify
def authenticate_spotify():
    scope = "user-library-read"  # Specify required scopes
    auth_manager = SpotifyOAuth(
        client_id=spotify_client_id,
        client_secret=spotify_client_secret,
        redirect_uri=spotify_redirect_uri,
        scope=scope,
        show_dialog=True  # Forces the user to log in every time
    )
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    print("Successfully logged in to Spotify!")
    return spotify


# fetch songs from spotify
def fetch_songs(spotify, genre):
    print(f"Fetching songs for genre: {genre}")
    user_songs = []

    try:
        # Step 1: Fetch user's saved tracks
        results = spotify.current_user_saved_tracks(limit=50)  # Fetch user's saved tracks (adjust limit as needed)
        for item in results['items']:
            track = item['track']
            track_name = track['name']
            artist_name = track['artists'][0]['name']
            track_url = track['external_urls']['spotify']
            # Check if the track matches the genre (tracks don't have  genres, so we check artists)
            artist_id = track['artists'][0]['id']
            artist_info = spotify.artist(artist_id)
            if 'genres' in artist_info and genre in artist_info['genres']:
                user_songs.append(f"{track_name} by {artist_name}, {track_url}")
            if len(user_songs) >= 10:
                break

        # Step 2: If no matches in user's individual library, fetch most popular songs in genre
        if not user_songs:
            print("No matching songs in your Spotify library. Fetching most popular songs.")
            results = spotify.search(q=f'genre:{genre}', type='track', limit=10)
            for item in results['tracks']['items']:
                track_name = item['name']
                artist_name = item['artists'][0]['name']
                track_url = item['external_urls']['spotify']
                user_songs.append(f"{track_name} by {artist_name}, {track_url}")
    except Exception as e:
        print(f"Error fetching songs: {e}")

    return user_songs


def fetch_recipes(recipe_theme):
    print(f"Fetching recipes for theme: {recipe_theme}")
    url = f"https://api.edamam.com/search?q={recipe_theme}&app_id={edamam_app_id}&app_key={edamam_app_key}"
    headers = {
        "Edamam-Account-User": "your_user_id_here"  # Replace with your Edamam user ID
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return [{"label": hit["recipe"]["label"], "url": hit["recipe"]["url"]} for hit in data['hits'][:5]]  # return top 5 recipes
    else:
        print("Error fetching recipes:", response.status_code, response.json())
        return []


# Main program
def main ():
    spotify = authenticate_spotify()
    print("Available genres:", ", ".join(genre_to_recipe.keys()))
    genre = input("select a genre: ").lower()

    if genre not in genre_to_recipe:
        print("Invalid genre. Please try again.")
        return

    # fetch songs
    songs = fetch_songs(spotify, genre)
    print(f"\nTop 10 {genre} Songs:")
    for song in songs:
        print(f"- {song}" )

    # Fetch recipes
    recipe_theme = genre_to_recipe[genre]
    recipes = fetch_recipes(recipe_theme)
    print(f"\nTop 5 {recipe_theme} Recipes:")
    for recipe in recipes:
        print(f"- {recipe['label']} ({recipe['url']})")

if __name__ == "__main__":
    main()
