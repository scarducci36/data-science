#Home Page
#Software Requirements: Search Bar, Search Results, Clickable Search Results (Goes to new page), Other display and clickable images to develop lagter

import requests 
import base64
import os 
from dotenv import load_dotenv
import json
from flask import Flask, request, jsonify, render_template 
import sqlite3
import time

# ---------------------------------------Function Definitions------------------------------------------- #

# Function Description: Takes in URL, header info for HTTP request, and data required for response. 
# Returns either authorization confirmation or new token. 
def refresh_token(url, headers, data):
    return requests.post(url, headers=headers, data=data)

# Function Description: Takes URL, header info for HTTP request, and parameter. 
# Returns search results.
def search_request(url, headers, params):
    return requests.get(url, headers=headers, params=params); 

#Function Description: Takes in the data from the JSON formatted result provided by the HTTP search request 
# and saves the information into the backend of the DB 
# Something to note is that this only applies to Artist Searches and doesn't account for searches that are for Albums, right???
def save_search(data):
    search_time = time.time()
    connection = sqlite3.connect("spotify_searches.db")
    c = connection.cursor()
    i = 1
    if "artists" in data:
        for artist in data['artists']['items']:
            spotify_id = artist['id']
            c.execute('''SELECT id FROM searches WHERE spotify_id = ?''', (spotify_id, ))
            existing = c.fetchone()

            if existing: 
                print(f"Artist '{artist['name']}' already exists, skipping insert into DB")

            else: 
                c.execute("INSERT INTO searches (artist_name, genres, followers, popularity, spotify_id, search_time) VALUES (?, ?, ?, ?, ?, ?)", 
                        (artist['name'], artist['genres'], artist['followers']['total'], artist['popularity'], artist['id'], search_time))
                print("Artist ", i)
                i = i + 1
                print("Name: ", artist["name"])
                print("ID: ", artist["id"])
                print("Popularity: ", artist['popularity'])
                print("Followers: ", artist['followers']['total'])
                print("\n")

                connection.commit()
                connection.close()
                return {"status": "success", "artist": artist['name']}
    elif "albums" in data: 
            j = 1
            for album in data['albums']['items']:
                spotify_id = album['id']
                c.execute('''SELECT id FROM searches WHERE SPOTIFY_IS = ?''', (spotify_id, ))
                existing = c.fetchone()

                if existing: 
                    print(f"Album '{album['name']}' already exists, skipping insert into DB")

                else: 

                    c.execute("INSERT INTO albums (spotify_id, album_name, popularity, image_url, genres, last_updated) VALUES (?, ?, ?, ?, ?, ?)", 
                            (album['name'], album['id'], album['popularity'], album['images']['url'], album['genres'], search_time))
                    c.execute("")
                    print("Album ", j)
                    j = j+1
                    print("Album Name: ", album['name'])
                    print("Album Popularity: ", album['popularity'])
                    print("Genres: ", album['genres'])
                    print("\n")

                    connection.commit()
                    connection.close()
                    return {"status": "success", "album": album['name']}
        
    connection.commit()
    connection.close()
    return {"status": "success", "artist": artist['name']}

# Function Definition: Function takes in no arguments (getter), prints the results of the searches table
# and returns the results object
def get_searches():
    connection = sqlite3.connect("spotify_searches.db")
    connection.row_factory = sqlite3.Row
    c = connection.cursor()
    c.execute("SELECT * FROM searches")
    rows = c.fetchall()
    connection.close()

    results = [dict(row) for row in rows]
    print(json.dumps(results, indent=2))

