import requests
from currency_converter import CurrencyConverter
from modules.semantic_search import find_best_match


# 🔗 Ambil link langsung ke Steam
def get_steam_link(nama_game):
    try:
        url = f"https://store.steampowered.com/api/storesearch/?term={nama_game}&cc=ID&l=english"
        data = requests.get(url, timeout=10).json()
        if data.get("items"):
            appid = data["items"][0]["id"]
            return f"https://store.steampowered.com/app/{appid}/"
    except:
        pass
    return None


# 💰 Ambil harga game utama (base game)
def get_game_price(nama_game):
    try:
        url = f"https://www.cheapshark.com/api/1.0/deals?title={nama_game}&pageSize=40"
        response = requests.get(url, timeout=10)
        data = response.json()

        if not data:
            return f"❌ Tidak ditemukan hasil untuk '{nama_game}'."

        c = CurrencyConverter()
        hasil = [f"🎮 *Hasil pencarian untuk* '{nama_game}':\n"]

        # Ambil daftar toko dari CheapShark
        store_info = requests.get("https://www.cheapshark.com/api/1.0/stores").json()
        store_lookup = {s["storeID"]: s["storeName"] for s in store_info}

        allowed_stores = {"Steam", "Epic Games Store", "GOG"}
        emoji_platform = {"Steam": "🔵", "Epic Games Store": "🟣", "GOG": "🟢"}

        # 🔎 Filter hanya base game
        base_games = []
        for game in data:
            title = game.get("title", "").lower()
            if any(kata in title for kata in ["dlc", "soundtrack", "bundle", "expansion", "pack"]):
                continue
            base_games.append(game)

        if not base_games:
            return "⚠️ Tidak ada base game ditemukan (mungkin hanya DLC)."

        # 🧠 Cari nama yang paling mirip
        candidates = [g.get("title", "") for g in base_games]
        best_match = find_best_match(nama_game, candidates, top_k=1)[0][0]
        data_terpilih = [g for g in base_games if g.get("title") == best_match]

        games = []
        for game in data_terpilih:
            store_id = game.get("storeID", "?")
            store_name = store_lookup.get(store_id, f"Store ID {store_id}")
            if store_name not in allowed_stores:
                continue

            title = game.get("title", "Tidak diketahui")
            normal_usd = float(game.get("normalPrice", 0))
            sale_usd = float(game.get("salePrice", normal_usd))
            potongan = float(game.get("savings", 0))

            # 🟢 Kalau toko Steam → ambil harga langsung dari region Indonesia
            if store_name.lower() == "steam":
                steam_url = f"https://store.steampowered.com/api/storesearch/?term={title}&cc=ID&l=english"
                steam_data = requests.get(steam_url, timeout=10).json()

                if steam_data.get("items"):
                    item = steam_data["items"][0]
                    price_info = item.get("price", {})
                    price_idr = price_info.get("final", 0) / 100
                    if price_idr > 0:
                        games.append({
                            "store": "Steam",
                            "title": title,
                            "sale_idr": price_idr,
                            "normal_idr": price_idr,
                            "potongan": 0,
                            "link": f"https://store.steampowered.com/app/{item['id']}/"
                        })
                        continue  # skip CheapShark konversi

            # 🟣 Epic & GOG → tetap pakai data dari CheapShark
            link = f"https://www.cheapshark.com/redirect?dealID={game.get('dealID', '')}"
            games.append({
                "store": store_name,
                "title": title,
                "sale_usd": sale_usd,
                "normal_usd": normal_usd,
                "potongan": potongan,
                "link": link
            })

        if not games:
            return "⚠️ Tidak ditemukan harga dari store yang diizinkan."

        # Urutkan prioritas tampilan (Steam duluan)
        def urutkan_prioritas(g):
            prioritas = {"Steam": 1, "Epic Games Store": 2, "GOG": 3}
            return prioritas.get(g["store"], 99)
        games.sort(key=urutkan_prioritas)

        # Format tampilan hasil
        for i, game in enumerate(games[:5], 1):
            store = game["store"]
            emoji = emoji_platform.get(store, "🛒")

            # 🔹 Harga
            if "sale_idr" in game:
                sale_idr = game["sale_idr"]
                normal_idr = game["normal_idr"]
            else:
                normal_idr = c.convert(game["normal_usd"], 'USD', 'IDR')
                sale_idr = c.convert(game["sale_usd"], 'USD', 'IDR')

            hasil.append(
                f"{i}. {emoji} *{store}*\n"
                f"💰 Rp{sale_idr:,.0f} (dari Rp{normal_idr:,.0f}) -{game.get('potongan', 0):.0f}%\n"
                f"🔗 {game['link']}\n"
            )

        return "\n".join(hasil)

    except Exception as e:
        return f"⚠️ Terjadi error: {str(e)}"


# Handler Telegram
async def handle_price_command(update, context):
    if not context.args:
        await update.message.reply_text("Gunakan: /harga <nama_game>")
        return

    nama_game = " ".join(context.args)
    await update.message.reply_text("🔎 Sedang mencari harga game...")
    hasil = get_game_price(nama_game)
    await update.message.reply_text(hasil, parse_mode="Markdown", disable_web_page_preview=False)
