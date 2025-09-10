#In this file I will write the code that pulls the API data
# from Spotify, and processes it before storage in the backend (Postgres or SQLite)

import requests 
import base64
import os 
from dotenv import load_dotenv
import json
from flask import Flask
import jsonify 
import sqlite3
import time

#Function Definitions
def refresh_token(url, headers, data):
    return requests.post(url, headers=headers, data=data)

def search_request(url, headers, params):
    return requests.get(url, headers=headers, params=params); 

def save_search(artist):
    #artist = data["artists"]["items"][result_num]
    artist_name = artist['name']
    genres = ", ".join(artist["genres"])
    followers = artist["followers"]["total"]
    popularity = artist["popularity"]
    id = artist["id"]
    search_time = time.time

    connection = sqlite3.connect("spotify_searches.db")
    c = connection.cursor()
    c.execute("INSERT INTO searches (artist_name, genres, followers, popularity, id, search_time) VALUES (?, ?, ?, ?, ?, ?)", 
              (artist_name, genres, followers, popularity, id, search_time))
    connection.commit()
    connection.close()
    return jsonify({"status": "success", "artist": artist_name})

def get_searches():
    connection = sqlite3.connect("spotify_searches.db")
    c = connection.cursor()
    c.execute("SELECT * FROM searches")
    rows = c.fetchall()
    connection.close()
    return jsonify(rows)

#Creating app instance with Flask and locating correct file
app = Flask(__name__)
@app.route('/')
def init_db():
    #Connects to or if does not exist creates file based DB
    connection = sqlite3.connect("spotify_searches.db")
    #Creates cursor object to execute SQL commands
    c = connection.cursor()
    #Create table and define columns 
    c.execute('''CREATE TABLE IF NOT EXISTS searches 
              (id INTEGER PRIMARY KEY AUTOINCREMENT, 
              artist_name TEXT, 
              genres TEXT, 
              followers INT, 
              popularity INT,   
              search_time REAL )''')
    
    connection.commit()
    connection.close()

#Ask User to type in Search Term (This should be converted into a text input connected to html and css)
search_term = input("Enter Search Term...")

load_dotenv(dotenv_path=".env")

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
ACCESS_TOKEN = ""
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

#Building Authorization String to Request Token
auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
b64_auth_str = base64.b64encode(auth_str.encode()).decode()
headers_b64 = {"Authorization": f"Basic {b64_auth_str}", 
               "Content-Type": "application/x-www-form-urlencoded"}
token_req_url = "https://accounts.spotify.com/api/token"
data = {"grant_type": "client_credentials"}

#Building String to Build HTTP Request Queries 
url_1 = "https://api.spotify.com/v1/search"
url_2 = "https://api.spotify.com/v1/search"
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
params = {"q":search_term, "type" : "artist", "limit": 5}
response = search_request(url_1, headers, params)

if response.status_code == 200:

    data = response.json()

    #print(json.dumps(data, indent=2))
    artists = data['artists']['items']
    num = 5
    init_db()
    for i, artist in enumerate(artists[:5]):
        save_search(artist)
        print("Artist ", i+1)
        print("Name: ", artists[i]["name"])
        print("ID: ", artists[i]["id"])
        print("Popularity: ", artists[i]['popularity'])
        print("Followers: ", artists[i]['followers']['total'])
        print("\n")
    get_searches()
else:
    print("Error: Attempting to Refresh Access Token...", response.status_code, response.text)
    response = refresh_token(token_req_url, headers_b64, data)
    if response.status_code == 200:
        ACCESS_TOKEN = response.json()["access_token"]
        print("Access Token: ", ACCESS_TOKEN)
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        response = search_request(url_1, headers, params)

    else:
        print("Error: ", response.status_code, response.text)


