from config import *
from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import mysql.connector

bot = TeleBot(telgram_api)

def check_join(user, channels: str) -> bool:
    for i in channels:
        is_member = bot.get_chat_member(chat_id=i, user_id=user)
        
        if is_member.status in ['kicked', 'left']: # اگر هیچوقت هم جوین نداده بود میشه left
            return False
    return True

@bot.message_handler(commands=['start'])
def start_command(m):
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text="ادامه", callback_data='proceed')
    markup.add(button)
    
    try:
        with mysql.connector.connect(**db_config) as connection:
            with connection.cursor() as cursor:
                sql = "INSERT INTO users (id) VALUES (%s)"
                val = m.from_user.id
                cursor.execute(sql, (val,))
                connection.commit()
        bot.send_message(chat_id=m.chat.id, text= "سلام کاربر جدید.", reply_markup=markup)      
             
    except:
        bot.send_message(chat_id=m.chat.id, text= "سلام کاربر قدیمی.", reply_markup=markup)
        
@bot.callback_query_handler(func=lambda call: call.data == 'proceed')
def proceed(call):
    is_member = check_join(call.from_user.id, channels_)
    
    if is_member:
        markup = InlineKeyboardMarkup()
        button = InlineKeyboardButton(text="تایید", callback_data='proceed')
        markup.add(button)
        
        bot.send_message(call.message.chat_id, text=f"شما مجاز به استفاده از ربات هستید.", reply_markup=markup)
    
    else:
        bot.send_message(call.message.chat_id, text=f"باید در کانال ما جوین شوید.\n{channels_[0]}", reply_markup=markup)
        
        
        




bot.infinity_polling()