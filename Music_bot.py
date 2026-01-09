import telebot
from telebot import types
import yt_dlp
import os

TOKEN = '8350288555:AAF9vnKGF50isbJLvKUcEWhXAxf5ZoRVEHA'
KANAL_ID = '@uz_kayfiyat_kliplar'
KANAL_ID = '@waveoffeilings001' 
bot = telebot.TeleBot(TOKEN)

def check_sub(user_id):
    try:
        member = bot.get_chat_member(KANAL_ID, user_id)
        return member.status in ['creator', 'administrator', 'member']
    except:
        return True # Xatolik bo'lsa o'tkazib yuboradi

@bot.message_handler(commands=['start'])
def start(message):
    if check_sub(message.from_user.id):
        bot.send_message(message.chat.id, "✅ Tayyor! Musiqa nomini yozing:")
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("A'zo bo'lish", url=f"https://t.me/{KANAL_ID[1:]}"))
        bot.send_message(message.chat.id, f"⚠️ Botdan foydalanish uchun {KANAL_ID} kanaliga a'zo bo'ling!", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def search_music(message):
    if not check_sub(message.from_user.id):
        start(message)
        return
        
    query = message.text
    m = bot.reply_to(message, "🔍 Qidirilmoqda...")
    ydl_opts = {'format': 'bestaudio/best', 'outtmpl': '%(title)s.%(ext)s', 'quiet': True, 'noplaylist': True}
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)['entries'][0]
            filename = ydl.prepare_filename(info)
        
        with open(filename, 'rb') as audio:
            bot.send_audio(message.chat.id, audio, title=info.get('title'))
        
        if os.path.exists(filename):
            os.remove(filename)
        bot.delete_message(message.chat.id, m.message_id)
    except:
        bot.edit_message_text("❌ Xato yuz berdi.", message.chat.id, m.message_id)

bot.infinity_polling()
