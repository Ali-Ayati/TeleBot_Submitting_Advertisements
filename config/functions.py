from .config import db_config, channels_, advertisement_fee
from telebot import TeleBot
import mysql.connector
from telebot.handler_backends import State, StatesGroup
import re




def check_join(user_id: int, channels: list, bot: TeleBot) -> bool:
    for i in channels:
        is_member = bot.get_chat_member(chat_id=i, user_id=user_id)
        
        if is_member.status in ['kicked', 'left']: # اگر هیچوقت هم جوین نداده بود میشه left
            return False
    return True

# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ

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
# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ
    
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

# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ

def escape_special_characters(txt):
    special_char = r"(\*\_\[\]\(\)\~\`\>\#\+\-\=\|\{\}\.\!)"
    return re.sub(special_char, r'\\\1', txt)

# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ

class Lang():
    def __init__(self, lang: str = "per"):
        self.lang = lang
        self.messages = {
            "join_required_message" : {
                "per" : f"📢 <b>برای ادامه استفاده از ربات، لطفاً ابتدا در کانال زیر عضو شوید:</b>\n\n{channels_[0]}\n\n✅ بعد از عضویت، روی دکمه <b>«جوین شدم»</b> بزنید.",
                "eng" : f"📢 <b>To continue using the bot, please first join the following channel:</b>\n\n{channels_[0]}\n\n✅ Once you've joined, tap the <b>“I've Joined”</b> button."
            },
            "welcome_message": {
                "per": """👋 <b>به ربات ما خوش آمدید!</b>

📢 این ربات برای <b>ثبت و مدیریت آگهی‌های شما</b> طراحی شده است.
📝 با استفاده از این ربات می‌توانید آگهی‌های خود را به سادگی <b>ثبت و منتشر</b> کنید.""",
                "eng": """👋 <b>Welcome to our bot!</b>

📢 This bot is designed to help you <b>submit and manage your ads</b>.
📝 You can easily <b>create and publish</b> your advertisements using this bot."""
            },
            "error_generic": {
                "per": "❗️ <b>مشکلی پیش آمده است</b>\nلطفاً در زمان دیگری دوباره تلاش کنید.",
                "eng": "❗️ <b>Something went wrong</b>\nPlease try again later."
            },
            "success_msg": {
                "per": "✅ زبان با موفقیت تغییر یافت.",
                "eng": "✅ Language changed successfully."
            },
            "account_info": {
                "per": "👤 <b>اطلاعات حساب کاربری شما</b>:\n\nنام: <a href='tg://user?id=%s'>%s</a>\n🆔 شناسه عددی: <code>%s</code>\n💰 موجودی: <b>%s تومان</b>",
                "eng": "👤 <b>Your Account Information</b>:\n\n▪️ Name: <a href='tg://user?id=%s'>%s</a>\n🆔 User ID: <code>%s</code>\n💰 Balance: <b>%s Toman</b>"
            },
            "send_your_message": {
                "per": "✉️ لطفاً پیام خود را برای ما ارسال کنید:",
                "eng": "✉️ Please type and send us your message:"
            },
            "message_sent_to_admin": {
                "per": "✅ پیام شما با موفقیت برای ادمین ارسال شد.",
                "eng": "✅ Your message has been successfully sent to the admin."
            },
            "admin_respond": {
                "per": "پیام شما: \n<i>%s</i>\n\nپاسخ پشتیبان:\n<b>%s</b>",
                "eng": "Your message:\n<i>%s</i>\n\nSupport reply:\n<b>%s</b>"
            },
            "referral_link": {
                "per": "📣 <b>لینک دعوت شما:</b>\n\n👇 برای دعوت دوستانتان از لینک زیر استفاده کنید 👇\n\n<a href='https://t.me/yourbot_id?start=%s'>https://t.me/yourbot_id?start=%s</a>",
                "eng": "📣 <b>Your Referral Link:</b>\n\n👇 Use the link below to invite your friends 👇\n\n<a href='https://t.me/yourbot_id?start=%s'>https://t.me/yourbot_id?start=%s</a>"
            },
            "send_ad_prompt": {
                "per": "📝 <b>لطفاً آگهی خود را ارسال کنید:</b>\n\nشما می‌توانید متن، عکس یا ویدیو مرتبط با آگهی را ارسال نمایید.",
                "eng": "📝 <b>Please send your ad:</b>\n\nYou can send a text, image, or video related to your advertisement."
            },
            "ad_pending_review": {
                "per": "⌛️ آگهی شما برای بررسی به ادمین ارسال شد.\nنتیجه بررسی به شما اطلاع داده خواهد شد.",
                "eng": "⌛️ Your ad has been sent to the admin for review.\nYou will be notified once a decision is made."
            },
            "request_rejected": {
                "per": "❌ متأسفیم، درخواست شما رد شد.",
                "eng": "❌ Sorry, your request has been rejected."
            },
            "ad_submitted_success": {
                "per": "✅ آگهی شما با موفقیت ثبت شد و در صف بررسی قرار گرفت.",
                "eng": "✅ Your ad has been successfully submitted and is now in the review queue."
            },
            "does_not_have_enough_balance":{
                "per": "❌ حساب شما موجودی کافی برای ثبت آگهی ندارد.\nلطفاً ابتدا حساب خود را شارژ کنید.",
                "eng": "❌ Your account does not have enough balance to submit an ad.\nPlease top up your account first."
            },
            "charge_prompt":{
                "per": "💳 <b>لطفاً مقدار شارژ مورد نظر خود را انتخاب کنید:</b>",
                "eng": "💳 <b>Please select your desired top-up amount:</b>"
            },
            "pay": {
                "per": "💰 <b>برای انجام پرداخت، روی دکمه زیر کلیک کنید:</b>",
                "eng": "💰 <b>Click the button below to complete your payment:</b>"
            }
        }
        
    def get(self, key: str) -> str:
        return self.messages.get(key, {}).get(self.lang, f"[{key}]")
    
# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ

def get_referral(token: int, gift: int) -> bool:
    "اگر کاربر از طرف کاربر دیگری دعوت شده باشه، کاربر دعوت کننده جایزه میگیره"
    
    try:    
        with mysql.connector.connect(**db_config) as connection:
            with connection.cursor() as cursor:
                # اگر کاربر بار اولش بود میومد و با لینک زیرمجموعه گیری کسی اومده بود جایزه به حسابش واریز میشه
                sql = f"UPDATE users SET balance = balance + {gift} WHERE id = {token}"
                cursor.execute(sql)
                connection.commit()
                return True
            
    except Exception as e:
        print(f"get_referral ERROR: {e}")
        return False

# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ

def add_new_member(user_id: int):
    try:    
        with mysql.connector.connect(**db_config) as connection:
            with connection.cursor() as cursor:
                # اگر کاربر بار اولش بود میومد و با لینک زیرمجموعه گیری کسی اومده بود جایزه به حسابش واریز میشه
                sql = "INSERT INTO users (id) VALUES (%s)"
                cursor.execute(sql, (user_id,))
                connection.commit()
                return True
            
    except Exception as e:
        print(f"add_new_member ERROR: {e}")
        return False
    
# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ

def change_lang(user_id: int, lang: str) -> bool:
    
    try:
        with mysql.connector.connect(**db_config) as conn:
            with conn.cursor() as cur:
                sql = "UPDATE users SET lang = %s"
                cur.execute(sql, (lang,))
                conn.commit()
                return True
        
    except Exception as e:
        print(f"change_lang Error: {e}")
        return False
    
# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ

def advertise_pay(user_id: int):
    try:    
        with mysql.connector.connect(**db_config) as connection:
            with connection.cursor() as cursor:
                # هزینه تبلیغات کسر میشود.
                sql = f"UPDATE users SET balance = balance - {advertisement_fee} WHERE id = {user_id}"
                cursor.execute(sql)
                connection.commit()
                return True
            
    except Exception as e:
        print(f"advertise_pay ERROR: {e}")
        return False