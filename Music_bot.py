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
        return s1 in ['creator', 'administrator', 'member'] and s2 in ['creator', 'administrator', 'member']
    except:
        return True

@bot.message_handler(commands=['start'])
def start(message):
    if check_sub(message.from_user.id):
        bot.send_message(message.chat.id, "🔍 Musiqa nomini yozing:")
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("1-kanal", url=f"https://t.me/{KANAL_1[1:]}"))
        markup.add(types.InlineKeyboardButton("2-kanal", url=f"https://t.me/{KANAL_2[1:]}"))
        markup.add(types.InlineKeyboardButton("✅ Tekshirish", callback_data="check_main"))
        bot.send_message(message.chat.id, "⚠️ Ikkala kanalga ham a'zo bo'ling:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def search_music(message):
    if not check_sub(message.from_user.id):
        start(message)
        return
    
    query = message.text
    m = bot.reply_to(message, "🔎 Qidirilmoqda...")
    
    ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'noplaylist': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 5 ta natijani qidirish
            search_results = ydl.extract_info(f"ytsearch5:{query}", download=False)['entries']
            
        markup = types.InlineKeyboardMarkup()
        for i, entry in enumerate(search_results):
            # Har bir natija uchun tugma (callback_data orqali URL yuboramiz)
            btn_text = f"{i+1}. {entry.get('title')[:30]}..."
            markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"dl_{entry['id']}"))
            
        bot.edit_message_text("👇 Kerakli musiqani tanlang:", message.chat.id, m.message_id, reply_markup=markup)
    except:
        bot.edit_message_text("❌ Musiqa topilmadi.", message.chat.id, m.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('dl_'))
def download_music(call):
    video_id = call.data.split('_')[1]
    bot.edit_message_text("📥 Yuklanmoqda...", call.message.chat.id, call.message.message_id)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=True)
            filename = ydl.prepare_filename(info)
            
        with open(filename, 'rb') as audio:
            bot.send_audio(call.message.chat.id, audio, title=info.get('title'))
        
        if os.path.exists(filename): os.remove(filename)
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        bot.send_message(call.message.chat.id, "❌ Yuklashda xato bo'ldi.")

@bot.callback_query_handler(func=lambda call: call.data == "check_main")
def check_callback(call):
    if check_sub(call.from_user.id):
        bot.edit_message_text("✅ Rahmat! Musiqa nomini yozing:", call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "❌ Hali a'zo bo'lmadingiz!", show_alert=True)

bot.infinity_polling()
)
