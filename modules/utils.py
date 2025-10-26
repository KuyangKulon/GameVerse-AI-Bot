import requests
from currency_converter import CurrencyConverter

converter = CurrencyConverter()

# 💰 Konversi harga USD → IDR
def usd_to_idr(usd_price):
    try:
        return int(converter.convert(float(usd_price), "USD", "IDR"))
    except Exception:
        return int(float(usd_price) * 16000)  # fallback manual

# 🏷️ Format harga biar rapi
def format_price(price_idr):
    return f"Rp{price_idr:,}".replace(",", ".")

# 🕹️ Deteksi platform game berdasarkan nama
def detect_platform(title):
    t = title.lower()
    if "steam" in t:
        return "🔵 Steam"
    elif "epic" in t:
        return "🟣 Epic Games"
    elif "gog" in t:
        return "🟢 GOG"
    else:
        return "🛒 Lainnya"

# 🌐 Cek koneksi internet
def check_connection(url="https://www.google.com"):
    try:
        requests.get(url, timeout=3)
        return True
    except:
        return False

# 🧠 Format teks markdown aman
def safe_md(text):
    return text.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[")

# 💾 Simpan JSON
import json, os
def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_json(path, default=None):
    if not os.path.exists(path):
        return default or {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
