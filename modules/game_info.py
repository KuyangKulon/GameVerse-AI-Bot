import requests
import re

def get_game_info(game_name):
    # 🔍 Cari game di Steam
    search_url = f"https://store.steampowered.com/api/storesearch/?term={game_name}&cc=us&l=en"
    search_data = requests.get(search_url).json()

    if not search_data.get("items"):
        return f"❌ Game '{game_name}' tidak ditemukan di Steam."

    game = search_data["items"][0]
    app_id = game["id"]

    # 📦 Ambil detail lengkap
    details_url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&cc=id&l=en"
    details_data = requests.get(details_url).json()
    details = details_data.get(str(app_id), {}).get("data")

    if not details:
        return f"⚠️ Gagal mengambil detail untuk '{game_name}'."

    # 🧾 Data utama
    name = details.get("name", "Tidak diketahui")
    developers = ", ".join(details.get("developers", ["Tidak diketahui"]))
    publishers = ", ".join(details.get("publishers", ["Tidak diketahui"]))
    release_date = details.get("release_date", {}).get("date", "Tidak diketahui")
    genres = ", ".join([g["description"] for g in details.get("genres", [])])
    price = details.get("price_overview", {}).get("final_formatted", "Free")
    metacritic = details.get("metacritic", {}).get("score", "N/A")
    short_desc = details.get("short_description", "Tidak ada deskripsi.")
    header = details.get("header_image", "")
    link = f"https://store.steampowered.com/app/{app_id}"

    # 🧰 Ambil spesifikasi PC
    pc_req = details.get("pc_requirements", {})
    min_spec_raw = pc_req.get("minimum", "Tidak ada informasi minimum spesifikasi.")
    rec_spec_raw = pc_req.get("recommended", "Tidak ada informasi rekomendasi spesifikasi.")

    def clean_spec(text):
        """Hapus semua HTML termasuk class bb_ul dan format rapi."""
        text = re.sub(r"<ul.*?>", "", text)  # hapus tag <ul> dengan atribut
        text = re.sub(r"</?li>", "", text)
        text = re.sub(r"<br\s*/?>", "\n", text)  # ubah <br> jadi newline
        text = re.sub(r"</?strong>|</?b>|</?i>|</?p>", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        text = re.sub(r"(OS:|Processor:|Memory:|Graphics:|DirectX:|Storage:|Sound Card:|Additional Notes:)", r"\n\1", text)
        return text.strip()

    min_spec = clean_spec(min_spec_raw)
    rec_spec = clean_spec(rec_spec_raw)

    # 🧩 Format hasil akhir
    result = (
        f"🎮 *{name}*\n\n"
        f"🧑‍💻 Developer: {developers}\n"
        f"🏢 Publisher: {publishers}\n"
        f"📅 Rilis: {release_date}\n"
        f"🕹️ Genre: {genres}\n"
        f"💰 Harga: {price}\n"
        f"⭐ Metacritic: {metacritic}\n\n"
        f"📖 {short_desc}\n\n"
        f"💻 *Minimum Specs:*\n```\n{min_spec}\n```\n"
        f"🚀 *Recommended Specs:*\n```\n{rec_spec}\n```\n"
        f"🔗 [Lihat di Steam]({link})"
    )

    if header:
        result += f"\n🖼️ {header}"

    return result
