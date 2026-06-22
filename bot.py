import requests
import asyncio
from telegram import Bot
from telegram.ext import Application, CommandHandler
import datetime
import feedparser
import time
import threading

# ===== আপনার তথ্য =====
BOT_TOKEN = "8679826654:AAFsDg8Hr7FdcC-KOA1VJFN3WuWDE30Dwt0"
CHAT_ID = 7057782214
# =====================

# বাংলা টেক নিউজের RSS ফিড
RSS_FEEDS = [
    "https://www.prothomalo.com/feed/technology",
    "https://www.bbc.com/bengali/technology/index.xml",
    "https://www.tbsnews.net/technology/rss.xml"
]

async def get_news():
    """RSS ফিড থেকে নিউজ আনা"""
    news_list = []
    
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:3]:
                news_list.append({
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.get("published", "সময় জানা নেই")
                })
        except Exception as e:
            print(f"⚠️ ফিড লোড করতে সমস্যা: {e}")
            continue
    
    return news_list[:8]

async def send_news(context=None):
    """নিউজ পাঠানোর ফাংশন"""
    bot = Bot(token=BOT_TOKEN)
    news_items = await get_news()
    
    if not news_items:
        await bot.send_message(
            chat_id=CHAT_ID,
            text="😅 ক্ষমা চাই, এখন নতুন কোনো টেক নিউজ নেই! পরে আবার চেষ্টা করবেন।"
        )
        return
    
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    await bot.send_message(
        chat_id=CHAT_ID,
        text=f"📡 *বাংলা টেক নিউজ*\n🕐 {current_time}\n━━━━━━━━━━━━━━━",
        parse_mode='Markdown'
    )
    
    for idx, news in enumerate(news_items, 1):
        message = f"*{idx}. {news['title']}*\n🔗 [বিস্তারিত পড়ুন]({news['link']})"
        await bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
        await asyncio.sleep(1)

async def start(update, context):
    """start কমান্ডের রেসপন্স"""
    await update.message.reply_text(
        "🙏 *স্বাগতম!*\n\n"
        "আমি *Techsudo Bot* - বাংলায় টেক নিউজ পাঠাই।\n\n"
        "📌 *কীভাবে কাজ করি?*\n"
        "• প্রতি ২ ঘণ্টা পরপর নতুন নিউজ পাঠাই\n"
        "• RSS ফিড থেকে সংগৃহীত খবর\n"
        "• শুধু প্রযুক্তি বিষয়ক নিউজ\n\n"
        "🔔 চালু থাকতে /news কমান্ড দিন",
        parse_mode='Markdown'
    )

async def news_command(update, context):
    """news কমান্ডের রেসপন্স"""
    await update.message.reply_text("⏳ নিউজ সংগ্রহ করা হচ্ছে... দয়া করে অপেক্ষা করুন।")
    await send_news(context)

def schedule_news():
    """threading দিয়ে প্রতি ২ ঘণ্টা পরপর নিউজ পাঠানো"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    while True:
        try:
            loop.run_until_complete(send_news())
            print(f"✅ নিউজ পাঠানো হয়েছে: {datetime.datetime.now()}")
        except Exception as e:
            print(f"❌ এরর: {e}")
        time.sleep(7200)

def main():
    """বট চালু করা"""
    news_thread = threading.Thread(target=schedule_news, daemon=True)
    news_thread.start()
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("news", news_command))
    
    print("🤖 বট চালু হচ্ছে...")
    print(f"📱 আপনার বট: t.me/Techsudobot")
    print("⏰ প্রতি ২ ঘণ্টা পরপর নিউজ যাবে!")
    
    app.run_polling()

if __name__ == "__main__":
    main()