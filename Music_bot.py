import telebot
from telebot import types
import yt_dlp
import os

# MA'LUMOTLAR
TOKEN = '8350288555:AAEpHqPxt_U6Bw6FQwYRUNNT3yCbDwasToo'
bot = telebot.TeleBot(TOKEN)

# Foydalanuvchini bazaga qo'shish (Statistika uchun)
def add_user(user_id):
    if not os.path.exists('users.txt'):
        with open('users.txt', 'w') as f: f.write("")
    with open('users.txt', 'r') as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open('users.txt', 'a') as f:
            f.write(str(user_id) + '\n')

@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.from_user.id) # Har bir yangi odamni bazaga qo'shadi
    bot.send_message(message.chat.id, "✅ Xush kelibsiz! Musiqa nomini yoki YouTube ssilkasi yozing:")

@bot.message_handler(commands=['stat'])
def statistics(message):
    if os.path.exists('users.txt'):
        with open('users.txt', 'r') as f:
            count = len(f.read().splitlines())
        bot.send_message(message.chat.id, f"📊 Jami foydalanuvchilar soni: {count} ta")
    else:
        bot.send_message(message.chat.id, "📊 Hozircha foydalanuvchilar yo'q.")

@bot.message_handler(func=lambda message: True)
def search_music(message):
    m = bot.reply_to(message, "🔎 Qidirilmoqda...")
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(f"ytsearch5:{message.text}", download=False)['entries']
            
        markup = types.InlineKeyboardMarkup()
        for i, entry in enumerate(search_results):
            markup.add(types.InlineKeyboardButton(f"{i+1}. {entry.get('title')[:30]}...", callback_data=f"dl_{entry['id']}"))
            
        bot.edit_message_text("👇 Kerakli musiqani tanlang:", message.chat.id, m.message_id, reply_markup=markup)
    except:
        bot.edit_message_text("❌ Musiqa topilmadi yoki xato yuz berdi.", message.chat.id, m.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('dl_'))
def download_music(call):
    video_id = call.data.split('_')[1]
    bot.edit_message_text("📥 Yuklanmoqda...", call.message.chat.id, call.message.message_id)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(id)s.%(ext)s',
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
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
        bot.send_message(call.message.chat.id, "❌ Yuklashda xato bo'ldi. Qaytadan urinib ko'ring.")

bot.infinity_polling()

