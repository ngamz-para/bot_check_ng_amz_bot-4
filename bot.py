import os
import re
import requests
import telebot
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7"
}

# ------------------ PARSE INPUT ------------------
def parse_input(text):
    text = text.strip()

    if "facebook.com" in text:
        return text.split("?")[0]

    if text.isdigit():
        return f"https://www.facebook.com/profile.php?id={text}"

    return f"https://www.facebook.com/{text}"

# ------------------ ESTIMATE REG DATE ------------------
def estimate_reg(uid):
    try:
        uid = int(uid)
        if uid < 100000000000000:
            return "~2009-2012"
        elif uid < 1000000000000000:
            return "~2013-2016"
        else:
            return "~2017+"
    except:
        return "Không xác định"


# ------------------ CHECK FACEBOOK ------------------
def check_fb(profile_url):
    r = requests.get(profile_url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    # NAME
    name = "Không xác định"
    if soup.title:
        name = soup.title.text.replace(" | Facebook", "").strip()

    # UID
    uid = "Không xác định"
    m = re.search(r"profile.php\?id=(\d+)", r.text)
    if m:
        uid = m.group(1)

    # USERNAME
    username = "Không có"
    u = re.search(r"https://www.facebook.com/([a-zA-Z0-9\.]+)", profile_url)
    if u and not u.group(1).isdigit():
        username = u.group(1)

    # VERIFIED
    verified = "Chưa xác minh"
    if (
        "Đã xác minh" in r.text
        or "Verified account" in r.text
        or "Blue verified badge" in r.text
        or "aria-label=\"Đã xác minh\"" in r.text
    ):
        verified = "Đã xác minh"

    # FOLLOWER
    follower = "Ẩn"
    f = re.search(r"([0-9\.,]+)\s+người theo dõi", r.text)
    if f:
        follower = f.group(1)

    # FRIENDS
    friends = "Ẩn"
    fr = re.search(r"([0-9\.,]+)\s+bạn bè", r.text)
    if fr:
        friends = fr.group(1)

    # POSTS
    posts = "Ẩn"
    p = re.search(r"([0-9\.,]+)\s+bài viết", r.text)
    if p:
        posts = p.group(1)

    # AVATAR
    avatar = "Không có"
    av = soup.find("img", {"data-imgperflogname": "profileCoverPhoto"})
    if av and av.get("src"):
        avatar = av["src"]

    # COVER
    cover = "Ẩn"
    cv = soup.find("img", {"alt": "Ảnh bìa"})
    if cv and cv.get("src"):
        cover = cv["src"]

    # COUNTRY
    country = "Ẩn"
    if "vi_VN" in r.text:
        country = "Việt Nam"

    return {
        "name": name,
        "uid": uid,
        "username": username,
        "verified": verified,
        "reg_date": estimate_reg(uid),
        "country": country,
        "follower": follower,
        "friends": friends,
        "posts": posts,
        "avatar": avatar,
        "cover": cover,
        "profile": profile_url
    }

# ------------------ BOT HANDLER ------------------
@bot.message_handler(commands=["start"])
def start(m):
    bot.reply_to(
        m,
        "🔍 <b>BOT CHECK FACEBOOK | NGAMZ</b>\n\n"
        "👉 Gửi <b>UID / Username / Link Facebook</b>\n"
        "⚠️ Chỉ check dữ liệu <b>public</b>\n\n"
        "⚡ Dev: @Ngamz"
    )

@bot.message_handler(func=lambda m: True)
def run(m):
    try:
        profile_url = parse_input(m.text)
        info = check_fb(profile_url)
        now = datetime.now().strftime("%d/%m/%Y %H:%M")

        msg = f"""
🔍 <b>FACEBOOK INFO | NGAMZ</b>

👤 <b>Tên:</b> {info['name']}
🆔 <b>UID:</b> {info['uid']}
🔗 <b>Username:</b> {info['username']}
✅ <b>Verified:</b> {info['verified']}

📅 <b>Đăng ký:</b> {info['reg_date']}
🌍 <b>Quốc gia:</b> {info['country']}

👥 <b>Follower:</b> {info['follower']}
👫 <b>Bạn bè:</b> {info['friends']}
📝 <b>Bài viết:</b> {info['posts']}

🖼 <b>Avatar:</b>
{info['avatar']}

🖼 <b>Cover:</b>
{info['cover']}

🔗 <b>Profile:</b>
{info['profile']}

🕒 <i>Cập nhật: {now}</i>
⚡ <b>Bot:</b> @bot_check_ngamz
"""
        bot.reply_to(m, msg)
    except Exception as e:
        bot.reply_to(m, "❌ Không thể check profile này (nick riêng tư hoặc bị chặn)")

# ------------------ RUN ------------------
bot.infinity_polling()
