import telebot
from telebot import types
import yt_dlp
import os

# YANGI TOKENNI SHU YERGA QO'YING (BotFather'dan revoke qilib olinganini)
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
        btn1 = types.InlineKeyboardButton("1-kanalga obuna", url=f"https://t.me/{KANAL_1[1:]}")
        btn2 = types.InlineKeyboardButton("2-kanalga obuna", url=f"https://t.me/{KANAL_2[1:]}")
        btn3 = types.InlineKeyboardButton("✅ Tekshirish", callback_data="check")
        markup.add(btn1)
        markup.add(btn2)
        markup.add(btn3)
        bot.send_message(message.chat.id, "⚠️ Botdan foydalanish uchun ikkala kanalga ham a'zo bo'ling!", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check")
def check_callback(call):
    if check_sub(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "✅ Rahmat! Endi musiqa nomini yozing:")
    else:
        bot.answer_callback_query(call.id, "❌ Hali ikkala kanalga a'zo bo'lmadingiz!", show_alert=True)

@bot.message_handler(func=lambda message: True)
def search_music(message):
    if not check_sub(message.from_user.id):
        start(message)
        return
    m = bot.reply_to(message, "🔍 Qidirilmoqda...")
    ydl_opts = {'format': 'bestaudio/best', 'outtmpl': '%(title)s.%(ext)s', 'quiet': True, 'noplaylist': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{message.text}", download=True)['entries'][0]
            filename = ydl.prepare_filename(info)
        with open(filename, 'rb') as audio:
            bot.send_audio(message.chat.id, audio, title=info.get('title'))
        if os.path.exists(filename): os.remove(filename)
        bot.delete_message(message.chat.id, m.message_id)
    except:
        bot.edit_message_text("❌ Xato!", message.chat.id, m.message_id)

bot.infinity_polling()
