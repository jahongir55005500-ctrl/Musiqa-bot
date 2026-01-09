import telebot
from telebot import types
import yt_dlp
import os

# YANGI TOKENNI SHU YERGA QO'YING
TOKEN = '8350288555:AAF9vnKGF50isbJLvKUcEWhXAxf5ZoRVEHA'
KANAL_ID = '@uz_kayfiyat_kliplar'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "✅ Tayyor! Musiqa nomini yozing:")

@bot.message_handler(func=lambda message: True)
def search_music(message):
    query = message.text
    m = bot.reply_to(message, "🔍 Qidirilmoqda...")
    # FFmpeg talab qilmaydigan yuklash sozlamalari
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
        'noplaylist': True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)['entries'][0]
            filename = ydl.prepare_filename(info)
        
        with open(filename, 'rb') as audio:
            bot.send_audio(message.chat.id, audio, title=info.get('title'))
        
        if os.path.exists(filename):
            os.remove(filename)
        bot.delete_message(message.chat.id, m.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Xato: {str(e)}", message.chat.id, m.message_id)

bot.infinity_polling()
