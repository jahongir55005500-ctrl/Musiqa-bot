import telebot
from telebot import types
import yt_dlp
import os

# YANGI TOKENNI SHU YERGA QO'YING
TOKEN '8350288555:AAF9vnKGF50isbJLvKUcEWhXAxf5ZoRVEHA' 
KANAL_1 = '@uz_kayfiyat_kliplar'
KANAL_2 = '@waveoffeelings001'
bot = telebot.TeleBot(TOKEN)

def check_sub(user_id):
    try:
        s1 = bot.get_chat_member(KANAL_1, user_id).status
        s2 = bot.get_chat_member(KANAL_2, user_id).status
        return s1 in ['creator', 'administrator', 'member'] and s2 in ['creator', 'administrator', 'member']
    except: return True

@bot.message_handler(commands=['start'])
def start(message):
    if check_sub(message.from_user.id):
        bot.send_message(message.chat.id, "✅ Tayyor! Musiqa nomini yozing:")
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("1-kanal", url=f"https://t.me/{KANAL_1[1:]}"))
        markup.add(types.InlineKeyboardButton("2-kanal", url=f"https://t.me/{KANAL_2[1:]}"))
        markup.add(types.InlineKeyboardButton("✅ Tekshirish", callback_data="check"))
        bot.send_message(message.chat.id, "⚠️ Kanallarga a'zo bo'ling:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def search(message):
    if not check_sub(message.from_user.id): return start(message)
    m = bot.reply_to(message, "🔎 Qidirilmoqda...")
    opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            res = ydl.extract_info(f"ytsearch5:{message.text}", download=False)['entries']
        markup = types.InlineKeyboardMarkup()
        for i, r in enumerate(res):
            markup.add(types.InlineKeyboardButton(f"{i+1}. {r['title'][:30]}", callback_data=f"dl_{r['id']}"))
        bot.edit_message_text("👇 Tanlang:", message.chat.id, m.message_id, reply_markup=markup)
    except: bot.edit_message_text("❌ Topilmadi.", message.chat.id, m.message_id)

@bot.callback_query_handler(func=lambda c: c.data.startswith('dl_'))
def dl(call):
    vid = call.data.split('_')[1]
    bot.edit_message_text("📥 Yuklanmoqda...", call.message.chat.id, call.message.message_id)
    opts = {'format': 'bestaudio/best', 'outtmpl': '%(id)s.%(ext)s', 'nocheckcertificate': True}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={vid}", download=True)
            file = ydl.prepare_filename(info)
        with open(file, 'rb') as a:
            bot.send_audio(call.message.chat.id, a, title=info.get('title'))
        if os.path.exists(file): os.remove(file)
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except: bot.send_message(call.message.chat.id, "❌ Xato.")

@bot.callback_query_handler(func=lambda c: c.data == "check")
def h(c):
    if check_sub(c.from_user.id): bot.edit_message_text("✅ Marhamat:", c.message.chat.id, c.message.message_id)
    else: bot.answer_callback_query(c.id, "❌ A'zo bo'lmadingiz!", show_alert=True)

bot.infinity_polling()
