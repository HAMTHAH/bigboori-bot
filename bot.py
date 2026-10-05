import os
import json
import random
import asyncio
from pathlib import Path
from telegram import Update, Bot
from telegram.ext import Application, ContextTypes, MessageHandler, filters

SOURCE_CHANNEL_ID = int(os.environ["SOURCE_CHANNEL_ID"])
TARGET_CHANNEL = os.environ.get("TARGET_CHANNEL", "@bigboori")
POST_INTERVAL = 2000
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
"Careful… staring this long might become a habit. 😏🔥 @bigboori",
"Be honest… you already looked twice. 👀❤️ @bigboori",
"I was going to scroll, but then this happened. 😮‍💨🔥 @bigboori",
"Some views deserve a second look… and a third. 😏👀 @bigboori",
"Too gorgeous to simply scroll past. 🔥😍 @bigboori",
"Your eyes called… they want another look. 😉💋 @bigboori",
"If beauty was a crime, this would be a serious case. 😏🔥 @bigboori",
"Warning: dangerously easy on the eyes. 🚨😍 @bigboori",
"One look was definitely not enough. 👀🔥 @bigboori",
"Stop scrolling… your favorite view just arrived. 😏❤️ @bigboori",
"This much confidence should come with a warning label. 🔥😮‍💨 @bigboori",
"I don't believe in love at first sight… but I'm reconsidering. 😉❤️ @bigboori",
"Somebody understood the assignment a little too well. 😏🔥 @bigboori",
"The camera definitely had a favorite today. 👀😍 @bigboori",
"Your timeline just got a whole lot more interesting. 🔥😏 @bigboori",
"Tell me you noticed without telling me you noticed. 👀❤️ @bigboori",
"This is what I call a serious distraction. 😮‍💨🔥 @bigboori",
"Scrolling suddenly feels like the wrong decision. 😉🔥 @bigboori",
"Some pictures don't need words. This is one of them. 😏👀 @bigboori",
"Your thumb can wait… this deserves a moment. ❤️‍🔥👀 @bigboori",
"Main-character energy from every angle. 😍🔥 @bigboori",
"Too much charm for one picture. 😏💋 @bigboori",
"This post just raised the temperature. 🥵🔥 @bigboori",
"Somebody turn down the heat… actually, don't. 😏🔥 @bigboori",
"If temptation had a profile picture… 👀😈 @bigboori",
"This is your sign to stop scrolling. 😉🔥 @bigboori",
"One picture, zero words needed. 😮‍💨❤️ @bigboori",
"The view is doing all the talking. 👀🔥 @bigboori",
"Confidence never looked this good. 😏❤️ @bigboori",
"Your feed wasn't ready for this one. 🔥👀 @bigboori",
"Some views are simply impossible to ignore. 😮‍💨😍 @bigboori",
"I suddenly forgot what I was doing. 😏🔥 @bigboori",
"Even the camera looks impressed. 👀❤️ @bigboori",
"Don't blame me if you come back for another look. 😉🔥 @bigboori",
"This deserves a permanent spot in your favorites. 😍❤️ @bigboori",
"That kind of confidence is dangerously attractive. 😏🔥 @bigboori",
"Your eyes definitely weren't ready for this. 👀💋 @bigboori",
"Just when you thought your feed couldn't get better… 😮‍💨🔥 @bigboori",
"Somebody brought the heat today. 🥵❤️ @bigboori",
"This is almost unfair to the rest of the timeline. 😏🔥 @bigboori",
"Tell your scrolling finger to take a break. 😉👀 @bigboori",
"Beauty with a little attitude hits different. 😍🔥 @bigboori",
"This picture knows exactly what it's doing. 😏💋 @bigboori",
"Not every distraction is a bad thing. 👀❤️ @bigboori",
"The timeline just got a little hotter. 🔥😮‍💨 @bigboori",
"Your favorite notification just arrived. 😉🔥 @bigboori",
"Somebody clearly woke up feeling dangerous. 😈❤️ @bigboori",
"Looking this good should require a license. 😏🔥 @bigboori",
"I'd say don't stare… but who am I kidding? 👀😍 @bigboori",
"This is what stopping the scroll looks like. 🔥😉 @bigboori",
"Consider this your daily dose of temptation. 😏💋 @bigboori",
"One glance and suddenly it's your new favorite post. 👀❤️ @bigboori",
"Too much beauty in one frame. 😮‍💨🔥 @bigboori",
"The camera caught something special today. 😍👀 @bigboori",
"Somebody is making scrolling very difficult. 😏🔥 @bigboori",
"That look deserves its own fan club. 😉❤️ @bigboori",
"This post came with absolutely no warning. 🚨🔥 @bigboori",
"Your feed just got a little more dangerous. 😈👀 @bigboori",
"Can't decide what's better: the confidence or the view. 😏😍 @bigboori",
"Your eyes can thank me later. 😉🔥 @bigboori",
"This is why we can't have boring timelines. 😮‍💨❤️ @bigboori",
"Absolutely unfair to everyone trying to concentrate. 👀🔥 @bigboori",
"Somebody forgot to turn down the charm. 😏💋 @bigboori",
"This is your reminder that confidence is attractive. 🔥❤️ @bigboori",
"Just casually stealing everyone's attention. 👀😍 @bigboori",
"Scroll responsibly… if that's even possible. 😏🔥 @bigboori",
"The kind of post that makes you forget what you were looking for. 😮‍💨👀 @bigboori",
"One second turned into a full appreciation session. 😂🔥 @bigboori",
"This view deserves VIP treatment. 😏❤️ @bigboori",
"Your algorithm finally did something right. 👀🔥 @bigboori",
"Someone definitely understood the assignment. 😍💋 @bigboori",
"Too stunning to be just another post. 😮‍💨❤️ @bigboori",
"Don't pretend you didn't stop scrolling. 😉🔥 @bigboori",
"This picture has serious main-character energy. 👀😍 @bigboori",
"Beauty, confidence, and a little trouble. 😈🔥 @bigboori",
"Your eyes just found their favorite corner of the internet. 😏❤️ @bigboori",
"Some pictures deserve to be admired slowly. 👀🔥 @bigboori",
"Now that's how you make an entrance. 😮‍💨😍 @bigboori",
"Your timeline needed this little distraction. 😉💋 @bigboori",
"This is the kind of view you don't forget. 🔥❤️ @bigboori",
"Somebody came prepared to steal the spotlight. 😏👀 @bigboori",
"Too much attitude for one frame. 😈🔥 @bigboori",
"That confidence is doing all the flirting. 😉❤️ @bigboori",
"I think we found today's favorite post. 😍🔥 @bigboori",
"This picture deserves more than one look. 👀💋 @bigboori",
"Don't rush… enjoy the view. 😏🔥 @bigboori",
"Your scroll break starts right here. 😮‍💨❤️ @bigboori",
"The definition of impossible to ignore. 👀🔥 @bigboori",
"Somebody just made the internet a little prettier. 😍❤️ @bigboori",
"Confidence looks dangerously good from here. 😏🔥 @bigboori",
"This post has no business being this attractive. 👀💋 @bigboori",
"Your eyes are officially distracted. 😉🔥 @bigboori",
"A little beauty for your timeline. 😮‍💨❤️ @bigboori",
"Who needs a caption when the picture says everything? 😏👀 @bigboori",
"This one deserves a double tap and a second look. 🔥😍 @bigboori",
"Your feed just found its new favorite distraction. 😉❤️ @bigboori",
"Keep scrolling if you can… I don't think you can. 😏🔥 @bigboori",
"That smile, that confidence, that whole vibe. 😍💋 @bigboori",
"Today's forecast: 100% chance of distraction. 🥵🔥 @bigboori",
"Proof that confidence can be seriously attractive. 😏❤️ @bigboori",
"One picture. One problem. You can't stop looking. 👀🔥 @bigboori",
"Welcome to the part of your feed you won't forget. 😮‍💨😍 @bigboori",
"Some views are worth getting lost in. 😏❤️ @bigboori",
"Your daily reminder to appreciate a beautiful view. 👀🔥 @bigboori",
"Okay… who allowed this much beauty on my timeline? 😍🔥 @bigboori",
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
