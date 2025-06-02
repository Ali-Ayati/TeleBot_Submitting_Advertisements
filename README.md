# Telegram Bot: Multi-language Referral & Ad Management System

A feature-rich Telegram bot built using Python and `pyTelegramBotAPI`, designed for multi-language user interaction, referral tracking, advertisement submission, and admin support handling.

## 🚀 Features

### 🌍 Multilingual Support
- Language selection (Persian 🇮🇷 / English 🇬🇧)
- Dynamic message rendering based on user preference

### 👥 User Management
- `/start` command detects new users
- Referral system with bonus credit (e.g. `?start=123456789`)
- Stores users in database with language preference
- Shows account details including balance

### 🔗 Referral System
- Each user gets a personal invite link
- Referrer receives bonus credit upon new user joining
- Visual referral card (image + link)

### 📝 Advertisement System
- Users can submit ads if they have enough balance
- Ads are reviewed and approved/rejected by admin
- Approved ads are published to a specified channel
- Balance is automatically deducted upon approval

### 💳 Account Charging
- Interactive inline buttons for choosing top-up amounts
- Prepared for payment integration

### 🛠 Support System
- Users can send support requests
- Admins receive the message with a reply button
- Admin responses are relayed back to the user with formatting

## 🧠 Bot States & Logic

Bot uses `telebot`'s built-in state management to handle:
- Language selection
- Support messaging
- Ad submission & moderation
- Admin replies

## 🛡️ Admin Tools

- View and respond to support messages
- Approve/deny ad submissions
- Manage user requests with inline keyboard buttons

## 📦 Tech Stack

- **Language:** Python 3.10+
- **Library:** `pyTelegramBotAPI`
- **Database:** MySQL or SQLite (with helper functions like `add_new_member`, `user_balance`, etc.)
- **Message Handling:** Inline & reply keyboards, callback queries
- **State Management:** `bot.set_state`, `bot.delete_state`

## 📁 Project Structure
.
├── config/                        
│   ├── config.py                 # Contains database credentials, admin list, join channels, and other settings
│   ├── functions.py              # Helper functions and a class for generating user-language-based messages
│   └── __init__.py
│
├── support_by_db/                
│   ├── support_with_db.py        # Handles support messages and interactions with related tables
│   ├── CREATE_TB_admins.sql      # SQL script to create the admins table
│   └── CREATE_TB_EVENT_MANAGEMENT.sql # SQL script to create the event management table
│
├── CREATE_DB.sql                 # SQL script to create the database
├── CREATE_TB_USERS.sql           # SQL script to create the users table
│
├── main.py                       # Main entry point of the bot
├── zarin_pal_connector.py        # Zarinpal payment gateway integration using Flask
├── requirements.txt              # List of required Python packages
└── referral.png                  # Image used for visual referral link

---------
---------

# ربات تلگرام: سیستم چندزبانه ارجاع و مدیریت آگهی

رباتی قدرتمند و چندزبانه برای تلگرام که با استفاده از Python و کتابخانه `pyTelegramBotAPI` ساخته شده و قابلیت‌هایی از جمله مدیریت کاربران، پیگیری ارجاع، ثبت آگهی و پشتیبانی ادمین‌ها را فراهم می‌کند.

## 🚀 امکانات

### 🌍 پشتیبانی از چند زبان
- انتخاب زبان (فارسی 🇮🇷 / انگلیسی 🇬🇧)
- نمایش پیام‌ها بر اساس زبان انتخابی کاربر

### 👥 مدیریت کاربران
- شناسایی کاربران جدید با دستور `/start`
- سیستم ارجاع با اعتبار هدیه (مثلاً: `?start=123456789`)
- ذخیره کاربران در دیتابیس همراه با زبان انتخابی
- نمایش جزئیات حساب از جمله موجودی

### 🔗 سیستم ارجاع
- هر کاربر لینک اختصاصی دعوت دارد
- معرف با ورود کاربر جدید اعتبار هدیه دریافت می‌کند
- کارت ارجاع گرافیکی شامل تصویر و لینک

### 📝 سیستم ثبت آگهی
- ارسال آگهی توسط کاربر در صورت داشتن اعتبار کافی
- بررسی و تأیید/رد آگهی توسط ادمین
- ارسال آگهی‌های تأییدشده در کانال مشخص
- کسر خودکار اعتبار در صورت تأیید

### 💳 شارژ حساب
- دکمه‌های اینلاین برای انتخاب مبلغ شارژ
- آماده‌سازی برای اتصال به درگاه پرداخت

### 🛠 سیستم پشتیبانی
- ارسال درخواست پشتیبانی توسط کاربران
- دریافت پیام توسط ادمین با دکمه پاسخ
- ارسال پاسخ ادمین به کاربر با فرمت مناسب

## 🧠 مدیریت وضعیت ربات

ربات از مدیریت وضعیت داخلی `telebot` برای کنترل موارد زیر استفاده می‌کند:
- انتخاب زبان
- پیام‌های پشتیبانی
- ارسال و بررسی آگهی
- پاسخ ادمین‌ها

## 🛡️ ابزارهای ادمین

- مشاهده و پاسخ به پیام‌های پشتیبانی
- تأیید یا رد آگهی‌ها
- مدیریت درخواست‌ها با دکمه‌های اینلاین

## 📦 تکنولوژی‌های استفاده شده

- **زبان:** Python 3.10+
- **کتابخانه:** `pyTelegramBotAPI`
- **دیتابیس:** MySQL یا SQLite (با توابع کمکی مانند `add_new_member`, `user_balance` و ...)
- **مدیریت پیام‌ها:** دکمه‌های اینلاین و ریپلای، callback query
- **مدیریت وضعیت:** `bot.set_state`, `bot.delete_state`

## 📁 ساختار پروژه
.
├── config/
│ ├── config.py # اطلاعات اتصال به دیتابیس، لیست ادمین‌ها، کانال‌های اجباری و سایر تنظیمات
│ ├── functions.py # توابع کمکی و کلاس ساخت پیام بر اساس زبان کاربر
│ └── init.py
│
├── support_by_db/
│ ├── support_with_db.py # مدیریت پیام‌های پشتیبانی با استفاده از دیتابیس
│ ├── CREATE_TB_admins.sql # ساخت جدول ادمین‌ها
│ └── CREATE_TB_EVENT_MANAGEMENT.sql # ساخت جدول مدیریت ایونت‌ها
│
├── CREATE_DB.sql # اسکریپت ساخت دیتابیس
├── CREATE_TB_USERS.sql # ساخت جدول کاربران
│
├── main.py # فایل اصلی اجرای ربات
├── zarin_pal_connector.py # اتصال به درگاه زرین‌پال با استفاده از Flask
├── requirements.txt # لیست پکیج‌های مورد نیاز پروژه
└── referral.png # تصویر کارت ارجاع برای ارسال به کاربر
