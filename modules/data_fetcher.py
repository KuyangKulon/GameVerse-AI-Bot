import requests, json, time

API_KEY = "41a0c6ffb4ab4cb59fecf1adeb5cd9b8"  # ganti dengan API-mu
BASE_URL = "https://api.rawg.io/api/games"
OUTPUT_FILE = "modules/data/games.json"

games = []
page = 1

print("🔄 Mengambil data dari RAWG API...")

while page <= 100:  
    url = f"{BASE_URL}?key={API_KEY}&page={page}&page_size=100"
    r = requests.get(url)
    data = r.json()

    for g in data["results"]:
        # ambil deskripsi detail biar hasilnya akurat
        details = requests.get(f"{BASE_URL}/{g['id']}?key={API_KEY}").json()
        games.append({
            "name": g["name"],
            "released": g.get("released"),
            "rating": g.get("rating"),
            "description_raw": details.get("description_raw", ""),
            "genres": [genre["name"] for genre in g.get("genres", [])],
        })
        time.sleep(1)  # delay biar gak diblokir API

    print(f"✅ Halaman {page} selesai, total {len(games)} game")
    page += 1
    time.sleep(2)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(games, f, indent=2, ensure_ascii=False)

print("🎮 Data berhasil disimpan di:", OUTPUT_FILE)
