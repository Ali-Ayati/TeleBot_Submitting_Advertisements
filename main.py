# This is my data; you should replace it with your own.
from config import (
    telgram_api,
    admin_id,
    channel_id,
    advertisement_fee,
    check_join,
    user_balance,
    lang_check,
    escape_special_characters,
    Lang,
    get_referral,
    add_new_member,
    change_lang,
    advertise_pay
)
from config import telgram_api, db_config, channels_, admin_id, channel_id
from telebot import TeleBot, custom_filters
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, Message, CallbackQuery
import mysql.connector
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup
import re

state_st = StateMemoryStorage()
chat_ids = []
texts = {}

# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ

class Support(StatesGroup):
    text = State()
    respond = State()
    agahi = State()

# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ

class KeyFactory:
    """
    A factory class to generate keyboard markups based on language preference.
    
    Attributes:
        lang (str): Language code ("per" for Persian or other for English).
    """
    
    def __init__(self, lang: str = "per"):
        """
        Initialize the KeyFactory with a specific language.

        Args:
            lang (str): Language code, default is "per" (Persian).
        """
        self.lang = lang

    def proceed_markup(self) -> InlineKeyboardMarkup:
        """
        Create an inline keyboard markup with a single 'proceed' button.

        Returns:
            InlineKeyboardMarkup: A markup containing the proceed button.
        """
        markup = InlineKeyboardMarkup()

        # Set button text based on selected language
        txt = "✅ جوین شدم" if self.lang == "per" else "✅ I've Joined"
        button = InlineKeyboardButton(text=txt, callback_data="proceed")

        return markup.add(button)

    def main_markup(self) -> InlineKeyboardMarkup:
        """
        Create the main reply keyboard markup based on language.

        Returns:
            ReplyKeyboardMarkup: A language-specific main menu keyboard.
        """
        markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

        if self.lang == "per":
            # Persian keyboard layout
            markup.add("📝 ثبت آگهی")
            markup.add("👤 حساب کاربری", "💳 شارژ حساب", "👥 زیرمجموعه‌گیری", "🛠 پشتیبانی")
            markup.add("🌐 /زبان")
        else:
            # English keyboard layout
            markup.add("📝 Submit Ad")
            markup.add("👤 My Account", "💳 Top-up", "👥 Referral", "🛠 Support")
            markup.add("🌐 /language")

        return markup

    def charge_markup(self) -> InlineKeyboardMarkup:
        """
        Create an inline keyboard markup for charge options.

        Returns:
            InlineKeyboardMarkup: A markup with preset charge amount buttons.
        """
        markup = InlineKeyboardMarkup(row_width=3)

        # Set button texts based on language
        txt1 = "۱۰ هزار تومان" if self.lang == "per" else "10,000 Toman"
        txt2 = "۲۰ هزار تومان" if self.lang == "per" else "20,000 Toman"

        # Create buttons for each charge option
        butt_1 = InlineKeyboardButton(text=txt1, callback_data="charge_10")
        butt_2 = InlineKeyboardButton(text=txt2, callback_data="charge_20")

        return markup.add(butt_1, butt_2)
    
    def lang_markup(self) -> InlineKeyboardMarkup:
        """
        Create an inline keyboard markup for language options.

        Returns:
            InlineKeyboardMarkup: A markup with language buttons.
        """
        markup = InlineKeyboardMarkup(row_width=1)
        
        # Prompt user to select their preferred language
        eng_button = InlineKeyboardButton(text="English", callback_data='eng')
        per_button = InlineKeyboardButton(text="فارسی", callback_data="per")
        return markup.add(eng_button, per_button)

# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ

bot = TeleBot(telgram_api, state_storage=state_st, parse_mode="HTML")

# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ

