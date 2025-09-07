#In this file I will write the code that pulls the API data
# from Spotify, and processes it before storage in the backend (Postgres or SQLite)

import requests 
import base64

CLIENT_ID = "3a2158dfdfee40bda1b696967040373f"
CLIENT_SECRET = "0370afc85f9743a68c0185433208ba40"

auth_str = f"{{CLIENT_ID}: {CLIENT_SECRET}}"
b64_auth_str = base64.b64encode(auth_str.encode()).decode()



ACCESS_TOKEN = ""

#Example search: URL searching for artist 
url_token = "https://accounts.spotify.com/api/token"
headers_b64 = {"Authorization": f"Basic {b64_auth_str}"}
data = {"grant_type": "client_credentials"}

response = requests.post(url_token,headers=headers_b64, data=data)

if response.status_code == 200:
    ACCESS_TOKEN = response.json()["access_token"]
    print("Access Token: ", ACCESS_TOKEN)

else:
    print("Error: ", response.status_code, response.text)

url = "https://api.spotify.com/v1/search"
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
params = {"q":"Jessica Lea Mayfield", "type" : "artist", "limit": 1}
response_1 = requests.get(url, headers=headers, params=params)

print("URL after requests library configures GET request: ", url); 


if response_1.status_code == 200:
    data = response_1.json()
    artist = data['artists']['items'][0]

    print("Name: ", artist['name'])
    print("Popularity: ", artist['popularity'])
    print("Followers: ", artist['followers']['total'])

else:
    print("Error: ", response.status_code, response.text)