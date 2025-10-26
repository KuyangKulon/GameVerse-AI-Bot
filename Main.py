# ============================================
# main.py — Program utama GameVerse AI Bot
# ============================================

import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from modules import (
    price_watcher,
    tracker,
    news_fetcher,
    recommender,
    trending,
    game_info,
    utils,
    currency_tool,
)
from modules.semantic_search import find_best_match

# ============================================
# Bagian 1: Fungsi-fungsi untuk setiap command
# ============================================

# /start → Pesan pembuka
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 Selamat datang di *GameVerse AI Bot!*\n\n"
        "🕹️ Berikut perintah yang bisa kamu gunakan:\n"
        "• /harga <nama game> — Lihat harga & diskon game\n"
        "• /pantau <nama game> — Pantau diskonnya\n"
        "• /berita — Lihat berita *umum* dunia game\n"
        "• /rekomendasi <nama game> — AI rekomendasi game mirip\n"
        "• /info <nama game> — Detail lengkap game (Steam)\n"
        "• /trending — Game paling sering diskon minggu ini\n"
        "• /konversi — akan mengkonversi mata uang yang diinginkan\n"
        "• /help — Tampilkan daftar perintah\n\n"
        "💡 Contoh:\n"
        "`/harga red dead redemption 2`\n"
        "`/konversi 100 usd idr `\n"
        "`/rekomendasi elden ring`\n",
        parse_mode="Markdown"
    )



# /harga → Ambil harga & diskon dari CheapShark
async def harga(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Contoh: /harga gta v")
        return

    nama_game = " ".join(args)
    result = price_watcher.get_game_price(nama_game)
    await update.message.reply_text(result)


# /pantau → Tambahkan game ke daftar pantauan user
async def pantau(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    args = context.args
    if not args:
        await update.message.reply_text("Contoh: /pantau gta v")
        return

    game_name = " ".join(args)
    msg = tracker.add_to_watchlist(user_id, game_name)
    await update.message.reply_text(msg)


# /berita → Ambil dan ringkas berita game terbaru (umum)
async def berita(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📰 Mengambil berita game terbaru...", parse_mode="Markdown")
    hasil = news_fetcher.get_game_news()
    await update.message.reply_text(hasil, parse_mode="Markdown")


# /rekomendasi → Beri saran game mirip pakai AI
async def rekomendasi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Contoh: /rekomendasi gta v")
        return

    game_name = " ".join(args)
    rec = recommender.recommend_game(game_name)
    await update.message.reply_text(rec, parse_mode="Markdown")


# /info → Ambil detail lengkap game dari Steam
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Contoh: /info gta v")
        return

    game_name = " ".join(args)
    result = game_info.get_game_info(game_name)
    await update.message.reply_text(result, parse_mode="Markdown", disable_web_page_preview=False)


# /trending → Tampilkan game diskon paling populer
async def trending_cmd(update, context):
    trend = trending.get_trending_games()
    await update.message.reply_text(trend, parse_mode="Markdown")


# /help → Tampilkan daftar perintah
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
🕹️ *GameVerse AI Bot — Daftar Perintah Lengkap*:

/harga <nama game> — Lihat harga & diskon terbaru  
/pantau <nama game> — Pantau harga game pilihan  
/berita — Baca berita game terbaru (AI Summarizer)  
/rekomendasi <nama game> — Rekomendasi game mirip  
/info <nama game> — Detail lengkap game (Steam)  
/trending — Game diskon paling populer minggu ini   
""", parse_mode="Markdown")

# /konversi → Konversi nilai mata uang
async def konversi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return  # pastikan bukan event lain

    args = context.args
    if len(args) != 3:
        await update.message.reply_text("⚙️ Format: /konversi <jumlah> <dari> <ke>\nContoh: /konversi 10 usd idr")
        return

    try:
        amount = float(args[0])
        from_currency = args[1]
        to_currency = args[2]

        result = currency_tool.convert_currency(amount, from_currency, to_currency)
        await update.message.reply_text(result)
    except ValueError:
        await update.message.reply_text("❌ Jumlah harus berupa angka. Contoh: /konversi 10 usd idr")


# ============================================
# Bagian 2: Jalankan bot
# ============================================

def main():
    token = os.environ.get("TG_BOT_TOKEN", "")
    if not token:
        print("⚠️ Token bot belum diatur! Gunakan environment variable TG_BOT_TOKEN.")
        return

    app = ApplicationBuilder().token(token).build()

    # Daftar semua perintah yang aktif
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("harga", price_watcher.handle_price_command))
    app.add_handler(CommandHandler("pantau", pantau))
    app.add_handler(CommandHandler("berita", berita))
    app.add_handler(CommandHandler("rekomendasi", rekomendasi))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("trending", trending_cmd))
    app.add_handler(CommandHandler("konversi", konversi))


    print("🤖 GameVerse AI Bot sedang berjalan...")
    app.run_polling()


if __name__ == "__main__":
    main()