@bot.message_handler(commands=['start'])
def start_command(m: Message):
    """
    Handles the /start command.
    
    Checks the user's language and membership status. If it's a new user, handles referral,
    adds the user to the database, and prompts for language selection. Otherwise, shows the main menu.
    """
    user_id = m.from_user.id

    user_lang = lang_check(user_id)
    if user_lang is None:
        lang = "per"
    else:
        lang = user_lang

    txt = Lang(lang=lang)
    markup = KeyFactory(lang=lang)

    # If the user has not joined the required channels
    if not check_join(user_id=user_id, channels=channels_, bot=bot):
        bot.send_message(m.chat.id, text=txt.get("join_required_message"), reply_markup=markup.proceed_markup())
        return

    # If the user is messaging the bot for the first time
    if user_lang is None:
        token = m.text.split()
        if len(token) > 1:
            # If the user joined via someone’s referral link
            gift = 10000
            get_referral(token=token[1], gift=gift)
            bot.send_message(chat_id=token[1], text=f"🎁 referral gift + <code>{gift}</code>")

        # Add the new user to the users table
        add_new_member(user_id=user_id)

        bot.send_message(m.chat.id, text="کاربر عزیز لطفا زبان خود را انتخاب کنید:\n\nDear user, please select your language.", reply_markup=markup.lang_markup())
        return

    # If user is already registered in the database
    bot.send_message(chat_id=user_id, text=txt.get("welcome_message"), reply_markup=markup.main_markup())
    
# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ

@bot.callback_query_handler(func=lambda call: call.data in ["per", "eng"])
def lang_callback_button(call: CallbackQuery):
    """
    Handles language selection button presses (English or Persian).
    
    Updates the user's preferred language in the database.
    If successful, sends a welcome message in the selected language.
    """
    
    # Selected language from the callback data
    data = call.data
    user_id = call.from_user.id

    txt = Lang(data)
    markup = KeyFactory(data)

    # Attempt to change user's language in database
    if not change_lang(user_id=user_id, lang=data):
        # If language update fails, send a generic error message
        bot.send_message(chat_id=user_id, text=txt.get("error_generic"))
        return
    
    # Show success message as popup (not alert)
    bot.answer_callback_query(callback_query_id=call.id, text=txt.get("success_msg"), show_alert=False)
    
    # Send welcome message in the newly selected language
    bot.send_message(chat_id=user_id, text=txt.get("welcome_message"), reply_markup=markup.main_markup())
    

# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ

@bot.message_handler(func=lambda m: m.text in ["👤 حساب کاربری", "👤 My Account"])
def account(m: Message):
    """
    Handles the 'My Account' button click.
    
    Retrieves and sends the user's account information including name, user ID, and balance.
    """

    # Get user ID and name from the message
    user_id = m.from_user.id
    user_name = m.from_user.first_name

    # Language handler instance
    lang = lang_check(user_id)
    txt = Lang(lang=lang)

    # Fetch user balance
    balance = user_balance(user_id)
    if balance is None:
        # If user not found or an error occurred, send generic error message
        bot.send_message(chat_id=user_id, text=txt.get("error_generic"))
        return

    # Generate and send user account information message
    msg = txt.get("account_info") % (user_id, user_name, user_id, balance)
    bot.send_message(chat_id=user_id, text=msg)
    
# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ

@bot.message_handler(func=lambda m: m.text in ("🌐 /زبان", "🌐 /language"))
def language(m: Message):
    user_id = m.from_user.id
    
    lang = lang_check(user_id)
    markup = KeyFactory(lang=lang)
    
    bot.send_message(m.chat.id, text="کاربر عزیز لطفا زبان خود را انتخاب کنید:\n\nDear user, please select your language.", reply_markup=markup.lang_markup())

# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ

@bot.message_handler(func=lambda m: m.text in ["🛠 پشتیبانی", "🛠 Support"])
def support_message(m: Message):
    """
    Handles initial support request from the user.
    Prompts user to send a message to be forwarded to the admin.
    """
    user_id = m.from_user.id

    # Detect user language and initialize message text generator
    lang = lang_check(user_id)
    txt = Lang(lang=lang)

    # Ask user to send their support message
    bot.send_message(chat_id=user_id, text=txt.get("send_your_message"))

    # Set bot state to wait for user support message
    bot.set_state(user_id=m.from_user.id, state=Support.text, chat_id=user_id)

# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ

