import telebot
import yt_dlp
import os

# SOZLAMALAR
TOKEN = '8350288555:AAFcVWJ6pxtaIxLQRF-8U-Ws4nRiMADR0I'
KANAL_ID = '@uz_kayfiyat_kliplar' # Bu yerda 'i' harfi bilan yozildi

bot = telebot.TeleBot(TOKEN)

def check_sub(user_id):
    try:
        status = bot.get_chat_member(KANAL_ID, user_id).status
        return status in ['creator', 'administrator', 'member']
    except:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    if check_sub(message.from_user.id):
        bot.reply_to(message, "✅ Xush kelibsiz! Musiqa nomini yozing.")
    else:
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton("Kanalga a'zo bo'lish", url=f"https://t.me/{KANAL_ID[1:]}")
        markup.add(btn)
        bot.send_message(message.chat.id, "⚠️ Botdan foydalanish uchun kanalga a'zo bo'ling!", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def download_music(message):
    if not check_sub(message.from_user.id):
        start(message)
        return

    query = message.text
    m = bot.reply_to(message, "🔍 Qidirilmoqda...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'default_search': 'ytsearch1',
        'outtmpl': '%(title)s.%(ext)s', # Fayl nomi m.mp3 bo'lmaydi
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            if 'entries' in info:
                video = info['entries'][0]
            else:
                video = info
            
            filename = ydl.prepare_filename(video)
            title = video.get('title', 'Musiqa')
            performer = video.get('uploader', 'YouTube')

            with open(filename, 'rb') as audio:
                bot.send_audio(
                    message.chat.id, 
                    audio, 
                    title=title, 
                    performer=performer,
                    caption=f"🎵 {title}\n🤖 @{bot.get_me().username}"
                )
            
            os.remove(filename)
            bot.delete_message(message.chat.id, m.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ Xato!", message.chat.id, m.message_id)

bot.infinity_polling()