# Function Description: This function is executed once when the user visits the website. 
# It takes in no arguments and returns either nothings or throws an exception describing the error
# It will create a file based SQLite DB if it does not already exist
# Within the DataBase exists four tables, the Artist Table, the Tracks Table, the Search History Table, and the Searches Table (Users Table Needed)
def init_db():
    connection = sqlite3.connect("spotify_searches.db")     # Create Connection
    c = connection.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS artists (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              spotify_id TEXT, 
              artist_name TEXT, 
              genres TEXT, 
              image_url TEXT, 
              followers INT, 
              popularity INT, 
              last_updated TIMESTAMP 
              ) ''')                                        # ^ Artist Table - Primary Key => id
    
    c.execute(''' CREATE TABLE IF NOT EXISTS albums (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              spotify_id TEXT, 
              album_name TEXT, 
              popularity TEXT, 
              image_url TEXT,
              genres TEXT, 
              artist_spotify_id TEXT, 
              last_updated TIMESTAMP
              )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS tracks (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              spotify_id TEXT, 
              artist_name TEXT,
              album_name TEXT, 
              artist_spotify_id TEXT,
              track_name TEXT, 
              image_url TEXT, 
              preview_url TEXT, 
              popularity INT,
              last_updated TIMESTAMP
              ) ''')                                        # ^ Track Table - Primary Key => id, Foreign Key => artist_name

    c.execute('''CREATE TABLE IF NOT EXISTS searches        
              (id INTEGER PRIMARY KEY AUTOINCREMENT, 
              query TEXT, 
              spotify_id TEXT,
              result_name TEXT,   
              search_time REAL
              artist_spotify_id TEXT )''')                        # ^ Searches Table
    
    connection.commit()

    c.execute("SELECT * FROM searches")
    rows = c.fetchall()
    connection.close()
    print(json.dumps(rows, indent=2))
    connection.close()

# Function Description: Function takes in user text and uses it as a search term in an SQLite search 
# Search is conducted by an INNER JOIN operation, joining multilple tables to find a result 
# Function returns the results in row form* 
def query_db(text):
    connection = sqlite3.connect("spotify_searches.db")
    connection.row_factory = sqlite3.Row
    c = connection.cursor()

    SQL = '''SELECT artists.artist_name, artists.genres, albums.album_name
             FROM albums
             JOIN artists ON albums.artist_spotify_id = artists.spotify_id 
             WHERE lower(artists.artist_name) LIKE ? 
             OR lower(artists.genres) LIKE ?
             OR lower(albums.album_name) LIKE ?'''
    
    search_term = f"%{text.lower()}%"
    c.execute(SQL, (search_term, search_term, search_term))
    rows = c.fetchall()

    if rows: 
        connection.close()
        return rows
    else:
        ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
        #Set up HTTP call requirements
        #Building String to Build HTTP Request Queries 
        url_artist = "https://api.spotify.com/v1/search"
        #url_album = "https://api.spotify.com/v1/albums"
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        params_artist = {"q":text, "type" : "artist", "limit": 5}
        #params_album = {"q":text, "type" : "album", "limit": 5}
        response = search_request(url_artist, headers, params_artist)
        #response_album = search_request_album(url_album, headers, params_album)

        if response.status_code == 200:

            data = response.json()
            #print(json.dumps(data, indent=2))
            save_search(data)
            get_searches()
                
        else:
            print("Error: Attempting to Refresh Access Token...", response.status_code, response.text)
            response = refresh_token(token_req_url, headers_b64, data)
            if response.status_code == 200:
                ACCESS_TOKEN = response.json()["access_token"]
                print("Access Token: ", ACCESS_TOKEN)
                headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
                response = search_request(url_artist, headers, params_artist)

            else:
                print("Error: ", response.status_code, response.text)
# ----------------------------------------End of Function Definitions---------------------------------------------- #

init_db()                           # Before we even create an instance of the app, we can check on the database

load_dotenv(dotenv_path=".env")     # Make sure that the path of the .env file is known so we can access private local variables 

CLIENT_ID = os.getenv("CLIENT_ID")  
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
ACCESS_TOKEN = ""
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"                       # Build Authorization String to Request Authorization Token (If needed)
b64_auth_str = base64.b64encode(auth_str.encode()).decode()
headers_b64 = {"Authorization": f"Basic {b64_auth_str}", 
               "Content-Type": "application/x-www-form-urlencoded"}
token_req_url = "https://accounts.spotify.com/api/token"
data = {"grant_type": "client_credentials"}

test_auth_url = "https://api.spotify.com/v1/search"             # Build Test Authorization HTTP Request
test = "0"
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
params = {"q":test, "type" : "artist", "limit": 1}              #This should be partly user input
response = search_request(test_auth_url, headers, params)

if response.status_code == 200:

    data = response.json()                 #No need to save this because it is just a test for authorization
    #print(json.dumps(data, indent=2))
    print("Authorization Successful.")

    #Prompt user for search here?
else:
    print("Access Denied: Attempting to Refresh Access Token...", response.status_code, response.text)
    response = refresh_token(token_req_url, headers_b64, data)
    if response.status_code == 200:
        ACCESS_TOKEN = response.json()["access_token"]
        print("Access Token: ", ACCESS_TOKEN)

    else:
        print("Error: ", response.status_code, response.text)

# Creating app instance with Flask and locating correct file. This will display the home page
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=["GET", "POST"])
def search(): 
    query=""
    results = []

    if request.method == 'POST':
        query = request.form.get('query', '')
    elif request.method == 'GET':
        query = request.args.get('query', '')

    if query: 
        results = query_db(query)


    return render_template('search_results.html', query=query, results=results)

if __name__ == '__main__':
    app.run(debug=True)