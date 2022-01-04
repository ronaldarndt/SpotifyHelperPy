from global_hotkeys import register_hotkeys, stop_checking_hotkeys, start_checking_hotkeys
from time import sleep
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import sys

is_alive = True
redirect_uri = "http://localhost:3030"
scope = " ".join([
 "user-read-currently-playing",
 "user-read-playback-state",
 "user-library-read",
 "playlist-read-private",
 "playlist-modify-private", 
 "playlist-modify-public",
 "playlist-read-collaborative"
])

def exit_application():
    global is_alive
    stop_checking_hotkeys()
    is_alive = False

def close(code = 1, message = None):
    if message != None:
        print(message)

    exit_application()
    exit(code)

def isInPlaylist(sp: spotipy.Spotify, track_id, playlist):
    limit = 100
    offset = 0
    total = playlist["tracks"]["total"]
    playlist_id = playlist["id"]

    while offset < total:
        tracks = sp.playlist_tracks(playlist_id, "items(track(id))", limit=limit, offset=offset)

        for track in tracks["items"]:
            if track["track"]["id"] == track_id:
                return True
        offset += limit

    return False

def addToPlaylist(sp:  spotipy.Spotify, playlist):
    track = sp.current_user_playing_track()["item"]

    if not track or isInPlaylist(sp, track["id"], playlist):
        return

    sp.playlist_add_items(playlist["id"], [track["id"]])

    print("Added " + track["artists"][0]["name"] + " - " + track["name"])

if len(sys.argv) < 4:
    close(message="Usage: playlistify <CLIENT_ID> <CLIENT_SECRET> <PLAYLIST_NAME> [keys = 'ctrl+f1']")

client_id = sys.argv[1]
client_secret = sys.argv[2];
playlist_name = sys.argv[3]

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, scope=scope, redirect_uri=redirect_uri))

playlists = sp.current_user_playlists()["items"]

playlist = next((x for x in playlists if x["name"] == playlist_name), None)

if not playlist:
    close("Playlist '" + playlist_name + "' not found.")

if len(sys.argv) < 5:
    keys = ["control", "f1"]
else:
    keys = sys.argv[4].split("+")

register_hotkeys([[keys, None, lambda: addToPlaylist(sp, playlist)]])

start_checking_hotkeys()

print("Logged in as " + sp.me()["display_name"] + ".")

while is_alive:
        sleep(1)

