import json, os, requests
from datetime import datetime

TRACK_FILE = "tracked_games.json"

def add_to_watchlist(user_id, game_name):
    if not os.path.exists(TRACK_FILE):
        with open(TRACK_FILE, "w") as f:
            json.dump({}, f)

    with open(TRACK_FILE, "r") as f:
        data = json.load(f)

    if str(user_id) not in data:
        data[str(user_id)] = []

    if game_name not in data[str(user_id)]:
        data[str(user_id)].append(game_name)

    with open(TRACK_FILE, "w") as f:
        json.dump(data, f)

    return f"✅ Game '{game_name}' ditambahkan ke daftar pantauan kamu!"
