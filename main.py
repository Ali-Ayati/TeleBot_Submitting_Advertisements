# This is my data; you should replace it with your own.
from config import telgram_api, db_config, channels_
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
    
    with mysql.connector.connect(**db_config) as connection:
        with connection.cursor() as cursor:
            sql = "SELECT id FROM users WHERE id = %s"
            val = m.from_user.id
            cursor.execute(sql, (val,))
            result = cursor.fetchone()
            
            if result:
                if result[0] == "per":
                    bot.send_message(m.chat.id, text="به ربات خوش آمدید.")
                else:
                    bot.send_message(m.chat.id, text="welcom to bot.")
            
            else:
                sql = "INSERT INTO users (id) VALUES (%s)"
                cursor.execute(sql, (val,))
                connection.commit()
                
                markup = InlineKeyboardMarkup(row_width=1)
                eng_button = InlineKeyboardButton(text="English", callback_data='eng')
                per_button = InlineKeyboardButton(text="فارسی", callback_data="per")
                markup.add(eng_button, per_button)
                
                bot.send_message(m.chat.id, text="کاربر عزیز لطفا زبان خود را انتخاب کنید:\n\nDear user, please select your language.", reply_markup=markup)
                
@bot.callback_query_handler(func=lambda call: call.data in ["per", "eng"])
def




        
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