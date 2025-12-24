import telebot
import requests
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def check_fb(uid):
    url = f"https://www.facebook.com/profile.php?id={uid}"
    r = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    # NAME
    name = "Không xác định"
    if soup.title:
        name = soup.title.text.replace(" | Facebook", "").strip()

    # USERNAME
    username = "Không có username"
    if "facebook.com/" in r.url and "profile.php" not in r.url:
        username = r.url.split("facebook.com/")[-1]

    # VERIFIED
    verified = "Chưa xác minh"
    if "verifiedBadge" in r.text:
        verified = "Đã xác minh"

    # LOCALE / COUNTRY (ước đoán)
    country = "Không xác định"
    if "vi_VN" in r.text:
        country = "Vietnam 🇻🇳"

    # REGISTER DATE (ước đoán)
    reg_date = "Không xác định"
    if uid.isdigit():
        reg_date = "Ước đoán: 2018–2021"

    return {
        "name": name,
        "username": username,
        "verified": verified,
        "country": country,
        "reg_date": reg_date,
        "profile": url
    }

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m,
"""⚡️ BOT CHECK NGAMZ

👉 Gửi UID Facebook để kiểm tra
👉 Chỉ dữ liệu công khai
👉 Không xâm phạm quyền riêng tư
""")

@bot.message_handler(func=lambda m: True)
def run(m):
    uid = m.text.strip()

    if not uid.isdigit():
        bot.reply_to(m, "❌ UID không hợp lệ")
        return

    info = check_fb(uid)
    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    msg = f"""
🔍 FACEBOOK INFO | NGAMZ DEV

👤 Tên: {info['name']}
🆔 UID: {uid}
🔗 Username: {info['username']}
✅ Verified: {info['verified']}

📅 Đăng ký: {info['reg_date']}
🌍 Quốc gia: {info['country']}

👫 Bạn bè: Ẩn
👥 Follower: Ẩn
🚻 Giới tính: Ẩn
🎂 Tuổi: Không xác định
🏠 Quê quán: Ẩn

🔗 Profile:
{info['profile']}

🕒 Cập nhật: {now}
⚡ Admin: @Ngamz
🟢 Trạng thái: Good
"""
    bot.reply_to(m, msg)

bot.polling(none_stop=True)
