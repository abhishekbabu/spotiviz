import urllib
from urllib.parse import quote
import base64
import requests
import json
import sys

### Client keys
CLIENT = json.load(open('conf.json', 'r+'))
CLIENT_ID = CLIENT['id']
CLIENT_SECRET = CLIENT['secret']

### Authorization URLs
SPOTIFY_ACCOUNTS_BASE_URL = "https://accounts.spotify.com/{}"
SPOTIFY_AUTH_URL = SPOTIFY_ACCOUNTS_BASE_URL.format('authorize')
SPOTIFY_TOKEN_URL = SPOTIFY_ACCOUNTS_BASE_URL.format('api/token')

### API URLs
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

### Server-side parameters
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 5000
REDIRECT_URI = "{}:{}/callback".format(CLIENT_SIDE_URL, PORT)
# REDIRECT_URI = "https://spotivizual.herokuapp.com/callback"
SCOPE = "user-read-private user-read-playback-state user-modify-playback-state user-library-read user-read-recently-played user-top-read"
# STATE = ""
# SHOW_DIALOG_bool = True
# SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    "client_id": CLIENT_ID
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
}

URL_ARGS = "&".join(["{}={}".format(key,urllib.parse.quote(val)) for key, val in auth_query_parameters.items()])
AUTH_URL = "{}/?{}".format(SPOTIFY_AUTH_URL, URL_ARGS)

### User authorization
def authorize(auth_token):
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI
    }

    base64encoded = base64.b64encode("{}:{}".format(CLIENT_ID, CLIENT_SECRET).encode())
    headers = {"Authorization": "Basic {}".format(base64encoded.decode())}
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload, headers=headers)

    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    auth_header = {"Authorization":"Bearer {}".format(access_token)}
    return auth_header

### User profile
USER_PROFILE_ENDPOINT = "{}/me".format(SPOTIFY_API_URL)
def get_user_profile(auth_header):
    user_profile_response = requests.get(USER_PROFILE_ENDPOINT, headers=auth_header)
    return json.loads(user_profile_response.text)

### Recently played tracks
RECENTLY_PLAYED_ENDPOINT = "{}/me/player/recently-played".format(SPOTIFY_API_URL)
def get_recently_played(auth_header):
    recently_played_response = requests.get(RECENTLY_PLAYED_ENDPOINT, headers=auth_header)
    return json.loads(recently_played_response.text)

### Top artists
TOP_ARTISTS_ENDPOINT = "{}/me/top/artists".format(SPOTIFY_API_URL)
def get_top_artists(auth_header, time_range, limit):
    payload = {'time_range': time_range, 'limit': limit }
    top_artists_response = requests.get(TOP_ARTISTS_ENDPOINT, headers=auth_header, params=payload)
    return json.loads(top_artists_response.text)