@bot.message_handler(state=Support.text)
def support_txt(m: Message):
    """
    Receives user's support message and sends it to the admin
    with a reply button. Then notifies the user.
    """
    user_id = m.from_user.id

    # Create inline keyboard for admin to respond
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text="پاسخ", callback_data=f"{user_id}_admin")
    markup.add(button)

    # Send user's message to the admin
    bot.send_message(
        chat_id=admin_id,
        text=f"""پیامی از کاربر با ای دی <code>{user_id}</code> با یوزرنیم @{m.from_user.username}:\nمتن پیام:\n
<b>{escape_special_characters(m.text)}</b>""",
        reply_markup=markup,
        parse_mode="HTML"
    )

    # Initialize localized text
    lang = lang_check(user_id)
    txt = Lang(lang=lang)

    # Notify user that the message was sent
    bot.send_message(chat_id=m.chat.id, text=txt.get("message_sent_to_admin"))

    # Save the user's message in a temporary dictionary
    texts[user_id] = m.text

    # Clear the bot's waiting state for this user
    bot.delete_state(user_id=user_id, chat_id=m.chat.id)

# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ

@bot.callback_query_handler(func=lambda call: "admin" in call.data)
def admin_answer(call: CallbackQuery):
    """
    Triggered when admin clicks the reply button.
    Asks admin to send a response to the user.
    """
    # Extract user ID from callback data
    user_id = int(call.data.split("_")[0])
    
    # Delete Reply Button
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)

    # Prompt admin to write a reply to the user
    bot.send_message(chat_id=call.message.chat.id, text=f"پیام خود را به <code>{user_id}</code> بنویسید.")

    # Store the user ID for reply tracking
    chat_ids.append(user_id)

    # Set bot state to wait for admin's reply
    bot.set_state(user_id=call.from_user.id, state=Support.respond, chat_id=call.message.chat.id)

# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ

@bot.message_handler(state=Support.respond)
def answer_txt(m: Message):
    """
    Receives the admin's reply and sends it to the user.
    Cleans up tracking data after response is sent.
    """
    chat_id = chat_ids[-1]

    lang = lang_check(chat_id)
    txt = Lang(lang=lang)

    if chat_id in texts:
        # Format and send the admin's response to the user
        msg = txt.get("admin_respond") % (escape_special_characters(texts[chat_id]), escape_special_characters(m.text))
        bot.send_message(chat_id=chat_id, text=msg)

        # Notify the admin that response was sent
        bot.send_message(chat_id=admin_id, text="پاسخ شما ارسال شد.")

        # Remove temporary message and ID
        del texts[chat_id]
        chat_ids.remove(chat_id)

    else:
        # Error if original message is not found
        bot.send_message(chat_id=admin_id, text="مشکلی پیش آمده...\nلطفا دوباره امتحان کنید.")

    # Clear the bot state for the admin
    bot.delete_state(user_id=m.from_user.id, chat_id=m.chat.id)

# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ
"زیرمجموعه گیری"
@bot.message_handler(func=lambda m: m.text in ("👥 زیرمجموعه‌گیری", "👥 Referral"))
def referral(m):
    """Send the user their referral link and image."""

    # Get user ID
    user_id = m.from_user.id

    # Generate localized message text
    lang = lang_check(user_id)
    txt = Lang(lang=lang)

    # Prepare referral message with image
    caption = txt.get("referral_link") % (user_id, user_id)
    try:
        with open("referral.png", "rb") as photo:
            bot.send_photo(chat_id=user_id, photo=photo, caption=caption)
    # If File Dose Not Exist
    except Exception as e:
        bot.send_message(chat_id=user_id, text=txt.get("error_generic"))

# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ
"ثبت آگهی"
@bot.message_handler(func=lambda m: m.text in ("📝 Submit Ad", "📝 ثبت آگهی"))
def get_agahi(m: Message):
    """Prompt the user to submit their advertisement content."""

    # Get user ID
    user_id = m.from_user.id

    # Generate localized message text
    lang = lang_check(user_id)
    txt = Lang(lang=lang)
    
    # Check If User Allowed To Send Content
    balance = user_balance(user_id)
    if balance < advertisement_fee:
        bot.send_message(chat_id=user_id, text=txt.get("does_not_have_enough_balance"))
        return

    # Prompt user to send the ad content
    bot.send_message(chat_id=user_id, text=txt.get("send_ad_prompt"))

    # Set state to receive the ad content
    bot.set_state(chat_id=m.chat.id, state=Support.agahi, user_id=user_id)
    
# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ

