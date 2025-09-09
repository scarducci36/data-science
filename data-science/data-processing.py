#In this file I will write the code that pulls the API data
# from Spotify, and processes it before storage in the backend (Postgres or SQLite)

import requests 
import base64
import os 
from dotenv import load_dotenv
import json


def refresh_token(url, headers, data):
    return requests.post(url, headers=headers, data=data)

def search_request(url, headers, params):
    return requests.get(url, headers=headers, params=params); 

#Ask User to type in Search Term 
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
params_1 = {"q":search_term, "type" : "artist", "limit": 5}
params_2 = {"q": "Red Hot Chilli Peppers", "type": "artist", "limit":1}
response_1 = search_request(url_1, headers, params_1)
response_2 = search_request(url_2, headers, params_2)

if response_1.status_code == 200:

    data = response_1.json()

    print(json.dumps(data, indent=2))
    artists = data['artists']['items']

    for i in artists:
        print("Name: ", artists['name'][i])
        print("ID: ", artists["id"][i])
        print("Popularity: ", artists['popularity'][i])
        print("Followers: ", artists['followers']['total'][i])

else:
    print("Error: Attempting to Refresh Access Token...", response_1.status_code, response_1.text)
    response = refresh_token(token_req_url, headers_b64, data)
    if response.status_code == 200:
        ACCESS_TOKEN = response.json()["access_token"]
        print("Access Token: ", ACCESS_TOKEN)
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        response_1 = search_request(url_1, headers, params_1)

    else:
        print("Error: ", response.status_code, response.text)


