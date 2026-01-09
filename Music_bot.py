import telebot
from telebot import types
import yt_dlp
import os

# MA'LUMOTLAR
TOKEN = '8150288555:AAFDHfcSqissVqtyjCgpDlV9ctD3BdV-86Q'
KANAL_1 = '@uz_kayfiyat_kliplar'  # 1-kanal
KANAL_2 = '@waveoffeilings001'   # 2-kanal
bot = telebot.TeleBot(TOKEN)

# IKKALA KANALNI TEKSHIRISH
def check_sub(user_id):
    try:
        # 1-kanalni tekshirish
        status1 = bot.get_chat_member(KANAL_1, user_id).status
        # 2-kanalni tekshirish
        status2 = bot.get_chat_member(KANAL_2, user_id).status
        
        ok = ['creator', 'administrator', 'member']
        return (status1 in ok) and (status2 in ok)
    except:
        return True # Xato bo'lsa o'tkazib yuboradi

@bot.message_handler(commands=['start'])
def start(message):
    if check_sub(message.from_user.id):
        bot.send_message(message.chat.id, "✅ Xush kelibsiz! Musiqa nomini yozing:")
    else:
        markup = types.InlineKeyboardMarkup()
        # Ikkala kanal uchun tugma
        markup.add(types.InlineKeyboardButton("1-kanalga a'zo bo'lish", url=f"https://t.me/{KANAL_1[1:]}"))
        markup.add(types.InlineKeyboardButton("2-kanalga a'zo bo'lish", url=f"https://t.me/{KANAL_2[1:]}"))
        markup.add(types.InlineKeyboardButton("✅ A'zo bo'ldim", callback_data="check"))
        
        bot.send_message(message.chat.id, "⚠️ Botdan foydalanish uchun ikkala kanalga ham a'zo bo'lishingiz kerak!", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check")
def check_callback(call):
    if check_sub(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ Rahmat! Endi foydalanishingiz mumkin.")
        bot.edit_message_text("✅ Marhamat, musiqa nomini yozing:", call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "❌ Hali a'zo bo'lmadingiz!", show_alert=True)

@bot.message_handler(func=lambda message: True)
def search_music(message):
    if not check_sub(message.from_user.id):
        start(message)
        return
        
    query = message.text
    m = bot.reply_to(message, "🔍 Qidirilmoqda...")
    
    ydl_opts = {'format': 'bestaudio/best', 'outtmpl': '%(title)s.%(ext)s', 'quiet': True, 'noplaylist': True}
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)['entries'][0]
            filename = ydl.prepare_filename(info)
        
        with open(filename, 'rb') as audio:
            bot.send_audio(message.chat.id, audio, title=info.get('title'))
        
        if os.path.exists(filename):
            os.remove(filename)
        bot.delete_message(message.chat.id, m.message_id)
    except:
        bot.edit_message_text("❌ Xato yuz berdi.", message.chat.id, m.message_id)

bot.infinity_polling()
