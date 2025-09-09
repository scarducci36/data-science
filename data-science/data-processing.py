#In this file I will write the code that pulls the API data
# from Spotify, and processes it before storage in the backend (Postgres or SQLite)

import requests 
import base64
import os 
from dotenv import load_dotenv
import json

load_dotenv(dotenv_path=".env")

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
ACCESS_TOKEN = ""
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

print("CLIENT_ID LENGTH: ", len(CLIENT_ID))
print("CLIENT_SECRET lenght: ", len(CLIENT_SECRET))

auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
print("Raw auth string: ", auth_str)
b64_auth_str = base64.b64encode(auth_str.encode()).decode()
print("Base64: ", b64_auth_str)

#Example search: URL searching for artist 
url_token = "https://accounts.spotify.com/api/token"
headers_b64 = {"Authorization": f"Basic {b64_auth_str}", 
               "Content-Type": "application/x-www-form-urlencoded"}

data = {"grant_type": "client_credentials"}

#response = requests.post(url_token,headers=headers_b64, data=data)

#if response.status_code == 200:
#    ACCESS_TOKEN = response.json()["access_token"]
#    print("Access Token: ", ACCESS_TOKEN)

#else:
#    print("Error: ", response.status_code, response.text)

url_1 = "https://api.spotify.com/v1/search"
url_2 = "https://api.spotify.com/v1/search"
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
params_1 = {"q":"Jessica Lea Mayfield", "type" : "artist", "limit": 1}
params_2 = {"q": "Red Hot Chilli Peppers", "type": "artist", "limit":1}
response_1 = requests.get(url_1, headers=headers, params=params_1)
response_2 = requests.get(url_2, headers=headers, params=params_2)

print("URL1 after requests library configures GET request: ", url_1); 
print("URL2 after requests library configures GET request: ", url_2); 


if response_1.status_code == 200:
    data = response_1.json()

    print(json.dumps(data, indent=2))
    artist = data['artists']['items'][0]

    print("Name: ", artist['name'])
    print("ID: ", artist["id"])
    print("Popularity: ", artist['popularity'])
    print("Followers: ", artist['followers']['total'])

else:
    print("Error: ", response_1.status_code, response_1.text)

if response_2.status_code == 200:
    data = response_2.json()

    print(json.dumps(data, indent=2))
    artist = data['artists']['items'][0]

    print("Name: ", artist['name'])
    print("ID: ", artist["id"])
    print("Popularity: ", artist['popularity'])
    print("Followers: ", artist['followers']['total'])
    print("Genres: ", artist['genres'][:])

else:
    print("Error: ", response_2.status_code, response_1.text)