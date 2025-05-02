# This is my data; you should replace it with your own.
from config import telgram_api, db_config, channels_
from telebot import TeleBot, custom_filters
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
import mysql.connector
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup
import re



def check_join(user, channels: list) -> bool:
    for i in channels:
        is_member = bot.get_chat_member(chat_id=i, user_id=user)
        
        if is_member.status in ['kicked', 'left']: # اگر هیچوقت هم جوین نداده بود میشه left
            return False
    return True

def user_balance(id):
    with mysql.connector.connect(**db_config) as connection:
        with connection.cursor() as cursor:
            sql = "SELECT balance FROM users WHERE id = %s"
            val = (id,)
            cursor.execute(sql, val)
            result = cursor.fetchone()
            return result[0]

class Support(StatesGroup):
    text = State()
    respond = State()


state_st = StateMemoryStorage()

bot = TeleBot(telgram_api, state_storage=state_st)


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
                    
                    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
                    markup.add("ثبت آگهی")
                    markup.add("حساب کاربری", "شارژ حساب", "زیرمجموعه گیری", "پشتیبانی")
                    
                    bot.send_message(m.chat.id,
                                        text="""به ربات ما خوش آمدید!
                                        این ربات برای ثبت و مدیریت آگهی‌های شما طراحی شده است.
                                        با استفاده از این ربات، می‌توانید آگهی‌های خود را به راحتی ثبت و منتشر کنید.""",
                                        parse_mode="HTML",
                                        reply_markup=markup)
                    
                else:
                    
                    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
                    markup.add("Submit ADS")
                    markup.add("my account", "Add Funds", "Referral", "Support")
                    
                    bot.send_message(m.chat.id, 
                                        text="""Welcome to our bot!
                                        This bot is designed to help you submit and manage your advertisements.
                                        You can easily create and publish your ads using this service.""", 
                                        parse_mode="HTML",
                                        reply_markup=markup)
            
            else:
                sql = "INSERT INTO users (id) VALUES (%s)"
                cursor.execute(sql, (val,))
                connection.commit()
                
                markup = InlineKeyboardMarkup(row_width=1)
                eng_button = InlineKeyboardButton(text="English", callback_data='eng')
                per_button = InlineKeyboardButton(text="فارسی", callback_data="per")
                markup.add(eng_button, per_button)
                
                bot.send_message(m.chat.id, text="کاربر عزیز لطفا زبان خود را انتخاب کنید:\n\nDear user, please select your language.", reply_markup=markup)







@bot.message_handler(commands=['language'])
def language(m):
    markup = InlineKeyboardMarkup(row_width=1)
    eng_button = InlineKeyboardButton(text="English", callback_data='eng')
    per_button = InlineKeyboardButton(text="فارسی", callback_data="per")
    markup.add(eng_button, per_button)
    
    bot.send_message(m.chat.id, text="کاربر عزیز لطفا زبان خود را انتخاب کنید:\n\nDear user, please select your language.", reply_markup=markup)





@bot.message_handler(func=lambda m: m.text in ["حساب کاربری", "my account"])
def account(m):
    txt = m.text
    user_id = m.from_user.id
    
    if txt == "حساب کاربری":
        balance = user_balance(user_id)
        bot.send_message(m.chat.id, text=f"""اطلاعات حساب کاربری:
                         نام کاربری: <a href='tg://user?id={m.from_user.id}>{m.from_user.first_name}</a>
                         شناسه کاربری: <code>{m.from_user.id}</code>
                         موجودی: {balance} تومان""", parse_mode="HTML")






@bot.callback_query_handler(func=lambda call: call.data in ["per", "eng"])
def lang_callback_button(call):
    
    data = call.data
    id = call.from_user.id
    
    if data == 'eng':
        
        markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add("Submit ADS")
        markup.add("my account", "Add Funds", "Referral", "Support")
        
        with mysql.connector.connect() as connection:
            with connection.cursor() as cursor:
                sql = "UPDATE users SET lang = %s WHERE id = %s"
                val = (data, id)
                cursor.execute(sql, val)
                connection.commit()
                
                bot.send_message(call.message.chat_id, text="Your language has been changed to English.", reply_markup=markup)
    else:
        
        markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add("ثبت آگهی")
        markup.add("حساب کاربری", "شارژ حساب", "زیرمجموعه گیری", "پشتیبانی")
        
        with mysql.connector.connect() as connection:
            with connection.cursor() as cursor:
                sql = "UPDATE users SET lang = %s WHERE id = %s"
                val = (data, id)
                cursor.execute(sql, val)
                connection.commit()
                
                bot.send_message(call.message.chat_id, text="زبان شما به فارسی تغییر یافت.")





        
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
        
        
        




if __name__ == "__main__":
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.infinity_polling()