import telebot
from telebot import types
import yt_dlp
import os

TOKEN = '8350288555:AAFOHfC5qissUqtyjCGpD1v9ctD3BdV-86Q'
KANAL_ID = '@uz_kayfiyat_kliplar'
bot = telebot.TeleBot(TOKEN)

search_results = {}

def check_sub(user_id):
    try:
        member = bot.get_chat_member(KANAL_ID, user_id)
        return member.status in ['creator', 'administrator', 'member']
    except:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    if check_sub(message.from_user.id):
        bot.send_message(message.chat.id, "✅ Xush kelibsiz! Musiqa nomini yozing:")
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Kanalga a'zo bo'lish", url=f"https://t.me/{KANAL_ID[1:]}"))
        bot.send_message(message.chat.id, f"⚠️ Botdan foydalanish uchun {KANAL_ID} kanaliga a'zo bo'ling!", reply_markup=markup)

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
        'default_search': 'scsearch5',
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
        
        markup = types.InlineKeyboardMarkup()
        text = "🎵 **Qaysi birini yuklamoqchisiz?**\n\n"
        
        for i, entry in enumerate(info['entries']):
            title = entry.get('title', 'Musiqa')[:40]
            url = entry.get('webpage_url')
            callback_data = f"dl_{i}_{message.from_user.id}"
            search_results[callback_data] = {
                'url': url,
                'title': entry.get('title'),
                'performer': entry.get('uploader')
            }
            text += f"{i+1}. {title}\n"
            markup.add(types.InlineKeyboardButton(f"{i+1}", callback_data=callback_data))

        bot.edit_message_text(text, message.chat.id, m.message_id, reply_markup=markup, parse_mode='Markdown')
    except Exception as e:
        bot.edit_message_text("❌ Xato! Keyinroq urinib ko'ring.", message.chat.id, m.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('dl_'))
def download_selected(call):
    if call.data not in search_results:
        bot.answer_callback_query(call.id, "Eski ma'lumot. Iltimos qaytadan qidiring.")
        return

    data = search_results[call.data]
    bot.edit_message_text(f"📥 Yuklanmoqda: **{data['title']}**", call.message.chat.id, call.message.message_id, parse_mode='Markdown')

    # SoundCloud orqali yuklash sozlamasi
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(data['url'], download=True)
            filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')

        with open(filename, 'rb') as audio:
            bot.send_audio(call.message.chat.id, audio, title=data['title'], performer=data['performer'])
        
        os.remove(filename)
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Yuklashda xatolik yuz berdi.")

bot.infinity_polling()
