# This is my data; you should replace it with your own.
from config import telgram_api, db_config, channels_, admin_id, channel_id
from telebot import TeleBot, custom_filters
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, Message, CallbackQuery
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

def user_balance(id: int) -> int:
    try:    
        with mysql.connector.connect(**db_config) as connection:
            with connection.cursor() as cursor:
                sql = "SELECT balance FROM users WHERE id = %s"
                val = (id,)
                cursor.execute(sql, val)
                result = cursor.fetchone()
                return result[0]
    except:
        return None
    
def lang_check(id: int) -> str:
    try:
        with mysql.connector.connect(**db_config) as connection:
            with connection.cursor() as cursor:
                sql = "SELECT lang FROM users WHERE id = %s"
                val = id
                cursor.execute(sql, (val,))
                result = cursor.fetchone()
                return result[0]
    except:
        return None

class Support(StatesGroup):
    text = State()
    respond = State()
    agahi = State()

def escape_special_characters(txt):
    special_char = r"(\*\_\[\]\(\)\~\`\>\#\+\-\=\|\{\}\.\!)"
    return re.sub(special_char, r'\\\1', txt)



state_st = StateMemoryStorage()
chat_ids = []
texts = {}




bot = TeleBot(telgram_api, state_storage=state_st, parse_mode="HTML")


@bot.message_handler(commands=['start'])
def start_command(m):
    
    id = m.from_user.id
    result = lang_check(id)
    is_member = check_join(m.from_user.id, channels_)
    
    if is_member:
        if result:
            if result[0] == "per":
                
                markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
                markup.add("ثبت آگهی")
                markup.add("حساب کاربری", "شارژ حساب", "زیرمجموعه گیری", "پشتیبانی")
                markup.add('/زبان')
                
                bot.send_message(m.chat.id,
                                    text="""به ربات ما خوش آمدید!
این ربات برای ثبت و مدیریت آگهی‌های شما طراحی شده است.
با استفاده از این ربات، می‌توانید آگهی‌های خود را به راحتی ثبت و منتشر کنید.""", parse_mode="HTML", reply_markup=markup)
                
            else:
                
                markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
                markup.add("Submit ADS")
                markup.add("my account", "Add Funds", "Referral", "Support")
                markup.add('/language')
                
                bot.send_message(m.chat.id, 
                                    text="""Welcome to our bot!
This bot is designed to help you submit and manage your advertisements.
You can easily create and publish your ads using this service.""", 
parse_mode="HTML",
reply_markup=markup)
        
        else:
            
            with mysql.connector.connect(**db_config) as connection:
                with connection.cursor() as cursor:
                    # اگر کاربر بار اولش بود میومد و با لینک زیرمجموعه گیری کسی اومده بود جایزه به حسابش واریز میشه.
                    token = m.text.split()
                    if len(token) > 1:
                        sql = f"UPDATE users SET balance = balance + 10000 WHERE id = {token[1]}"
                        cursor.execute(sql, (id,))
                        connection.commit()
                    
                    sql = "INSERT INTO users (id) VALUES (%s)"
                    cursor.execute(sql, (id,))
                    connection.commit()
            
            markup = InlineKeyboardMarkup(row_width=1)
            eng_button = InlineKeyboardButton(text="English", callback_data='eng')
            per_button = InlineKeyboardButton(text="فارسی", callback_data="per")
            markup.add(eng_button, per_button)
            
            bot.send_message(m.chat.id, text="کاربر عزیز لطفا زبان خود را انتخاب کنید:\n\nDear user, please select your language.", reply_markup=markup)

    else:
        markup = InlineKeyboardMarkup()
        button = InlineKeyboardButton(text="تایید", callback_data='proceed')
        markup.add(button)
        
        bot.send_message(m.chat.id, text=f"باید در کانال ما جوین شوید.\n{channels_[0]}", reply_markup=markup)


# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ

@bot.message_handler(commands=['language', 'زبان'])
def language(m):
    markup = InlineKeyboardMarkup(row_width=1)
    eng_button = InlineKeyboardButton(text="English", callback_data='eng')
    per_button = InlineKeyboardButton(text="فارسی", callback_data="per")
    markup.add(eng_button, per_button)
    
    bot.send_message(m.chat.id, text="کاربر عزیز لطفا زبان خود را انتخاب کنید:\n\nDear user, please select your language.", reply_markup=markup)


# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ



@bot.message_handler(func=lambda m: m.text in ["حساب کاربری", "my account"])
def account(m):
    txt = m.text
    id = m.from_user.id
    balance = user_balance(id)
    
    if txt == "حساب کاربری":
        bot.send_message(m.chat.id, text=f"""اطلاعات حساب کاربری:
نام کاربری: <a href='tg://user?id={id}'>{m.from_user.first_name}</a>
شناسه کاربری: <code>{id}</code>
موجودی: {balance} تومان""", parse_mode="HTML")
    
    else:
        bot.send_message(m.chat.id, text=f"""User Account Information:
Username: <a href='tg://user?id={id}'>{m.from_user.first_name}</a>
User ID: <code>{id}</code>
Balance: {balance} Toman""", parse_mode="HTML")


# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ



@bot.message_handler(func=lambda m: m.text in ["Support", "پشتیبانی"])
def support_message(m):
    "پیامی که کاربر برای ادمین میفرسته."
    txt = m.text
    id = m.chat.id
    
    if txt == "پشتیبانی":
        bot.send_message(chat_id=id, text="لطفا پیام خود را ارسال کنید:")
        # منتظر پیام کاربر میمونه
        bot.set_state(user_id=m.from_user.id, state=Support.text, chat_id=id)
    else:
        bot.send_message(chat_id=id, text="please send your message:")
        # منتظر پیام کاربر میمونه
        bot.set_state(user_id=m.from_user.id, state=Support.text, chat_id=id)

@bot.message_handler(state=Support.text)
def support_txt(m):
    "دریافت پیام کاربر توسط ادمین."
    id = m.from_user.id
    
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text="پاسخ", callback_data=id)
    markup.add(button)
    
    # اینحا ای دی ادمینو قرار میدیم تا پیام کاربر برای ادمین ارسال بشه
    bot.send_message(chat_id=admin_id, text=f"""پیامی از کاربر با ای دی <code>{id}</code> با یوزرنیم @{m.from_user.username}:\nمتن پیام:\n
<b>{escape_special_characters(m.text)}</b>""", reply_markup=markup, parse_mode="HTML")
    
    lang = lang_check(id)
    if lang == "per":
        bot.send_message(chat_id=m.chat.id, text="پیام شما برای ادمین ارسال شد.")
    
    else:
        bot.send_message(chat_id=m.chat.id, text="Your message has been sent to the admin.")
    
    texts[id] = m.text
    
    # این برای اینه که دیگه منتظر پیام کاربر برای ارسال به ادمین نمونه رباتمون
    bot.delete_state(user_id=id, chat_id=m.chat.id)

# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ


@bot.message_handler(state=Support.respond)
def answer_txt(m):
    "ارسال پاسخ ادمین برای کاربر."
    chat_id = chat_ids[-1]
    lang = lang_check(chat_id)
    
    if chat_id in texts:
        
        if lang == "per":
            bot.send_message(chat_id=chat_id, text=f"""پیام شما: \n<i>{escape_special_characters(texts[chat_id])}</i>\n
پاسخ پشتیبان:\n<b>{escape_special_characters(m.text)}</b>""", parse_mode="HTML")
            
        else:
            bot.send_message(chat_id=chat_id, text=f"""Your message:\n<i>{escape_special_characters(texts[chat_id])}</i>\n
Support reply:\n<b>{escape_special_characters(m.text)}</b>""", parse_mode="HTML")
        
        bot.send_message(chat_id=m.chat.id, text="پاسخ شما ارسال شد.")
        
        del texts[chat_id]
        chat_ids.remove(chat_id)
    
    else:
        if lang == "per":
            bot.send_message(chat_id=m.chat.id, text="مشکلی پیش آمده...\nلطفا دوباره امتحان کنید.")
        else:
            bot.send_message(chat_id=m.chat.id, text="Something went wrong...\nKindly try again.")
        
    bot.delete_state(user_id=m.from_user.id, chat_id=m.chat.id)

# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ


@bot.callback_query_handler(func=lambda call: call.data in ["per", "eng"])
def lang_callback_button(call):
    
    data = call.data
    id = int(call.from_user.id)
    
    if data == 'eng':
        
        markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add("Submit ADS")
        markup.add("my account", "Add Funds", "Referral", "Support")
        markup.add('/language')
        
        with mysql.connector.connect(**db_config) as connection:
            with connection.cursor() as cursor:
                sql = "UPDATE users SET lang = %s WHERE id = %s"
                val = (data, id)
                cursor.execute(sql, val)
                connection.commit()
                
                bot.send_message(call.message.chat.id, text="Your language has been changed to English.", reply_markup=markup)
    else:
        
        markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add("ثبت آگهی")
        markup.add("حساب کاربری", "شارژ حساب", "زیرمجموعه گیری", "پشتیبانی")
        markup.add('/زبان')
        
        with mysql.connector.connect(**db_config) as connection:
            with connection.cursor() as cursor:
                sql = "UPDATE users SET lang = %s WHERE id = %s"
                val = (data, id)
                cursor.execute(sql, val)
                connection.commit()
                
                bot.send_message(call.message.chat.id, text="زبان شما به فارسی تغییر یافت.", reply_markup=markup)


# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ
        
@bot.callback_query_handler(func=lambda call: call.data == 'proceed')
def proceed(call):
    is_member = check_join(call.from_user.id, channels_)
    
    if is_member:
        markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add("/start")
        
        bot.send_message(call.message.chat.id, text=f"شما مجاز به استفاده از ربات هستید.", reply_markup=markup)
    
    else:
        markup = InlineKeyboardMarkup()
        button = InlineKeyboardButton(text="تایید", callback_data='proceed')
        markup.add(button)
        
        bot.send_message(call.message.chat.id, text=f"باید در کانال ما جوین شوید.\n{channels_[0]}", reply_markup=markup)
        
        
        
# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ
"زیرمجموعه گیری"
@bot.message_handler(func= lambda m: m.text == "زیرمجموعه گیری")
def referral(m):
    user_id = m.from_user.id
    with open("referral.png", "rb") as photo:
        bot.send_photo(chat_id=user_id, photo=photo, caption=f"لینک زیر مجموعه گیری شما:\n\nhttps://t.me/your_bot?start={user_id}")
        
        
# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ
"ثبت آگهی"
@bot.message_handler(func= lambda m: m.text == "ثبت آگهی")
def get_agahi(m: Message):
    user_id = m.from_user.id
    
    bot.send_message(chat_id=user_id, text="آگهی خود را ارسال کنید:")
    bot.set_state(chat_id=m.chat.id, state=Support.agahi, user_id=user_id)
    
    
@bot.message_handler(state=Support.agahi)
def get_agahi_2(m: Message):
    
    markup = InlineKeyboardMarkup()
    button_1 = InlineKeyboardButton(text="رد کردن", callback_data="denie")
    button_2 = InlineKeyboardButton(text="تایید کردن", callback_data="confirm")
    markup.add(button_1, button_2)
    
    forwarded_m = bot.forward_message(chat_id=admin_id, from_chat_id=m.chat.id, message_id=m.message_id)
    
    bot.send_message(chat_id=admin_id, text=f"این کاربر میخواد آگهی ثبت کنه:\n\nایدی کاربر: {m.from_user.id}", reply_markup=markup, reply_to_message_id=forwarded_m.message_id)
    
    bot.send_message(chat_id=m.chat.id, text="آگهی شما توسط ادمین بررسی خواهد شد و نتیجه اعلام میگردد.")
    bot.delete_state(user_id=m.from_user.id, chat_id=m.chat.id)
    
@bot.callback_query_handler(lambda call: call.data == "denie")
def denie(call: CallbackQuery):
    admin_id = call.from_user.id
    
    pattern = r"ایدی کاربر: \d+"
    user_id = int(re.findall(pattern=pattern, string=call.message.text)[0].split()[2])
    
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text="با موفقیت رد شد.")
    markup.add(button)
    
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
    
    bot.send_message(chat_id=user_id, text="درخواست شما رد شد.")
    
@bot.callback_query_handler(lambda call: call.data == "confirm")
def confirm(call: CallbackQuery):
    admin_id = call.from_user.id
    
    pattern = r"ایدی کاربر: \d+"
    user_id = int(re.findall(pattern=pattern, string=call.message.text)[0].split()[2])
    
    # انتشار آگهی توی کانال مورد نظر
    bot.copy_message(
        chat_id=channel_id, # همون چنلی که میخوایم آگهی داخلش منتشر بشه
        from_chat_id=call.message.chat.id,
        message_id=call.message.reply_to_message.message_id
    )
    
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text="با موفقیت تایید شد")
    markup.add(button)
    
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
    
    bot.send_message(chat_id=user_id, text="آگهی شما با موفقیت ثبت شد.")
    


# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ

# شارژ حساب
@bot.message_handler(func= lambda m: m.text == "شارژ حساب")
def charge_account(m):
    
    markup = InlineKeyboardMarkup(row_width=3)
    butt_1 = InlineKeyboardButton(text="۱۰ هزار تومان", callback_data="10")
    butt_2 = InlineKeyboardButton(text="2۰ هزار تومان", callback_data="20")
    markup.add(butt_1, butt_2)
    
    bot.send_message(chat_id=m.chat.id, text="مقدار شارژ خود را انتخاب کنید: ", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "10")
def ten(call):
    
    user_id = call.from_user.id
    
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text="پرداخت", url=f"https://your_site_address/zarinpal/request/?user={user_id}")
    markup.add(button)
    
    bot.send_message(chat_id=user_id, text="از طریق زدن دکمه زیر پرداخت خود را انجام دهید:", reply_markup=markup)



@bot.callback_query_handler(func=lambda call: call.data == "20")
def twenty(call):
    pass


# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ


# برای دریافت پاسخ ادمین. آخر میزاریمش تا از فیلتر باقی کال ها رد بشه و اگه هیچکدوم نبود برسه به اینجا
@bot.callback_query_handler(func=lambda call: True)
def admin_answer(call):
    bot.send_message(chat_id=call.message.chat.id, text=f"پیام خود را به <code>{call.data}</code> بنویسید.", parse_mode="HTML")
    
    chat_ids.append(int(call.data))
    # ذخیره پیام ادمین در متغیر ریسپاند
    bot.set_state(user_id=call.from_user.id, state=Support.respond, chat_id=call.message.chat.id)




if __name__ == "__main__":
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.infinity_polling()