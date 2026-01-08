import telebot
import yt_dlp
import os
from telebot import types

# SOZLAMALAR
TOKEN = '8350288555:AAFOHfC5qissUqtyjCGpD1v9ctD3BdV-86Q'
KANAL_ID = '@aslwaynemusic_lyrics'

bot = telebot.TeleBot(TOKEN)

# Musiqalarni vaqtinchalik saqlash uchun lug'at
search_results = {}

def check_sub(user_id):
    try:
        status = bot.get_chat_member(KANAL_ID, user_id).status
        return status in ['creator', 'administrator', 'member']
    except:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    if check_sub(message.from_user.id):
        bot.reply_to(message, "✅ Xush kelibsiz! Musiqa nomini yozing, men 5 ta variant topaman.")
    else:
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Kanalga a'zo bo'lish", url=f"https://t.me/{KANAL_ID[1:]}")
        markup.add(btn)
        bot.send_message(message.chat.id, "⚠️ Botdan foydalanish uchun kanalga a'zo bo'ling!", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def search_music(message):
    if not check_sub(message.from_user.id):
        start(message)
        return

    query = message.text
    m = bot.reply_to(message, "🔍 Qidirilmoqda...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'default_search': 'ytsearch5', # 5 ta natija qidiradi
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if 'entries' not in info or not info['entries']:
                bot.edit_message_text("❌ Hech narsa topilmadi.", message.chat.id, m.message_id)
                return

            markup = types.InlineKeyboardMarkup()
            text = "🎵 **Qaysi birini yuklamoqchisiz?**\n\n"
            
            for i, entry in enumerate(info['entries']):
                title = entry.get('title', 'Musiqa')[:40]
                url = entry.get('webpage_url')
                # Natijani saqlab qo'yamiz
                callback_data = f"dl_{i}_{message.from_user.id}"
                search_results[callback_data] = {
                    'url': url,
                    'title': entry.get('title'),
                    'performer': entry.get('uploader')
                }
                
                text += f"{i+1}. {title}\n"
                markup.add(types.InlineKeyboardButton(f"{i+1}", callback_data=callback_data))

            bot.edit_message_text(text, message.chat.id, m.message_id, reply_markup=markup, parse_mode="Markdown")

    except Exception as e:
        bot.edit_message_text(f"❌ Xato!", message.chat.id, m.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('dl_'))
def download_selected(call):
    # Faqat so'rov yuborgan odam yuklay oladi
    user_id = int(call.data.split('_')[2])
    if call.from_user.id != user_id:
        bot.answer_callback_query(call.id, "⚠️ Bu qidiruv sizga tegishli emas!")
        return

    data = search_results.get(call.data)
    if not data:
        bot.answer_callback_query(call.id, "❌ Ma'lumot eskirgan, qayta qidiring.")
        return

    bot.edit_message_text(f"⏳ **'{data['title']}'** yuklanmoqda...", call.message.chat.id, call.message.message_id)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(data['url'], download=True)
            filename = ydl.prepare_filename(info)

            with open(filename, 'rb') as audio:
                bot.send_audio(
                    call.message.chat.id,
                    audio,
                    title=data['title'],
                    performer=data['performer'],
                    caption=f"🎵 {data['title']}\n🤖 @{bot.get_me().username}"
                )
            os.remove(filename)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            
    except Exception as e:
        bot.send_message(call.message.chat.id, "❌ Yuklashda xato yuz berdi.")

bot.infinity_polling()
