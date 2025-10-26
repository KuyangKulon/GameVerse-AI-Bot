import requests
import feedparser
from transformers import pipeline
from datetime import datetime, timedelta
from currency_converter import CurrencyConverter

# Summarizer pakai CPU
summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device_map=None)
c = CurrencyConverter()

# 🗓️ Ambil game yang akan rilis (RAWG.io)
def get_upcoming_games():
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        next_month = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        url = f"https://api.rawg.io/api/games?key=41a0c6ffb4ab4cb59fecf1adeb5cd9b8&dates={today},{next_month}&ordering=released&page_size=5"
        response = requests.get(url, timeout=10)
        data = response.json().get("results", [])

        if not data:
            return "⚠️ Tidak ada game yang akan rilis dalam waktu dekat."

        hasil = ["🗓️ *Upcoming Game Releases (30 hari ke depan)*:\n"]
        for game in data:
            name = game["name"]
            release_date = game.get("released", "TBA")
            platforms = ", ".join([p["platform"]["name"] for p in game.get("platforms", []) if "platform" in p])
            link = f"https://rawg.io/games/{game['slug']}"
            hasil.append(f"🎮 *{name}*\n📅 Rilis: {release_date}\n🕹️ Platform: {platforms}\n🔗 {link}\n")

        return "\n".join(hasil)
    except Exception as e:
        return f"⚠️ Error ambil upcoming games: {e}"

# 🔥 Ambil game trending di Steam
def get_trending_steam_games():
    try:
        url = "https://store.steampowered.com/api/featuredcategories/"
        response = requests.get(url, timeout=10).json()
        top_sellers = response.get("top_sellers", {}).get("items", [])

        hasil = ["🔥 *Trending Games di Steam (Top Sellers)*:\n"]
        for i, game in enumerate(top_sellers[:5], 1):
            name = game["name"]
            price_usd = game.get("final_price", 0) / 100
            price_idr = c.convert(price_usd, 'USD', 'IDR')
            link = f"https://store.steampowered.com/app/{game['id']}/"
            hasil.append(f"{i}. 🎮 *{name}*\n💰 Rp{price_idr:,.0f}\n🔗 {link}\n")

        return "\n".join(hasil)
    except Exception as e:
        return f"⚠️ Error ambil trending Steam: {e}"

# 💸 Game diskon besar (CheapShark)
def get_discounted_games():
    try:
        url = "https://www.cheapshark.com/api/1.0/deals?pageSize=20&sortBy=Savings"
        data = requests.get(url, timeout=10).json()

        if not data:
            return "⚠️ Tidak ada data diskon ditemukan."

        hasil = ["💸 *Game Dengan Diskon Tertinggi Saat Ini:*\n"]

        # 🚫 Daftar kata yang menandakan bukan game
        non_game_keywords = [
            "bundle", "pack", "software", "course", "unity", "unreal", "learn",
            "edition", "toolkit", "dev", "development", "project", "asset", "license", "manga", "comic"
        ]

        count = 0
        for game in data:
            title = game.get("title", "Tidak diketahui")

            # 🧩 Skip kalau bukan game
            if any(word in title.lower() for word in non_game_keywords):
                continue

            normal_usd = float(game.get("normalPrice", 0))
            sale_usd = float(game.get("salePrice", normal_usd))
            potongan = float(game.get("savings", 0))
            link = f"https://www.cheapshark.com/redirect?dealID={game.get('dealID', '')}"

            sale_idr = c.convert(sale_usd, 'USD', 'IDR')
            normal_idr = c.convert(normal_usd, 'USD', 'IDR')

            hasil.append(
                f"{count+1}. 🎮 *{title}*\n💰 Rp{sale_idr:,.0f} (dari Rp{normal_idr:,.0f}) -{potongan:.0f}%\n🔗 {link}\n"
            )
            count += 1

            if count >= 5:
                break  # hanya tampilkan 5 game

        if count == 0:
            return "⚠️ Tidak ada game yang sedang diskon besar saat ini."

        return "\n".join(hasil)

    except Exception as e:
        return f"⚠️ Error ambil diskon: {e}"


# 📰 Berita Game dari Gamespot
def get_latest_game_news():
    try:
        # 📰 Gunakan beberapa sumber berita game
        feeds = [
            "https://www.gamespot.com/feeds/news/",
            "https://www.ign.com/rss",
            "https://www.pcgamer.com/rss/",
        ]

        news_list = []

        # ✅ Kata yang menunjukkan berita game
        allowed_keywords = [
            "update", "patch", "dlc", "trailer", "expansion", "release",
            "game", "event", "season", "developer", "studio"
        ]

        # 🚫 Kata yang sering muncul di non-game news
        blocked_keywords = [
            "board", "card", "toy", "lego", "hardware", "device",
            "console", "cpu", "gpu", "bundle", "peripheral", "controller",
            "headset", "keyboard", "mouse", "chair"
        ]

        for feed_url in feeds:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:15]:
                title_lower = entry.title.lower()
                summary_lower = entry.get("summary", "").lower()

                # Filter: harus mengandung minimal satu kata yang "game-related"
                if not any(word in title_lower or word in summary_lower for word in allowed_keywords):
                    continue

                # Filter: buang berita yang tentang hardware, board game, dll
                if any(word in title_lower or word in summary_lower for word in blocked_keywords):
                    continue

                # Ringkas berita pakai summarizer
                try:
                    summary = summarizer(entry.summary, max_length=60, min_length=25, do_sample=False)[0]['summary_text']
                except Exception:
                    summary = entry.summary[:200]

                news_list.append(f"📰 *{entry.title}*\n{summary}\n🔗 {entry.link}")

        if not news_list:
            return "⚠️ Tidak ada berita game terbaru yang relevan."

        return "🗞️ *Berita Game Terkini:*\n\n" + "\n\n".join(news_list[:5])

    except Exception as e:
        return f"⚠️ Error ambil berita: {e}"


# 🚀 Gabungkan semua ke satu fungsi utama
def get_game_news():
    try:
        trending = get_trending_steam_games()
        upcoming = get_upcoming_games()
        discounted = get_discounted_games()
        latest_news = get_latest_game_news()

        return f"{trending}\n\n{upcoming}\n\n{discounted}\n\n{latest_news}"
    except Exception as e:
        return f"⚠️ Error saat membuat laporan berita: {e}"
