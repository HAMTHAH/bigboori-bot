import os
import json
import random
import asyncio
from pathlib import Path
from telegram import Update, Bot
from telegram.ext import Application, ContextTypes, MessageHandler, filters

SOURCE_CHANNEL_ID = int(os.environ["SOURCE_CHANNEL_ID"])
TARGET_CHANNEL = os.environ.get("TARGET_CHANNEL", "@bigboori")
POST_INTERVAL = 600
DATA_DIR = Path("/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_FILE = DATA_DIR / "photos.json"

CAPTIONS = [
    "Curves doing all the talking. 👀🔥 @bigboori",
    "That view deserves a second look. 😮‍💨 @bigboori",
    "Just casually stealing the spotlight. 👀🔥 @bigboori",
    "Confidence looks good from every angle. 🔥 @bigboori",
    "The view is definitely worth stopping for. 👀 @bigboori",
    "A little reminder that curves never go unnoticed. 😮‍💨 @bigboori",
    "Serving looks without saying a word. 🔥 @bigboori",
    "Some pictures simply demand a second look. 👀 @bigboori",
    "Main character energy. 🔥 @bigboori",
    "The kind of post that makes you pause the scroll. 👀 @bigboori",
    "No explanation needed. Just enjoy the view. 😮‍💨 @bigboori",
    "Scroll carefully… you might miss the best part. 👀🔥 @bigboori",
    "Too much confidence for one picture. 🔥 @bigboori",
    "Consider this your sign to stop scrolling. 👀 @bigboori",
    "A whole lot of attitude in one frame. 😮‍💨🔥 @bigboori",
    "Curves and confidence — dangerous combination. 👀 @bigboori",
    "Definitely not an ordinary scroll. 🔥 @bigboori",
    "The timeline just got a little more interesting. 👀 @bigboori",
    "Serving a look from every angle. 😮‍💨 @bigboori",
    "One picture, zero words needed. 👀🔥 @bigboori",
]

def load_db():
    if not DB_FILE.exists():
        return {"photos": [], "posted": []}
    try:
        return json.loads(DB_FILE.read_text())
    except Exception:
        return {"photos": [], "posted": []}

def save_db(db):
    tmp = DB_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(db))
    tmp.replace(DB_FILE)

async def collect_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.channel_post
    if not msg or msg.chat_id != SOURCE_CHANNEL_ID or not msg.photo:
        return

    # Telegram gives the highest-resolution photo as the last item.
    file_id = msg.photo[-1].file_id
    db = load_db()

    if not any(p["file_id"] == file_id for p in db["photos"]):
        db["photos"].append({
            "file_id": file_id,
            "source_message_id": msg.message_id
        })
        save_db(db)
        print(f"Saved new photo {msg.message_id}. Total: {len(db['photos'])}")

async def post_one(context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    photos = db["photos"]
    posted = set(db.get("posted", []))

    available = [p for p in photos if p["file_id"] not in posted]

    # Start a new cycle when every saved photo has been posted.
    if not available:
        posted = set()
        available = photos

    if not available:
        print("No photos collected yet.")
        return

    item = random.choice(available)
    caption = random.choice(CAPTIONS)

    try:
        await context.bot.send_photo(
            chat_id=TARGET_CHANNEL,
            photo=item["file_id"],
            caption=caption
        )
        posted.add(item["file_id"])
        db["posted"] = list(posted)
        save_db(db)
        print("Posted a photo.")
    except Exception as e:
        print(f"Posting error: {e}")

async def startup(context: ContextTypes.DEFAULT_TYPE):
    # Post immediately on first run, then every hour.
    await post_one(context)

def main():
    token = os.environ["BOT_TOKEN"]

    app = (
        Application.builder()
        .token(token)
        .build()
    )

    # Channel posts are delivered to bots that are administrators of the source channel.
    app.add_handler(
        MessageHandler(filters.UpdateType.CHANNEL_POST & filters.PHOTO, collect_photo)
    )

    app.job_queue.run_once(startup, when=5)
    app.job_queue.run_repeating(post_one, interval=POST_INTERVAL, first=POST_INTERVAL)

    print("BigBoori poster is running.")
    app.run_polling(allowed_updates=["channel_post"])

if __name__ == "__main__":
    main()
