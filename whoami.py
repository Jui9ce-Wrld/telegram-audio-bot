import os
from pathlib import Path
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = "7971468678:AAHEn_0ACbnhu8fAOgFu1B2MAGmJfkJFs5g"
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

COOKIES_FILE = "cookies.txt"  # اینجا نام فایل کوکی رو مشخص کن

async def audio_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    chat_id = update.effective_chat.id

    if "youtube.com" not in url.lower() and "instagram.com" not in url.lower():
        await update.message.reply_text("لطفاً فقط لینک یوتیوب یا اینستاگرام بفرستید.")
        return

    await update.message.reply_text("در حال استخراج آهنگ از ویدیو... 🎵")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(DOWNLOAD_DIR / "%(id)s.%(ext)s"),
        "postprocessors": [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        "noplaylist": True,
        "quiet": True,
        # اضافه کردن کوکی اینجا:
        "cookiefile": COOKIES_FILE,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            base, ext = os.path.splitext(filename)
            mp3_file = base + ".mp3"

        size = os.path.getsize(mp3_file)
        if size <= 50 * 1024 * 1024:
            await context.bot.send_audio(chat_id=chat_id, audio=open(mp3_file, "rb"),
                                         title=info.get('title', 'آهنگ'))
            await update.message.reply_text("آهنگ ارسال شد 🎉")
        else:
            await update.message.reply_text("حجم فایل بیشتر از ۵۰ مگابایت است و نمی‌توان ارسال کرد.")
    except Exception as e:
        await update.message.reply_text(f"خطا در استخراج صدا: {e}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), audio_handler))
    print("Bot started ✅")
    app.run_polling()

if __name__ == "__main__":
    main()
