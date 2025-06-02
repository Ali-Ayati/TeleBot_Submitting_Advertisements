from ..config import telgram_api, db_config
from telebot import TeleBot, custom_filters
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
import mysql.connector
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup
import re


def get_admin_ids():
    with mysql.connector.connect(**db_config) as connection:
        with connection.cursor() as cursor:
            sql = "SELECT admin_id FROM admins"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result


class Support(StatesGroup):
    text = State()
    respond = State()


def escape_special_characters(txt):
    special_char = r"(\*\_\[\]\(\)\~\`\>\#\+\-\=\|\{\}\.\!)"
    return re.sub(special_char, r'\\\1', txt)


state_st = StateMemoryStorage()


bot = TeleBot(telgram_api, state_storage=state_st, parse_mode="HTML")

# Start the bot with a support button
@bot.message_handler(commands=['start'])
def start(m):
    """Handles the /start command and shows the support button."""
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add("پشتیبانی")
    bot.send_message(m.chat.id, "سلام خوش آمدید.", reply_markup=markup)


# Handle support message trigger
@bot.message_handler(func=lambda m: m.text in ["Support", "پشتیبانی"])
def support_message(m):
    """Trigger user state for entering support message."""
    txt = m.text
    id = m.chat.id

    # Check language and set state accordingly
    if txt == "پشتیبانی":
        bot.send_message(chat_id=id, text="لطفا پیام خود را ارسال کنید:")
        bot.set_state(user_id=m.from_user.id, state=Support.text, chat_id=id)
    else:
        bot.send_message(chat_id=id, text="please send your message:")
        bot.set_state(user_id=m.from_user.id, state=Support.text, chat_id=id)
        print(Support.text)


# Receive user's support message and forward to admins
@bot.message_handler(state=Support.text)
def support_txt(m):
    """Receives a user's message in support state and sends it to all admins."""
    id = m.from_user.id

    # Create reply button for each message
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text="پاسخ", callback_data=id)
    markup.add(button)

    # Get all admin user IDs
    admin_ids = get_admin_ids()

    # Forward message to each admin
    for i in admin_ids:
        bot.send_message(
            chat_id=i[0],
            text=f"""پیامی از کاربر با ای دی <code>{id}</code> با یوزرنیم @{id}:\nمتن پیام:\n
<b>{escape_special_characters(m.text)}</b>""",
            reply_markup=markup,
            parse_mode="HTML"
        )

    # Inform the user that message was sent
    bot.send_message(chat_id=m.chat.id, text="پیام شما برای ادمین ارسال شد.")

    # Save message to database
    with mysql.connector.connect(**db_config) as connection:
        with connection.cursor() as cursor:
            sql = f"INSERT INTO events_mange (user_id, user_message) VALUES (%s, %s)"
            val = (id, m.text)
            cursor.execute(sql, val)
            connection.commit()

    # Clear user state
    bot.delete_state(user_id=id, chat_id=m.chat.id)


# Admin replies to the user message in support state
@bot.message_handler(state=Support.respond)
def answer_txt(m):
    """Admin sends a reply to the first unanswered support message."""
    with mysql.connector.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            # Get the first message that hasn't been answered yet
            sql = "SELECT event_id, user_id, user_message FROM events_mange WHERE admin_answer IS NULL LIMIT 1"
            cursor.execute(sql)
            event = cursor.fetchone()

            if not event:
                bot.send_message(m.chat.id, "پیامی برای پاسخ‌گویی یافت نشد.")
                return

            event_id, user_id, user_message = event

            # Send admin's reply to the user
            bot.send_message(user_id, text=f"""پیام شما:
<i>{escape_special_characters(user_message)}</i>

پاسخ پشتیبان:
<b>{escape_special_characters(m.text)}</b>""", parse_mode="HTML")

            # Save admin's response in database
            cursor.execute(
                "UPDATE events_mange SET admin_id = %s, admin_answer = %s WHERE event_id = %s",
                (m.from_user.id, m.text, event_id)
            )
            conn.commit()

    # Notify admin of successful send
    bot.send_message(m.chat.id, "پاسخ شما ارسال شد.")

    # Clear admin state
    bot.delete_state(user_id=m.from_user.id, chat_id=m.chat.id)


# Handle inline button "reply" pressed by admin
@bot.callback_query_handler(func=lambda call: True)
def admin_answer(call):
    """Handles the callback query to allow admin to reply to a support message."""
    id = int(call.data)

    # Ask admin to write reply
    bot.send_message(chat_id=call.message.chat.id, text=f"پیام خود را به <code>{id}</code> بنویسید.", parse_mode="HTML")

    # Set admin in respond state
    bot.set_state(user_id=call.from_user.id, state=Support.respond, chat_id=call.message.chat.id)


# Bot runner
if __name__ == "__main__":
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.infinity_polling()