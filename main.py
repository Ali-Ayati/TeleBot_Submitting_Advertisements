from config import *
from telebot import TeleBot
import mysql.connector

bot = TeleBot(telgram_api)

@bot.message_handler(commands=['start'])
def start_command(m):
    try:
        with mysql.connector.connect(**db_config) as connection:
            with connection.cursor() as cursor:
                sql = "INSERT INTO users (id) VALUES (%s)"
                val = m.from_user.id
                cursor.execute(sql, val)
                connection.commit()
        bot.send_message(m.chat.id, text="سلام کاربر جدید.")      
          
    except:
        bot.send_message(m.chat.id, text= "سلام کاربر قدیمی.")
        
        
        
        
        




bot.infinity_polling()