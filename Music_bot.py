import telebot
from telebot import types
import yt_dlp
import os

TOKEN = '8350288555:AAF9vnKGF50isbJLvKUcEWhXAxf5ZoRVEHA'
KANAL_1 = '@uz_kayfiyat_kliplar'
KANAL_2 = '@waveoffeelings001'
bot = telebot.TeleBot(TOKEN)

def check_sub(user_id):
    try:
        s1 = bot.get_chat_member(KANAL_1, user_id).status
        s2 = bot.get_chat_member(KANAL_2, user_id).status
        ok = ['creator', 'administrator', 'member']
        return (s1 in ok) and (s2 in ok)
    except:
        return True

@bot.message_handler(commands=['start'])
def start(message):
    if check_sub(message.from_user.id):
        bot.send_message(message.chat.id, "✅ Xush kelibsiz! Musiqa nomini yozing:")
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("1-kanalga obuna", url=f"https://t.me/{KANAL_1[1:]}"))
        markup.add(types.InlineKeyboardButton("2-kanalga obuna", url=f"https://t.me/{KANAL_2[1:]}"))
        markup.add(types.InlineKeyboardButton("✅ Tekshirish", callback_data="check_main"))
        bot.send_message(message.chat.id, "⚠️ Botdan foydalanish uchun kanallarga a'zo bo'ling!", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def search_music(message):
    if not check_sub(message.from_user.id):
        start(message)
        return
    
    query = message.text
    m = bot.reply_to(message, "🔎 Qidirilmoqda...")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(f"ytsearch5:{query}", download=False)['entries']
            
        markup = types.InlineKeyboardMarkup()
        for i, entry in enumerate(search_results):
            btn_text = f"{i+1}. {entry.get('title')[:35]}..."
            markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"dl_{entry['id']}"))
            
        bot.edit_message_text("👇 Kerakli musiqani tanlang:", message.chat.id, m.message_id, reply_markup=markup)
    except Exception as e:
        bot.edit_message_text("❌ Musiqa topilmadi yoki YouTube blokladi.", message.chat.id, m.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('dl_'))
def download_music(call):
    video_id = call.data.split('_')[1]
    bot.edit_message_text("📥 Yuklanmoqda, kuting...", call.message.chat.id, call.message.message_id)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=True)
            filename = ydl.prepare_filename(info)
            
        with open(filename, 'rb') as audio:
            bot.send_audio(call.message.chat.id, audio, title=info.get('title'))
        
        if os.path.exists(filename): os.remove(filename)
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        bot.send_message(call.message.chat.id, "❌ Yuklashda xato bo'ldi. Server bloklangan bo'lishi mumkin.")

@bot.callback_query_handler(func=lambda call: call.data == "check_main")
def check_callback(call):
    if check_sub(call.from_user.id):
        bot.edit_message_text("✅ Rahmat! Musiqa nomini yozing:", call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "❌ Hali obuna bo'lmadingiz!", show_alert=True)

bot.infinity_polling()
