import telebot
from telebot import types
import yt_dlp
import os

# YANGI TOKENNI SHU YERGA QO'YING
TOKEN = '8350288555:AAF9vnKGF50isbJLvKUcEWhXAxf5ZoRVEHA'
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
        bot.send_message(message.chat.id, "✅ Tayyor! Musiqa nomini yozing:")
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("A'zo bo'lish", url=f"https://t.me/{KANAL_ID[1:]}"))
        bot.send_message(message.chat.id, "⚠️ Kanalga a'zo bo'ling!", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def search_music(message):
    if not check_sub(message.from_user.id):
        start(message)
        return
    query = message.text
    m = bot.reply_to(message, "🔍 Qidirilmoqda...")
    ydl_opts = {'format': 'bestaudio/best', 'noplaylist': True, 'default_search': 'scsearch5', 'quiet': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
        markup = types.InlineKeyboardMarkup()
        text = "🎵 **Tanlang:**\n\n"
        for i, entry in enumerate(info['entries']):
            title = entry.get('title', 'Musiqa')[:40]
            callback_data = f"dl_{i}_{message.from_user.id}"
            search_results[callback_data] = {'url': entry.get('webpage_url'), 'title': entry.get('title'), 'performer': entry.get('uploader')}
            text += f"{i+1}. {title}\n"
            markup.add(types.InlineKeyboardButton(f"{i+1}", callback_data=callback_data))
        bot.edit_message_text(text, message.chat.id, m.message_id, reply_markup=markup, parse_mode='Markdown')
    except:
        bot.edit_message_text("❌ Topilmadi.", message.chat.id, m.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('dl_'))
def download_selected(call):
    data = search_results.get(call.data)
    if not data: return
    bot.edit_message_text("📥 Yuklanmoqda...", call.message.chat.id, call.message.message_id)
    ydl_opts = {'format': 'bestaudio/best', 'outtmpl': '%(title)s.%(ext)s', 'quiet': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(data['url'], download=True)
            filename = ydl.prepare_filename(info)
        with open(filename, 'rb') as audio:
            bot.send_audio(call.message.chat.id, audio, title=data['title'], performer=data['performer'])
        if os.path.exists(filename): os.remove(filename)
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        bot.send_message(call.message.chat.id, "❌ Xato!")

bot.infinity_polling()