@bot.message_handler(state=Support.agahi)
def get_agahi_2(m: Message):
    """Receive user-submitted ad and forward it to admin for approval."""

    # User ID
    user_id = m.from_user.id

    # Language and text generator
    lang = lang_check(user_id)
    txt = Lang(lang=lang)

    # Admin approval buttons
    markup = InlineKeyboardMarkup()
    button_1 = InlineKeyboardButton(text="رد کردن", callback_data=f"denie_{user_id}")
    button_2 = InlineKeyboardButton(text="تایید کردن", callback_data=f"confirm_{user_id}")
    markup.add(button_1, button_2)

    # Forward user's message to admin
    forwarded_m = bot.forward_message(chat_id=admin_id, from_chat_id=m.chat.id, message_id=m.message_id)

    # Notify admin with user ID and action buttons
    bot.send_message(
        chat_id=admin_id,
        text=f"📬 <b>یک کاربر درخواست ثبت آگهی دارد:</b>\n\n🆔 شناسه کاربر: <code>{user_id}</code>",
        reply_markup=markup,
        reply_to_message_id=forwarded_m.message_id
    )

    # Notify user their ad is pending review
    bot.send_message(chat_id=m.chat.id, text=txt.get("ad_pending_review"))

    # Clear user state
    bot.delete_state(user_id=m.from_user.id, chat_id=m.chat.id)

# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ

@bot.callback_query_handler(lambda call: "denie" in call.data)
def denie(call: CallbackQuery):
    """Handle admin rejection of ad submission."""

    admin_id = call.from_user.id

    # Extract user ID from admin message
    user_id = int(call.data.split("_")[1])

    # Language and text generator
    lang = lang_check(user_id)
    txt = Lang(lang=lang)

    # Replace admin buttons with a confirmation label
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text="با موفقیت رد شد.", callback_data="a")
    markup.add(button)

    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)

    # Notify user of rejection
    bot.send_message(chat_id=user_id, text=txt.get("request_rejected"))

# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ

@bot.callback_query_handler(lambda call: "confirm" in call.data)
def confirm(call: CallbackQuery):
    """Handle admin approval of ad and publish it to the channel."""

    admin_id = call.from_user.id

    # Extract user ID from admin message
    user_id = int(call.data.split("_")[1])

    # Language and text generator
    lang = lang_check(user_id)
    txt = Lang(lang=lang)

    # Deduct user's balance for ad submission
    pay_status = advertise_pay(user_id=user_id)
    if not pay_status:
        bot.send_message(chat_id=admin_id, text=Lang().get("error_generic"))
        return

    # Publish the user's ad to the channel
    bot.copy_message(
        chat_id=channel_id,
        from_chat_id=call.message.chat.id,
        message_id=call.message.reply_to_message.message_id
    )

    # Replace admin buttons with a confirmation label
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text="با موفقیت تایید شد", callback_data="a")
    markup.add(button)

    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)

    # Notify user of successful submission
    bot.send_message(chat_id=user_id, text=txt.get("ad_submitted_success"))
    
# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ

@bot.message_handler(func=lambda m: m.text in ("💳 Top-up", "💳 شارژ حساب"))
def charge_account(m: Message):
    """Prompt user to choose a top-up amount."""
    
    # Extract user ID from admin message
    user_id = m.from_user.id

    # Language and text generator
    lang = lang_check(user_id)
    txt = Lang(lang=lang)

    # Create inline buttons for recharge options
    markup = KeyFactory(lang=lang)

    bot.send_message(chat_id=user_id, text=txt.get("charge_prompt"), reply_markup=markup.charge_markup())


# ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ

@bot.callback_query_handler(func=lambda call: call.data.startswith("charge_"))
def handle_charge(call):
    """Handle charge selection and send payment link."""

    user_id = call.from_user.id
    amount_label = call.data.split("_")[1]
    
    # Language and text generator
    lang = lang_check(user_id)
    txt = Lang(lang=lang)

    # Validate amount and convert to integer
    if amount_label not in ["10", "20"]:
        bot.answer_callback_query(call.id, text=txt.get("error_generic"))
        return

    amount = int(amount_label) * 1000

    # Create payment button with link
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton(
        text="پرداخت" if lang == "per" else "pay",
        url=f"https://your_site_address/zarinpal/request/?user={user_id}&amount={amount}"
    )
    markup.add(button)

    bot.send_message(chat_id=user_id, text=txt.get("pay"), reply_markup=markup)
    
    
if __name__ == "__main__":
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.infinity_polling()