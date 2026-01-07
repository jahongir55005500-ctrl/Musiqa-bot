import telebot
import yt_dlp
import os

TOKEN = '8350288555:AAFcVWJ6pxtaUxLQRf-8U-MVs4nRiMADR0I'
KANAL_ID = '@uz_kayfuyat_kliplar'

bot = telebot.TeleBot(TOKEN)

def check_sub(user_id):
    try:
        status = bot.get_chat_member(KANAL_ID, user_id).status
        return status in ['creator', 'administrator', 'member']
    except Exception: return False

@bot.message_handler(commands=['start'])
def start(message):
    if check_sub(message.from_user.id):
        bot.reply_to(message, "✅ Xush kelibsiz! Musiqa nomini yozing.")
    else:
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton("Kanalga a'zo bo'lish ➕", url=f"https://t.me/{KANAL_ID[1:]}")
        markup.add(btn)
        bot.send_message(message.chat.id, "⚠️ Botdan foydalanish uchun kanalga a'zo bo'ling!", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def download(message):
    if not check_sub(message.from_user.id): return
    query = message.text
    m = bot.reply_to(message, "📥 Qidirilmoqda...")
    ydl_opts = {'format': 'bestaudio/best', 'outtmpl': 'm.mp3', 'noplaylist': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([f"ytsearch1:{query}"])
        with open('m.mp3', 'rb') as a: bot.send_audio(message.chat.id, a, caption=f"🎵 @Music_yukla_321_bot")
        os.remove('m.mp3')
        bot.delete_message(message.chat.id, m.message_id)
    except: bot.edit_message_text("❌ Xato!", message.chat.id, m.message_id)

bot.infinity_polling()
