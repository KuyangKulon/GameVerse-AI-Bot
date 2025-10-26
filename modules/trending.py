import requests
import time

def format_rupiah(value):
    return "Rp{:,.0f}".format(value).replace(",", ".")

def get_price_from_appid(appid):
    """Ambil harga game yang benar-benar dari region Indonesia."""
    try:
        url = f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=ID&l=indonesian"
        data = requests.get(url, timeout=10).json()
        app_data = data[str(appid)]["data"]

        price_info = app_data.get("price_overview")
        if not price_info:
            return "💰 Gratis / Belum tersedia"

        final_price = price_info["final"] / 100
        initial_price = price_info["initial"] / 100
        discount = price_info["discount_percent"]

        if discount > 0:
            return f"💰 {format_rupiah(final_price)} (Diskon {discount}% dari {format_rupiah(initial_price)})"
        else:
            return f"💰 {format_rupiah(final_price)}"
    except:
        return "💰 Belum tersedia"

def get_trending_games():
    """Ambil daftar game trending Steam (region Indonesia, harga asli)."""
    try:
        url = "https://store.steampowered.com/api/featuredcategories/?cc=ID&l=indonesian"
        data = requests.get(url, timeout=10).json()
        top_sellers = data.get("top_sellers", {}).get("items", [])[:10]

        if not top_sellers:
            return "⚠️ Tidak ada data trending ditemukan."

        result = ["🔥 *Trending Games di Steam (Top Sellers)*:\n"]

        for i, game in enumerate(top_sellers, 1):
            name = game.get("name", "Tidak diketahui")
            appid = game.get("id")
            link = f"https://store.steampowered.com/app/{appid}/"

            harga_str = get_price_from_appid(appid)
            result.append(f"{i}. 🎮 *{name}*\n{harga_str}\n🔗 {link}\n")

            time.sleep(0.4)  # jeda biar ga rate-limit

        return "\n".join(result)
    except Exception as e:
        return f"⚠️ Gagal mengambil data trending: {e}"
