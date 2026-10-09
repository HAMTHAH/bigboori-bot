import os
import json
import random
from pathlib import Path

from telegram import Update
from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
    filters,
)

# ============================================================
# SETTINGS
# ============================================================

BOT_TOKEN = os.environ["BOT_TOKEN"]
SOURCE_CHANNEL_ID = int(os.environ["SOURCE_CHANNEL_ID"])
TARGET_CHANNEL = os.environ.get("TARGET_CHANNEL", "@bigboori")

POST_INTERVAL = 2 * 60 * 60  # Every 2 hours

# ============================================================
# DATABASE
# ============================================================

DATA_DIR = Path("/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_FILE = DATA_DIR / "photos.json"


def load_db():
    if not DB_FILE.exists():
        return {"photos": [], "posted": []}

    try:
        data = json.loads(DB_FILE.read_text())
        data.setdefault("photos", [])
        data.setdefault("posted", [])
        return data
    except (json.JSONDecodeError, OSError) as error:
        print(f"Database error: {error}")
        return {"photos": [], "posted": []}


def save_db(db):
    temp_file = DB_FILE.with_suffix(".tmp")
    temp_file.write_text(json.dumps(db, indent=2))
    temp_file.replace(DB_FILE)


# ============================================================
# CAPTIONS
# ============================================================

CAPTIONS = [
    "Pretty face. Dangerous curves. Bad intentions. 🖤",
    "You looked once. That was your first mistake. 😏",
    "Not a thirst trap. A whole drought. 🔥",
    "Your self-control just left the chat. 👀",
    "Handle with caution. Curves have consequences.",
    "Sweet smile, savage energy. 😈",
    "I'm not responsible for where your eyes wander.",
    "Too much curve for a quiet entrance. 🔥",
    "Your favorite distraction has entered the room. 👀",
    "Don't stare too long. You might get attached. 😏",
    "Confidence looks better from this angle. 🔥",
    "I came to ruin your scrolling.",
    "Your weakness has a silhouette. 🖤",
    "Some views deserve absolutely no explanation.",
    "Caught you looking. Again. 👀",
    "Beautiful enough to tempt, savage enough to disappear.",
    "Your screen time is about to become embarrassing. 😏",
    "A little evil, a lot of curves. 😈",
    "You weren't ready for this timeline. 🔥",
    "The kind of distraction you secretly wanted.",
    "No warning label was going to save you. 🖤",
    "Curves sharper than my attitude.",
    "Scroll away. I dare you. 👀",
    "Your eyes have expensive taste. 😏",
    "I don't chase attention. I collect it. 🔥",
    "Serving looks with a side of trouble. 😈",
    "You can blame the algorithm.",
    "Too confident to be ignored. 🖤",
    "A dangerous amount of pretty. 🔥",
    "Your favorite bad decision looks like this.",
    "One post closer to losing your focus. 👀",
    "Keep staring. I know you want to. 😏",
    "Cute enough to distract, savage enough to haunt.",
    "This is what 'handle with care' looks like. 🖤",
    "No caption can compete with the view.",
    "Your patience deserves a challenge. 🔥",
    "A little mystery makes the curves hit harder.",
    "I'm the reason you forgot why you opened the app. 👀",
    "Not everyone deserves this view.",
    "Eyes up... if you can manage it. 😏",
    "Your attention has officially been stolen.",
    "Curves with criminal intentions. 🔥",
    "I bring the trouble. The curves bring the witnesses. 😈",
    "Danger never looked this comfortable.",
    "You're staring like there's a prize. 👀",
    "Your feed just got a lot more interesting.",
    "Too bold for boring timelines. 🖤",
    "This post comes with zero regrets.",
    "Call it temptation. I call it confidence. 🔥",
    "I don't need an introduction. The silhouette says enough.",
    "You can scroll, but you'll probably come back. 😏",
    "Built to be remembered.",
    "A little toxic, a lot unforgettable. 🖤",
    "Your eyes already picked a favorite.",
    "Not here to behave. 😈",
    "The kind of post that makes 'just one look' impossible.",
    "Dark energy. Soft smile. Dangerous curves. 🔥",
    "Your attention span never stood a chance.",
    "Some people bring flowers. I bring distractions. 👀",
    "The camera knew exactly what it was doing.",
    "You call it a thirst trap. I call it advertising. 😏",
    "Too much attitude to be innocent.",
    "Look again. I know you did. 👀",
    "A masterpiece with questionable intentions. 🖤",
    "I'm not your type. I'm your exception.",
    "Your weakness just posted again. 🔥",
    "Beautiful chaos, perfectly framed.",
    "The scroll was peaceful before I arrived.",
    "No permission needed to steal the spotlight. 😈",
    "This much confidence should be illegal. 🔥",
    "I leave impressions, not explanations.",
    "You wanted a sign. Here it is. 👀",
    "The view is dangerous after midnight. 🖤",
    "If temptation had a profile picture...",
    "Don't blame me for your imagination. 😏",
    "Your curiosity brought you here. Your eyes kept you here.",
    "A little wicked never hurt anybody. 😈",
    "The kind of pretty that causes problems. 🔥",
    "Your favorite distraction is becoming a habit.",
    "I'm the plot twist your feed needed. 🖤",
    "Too hot for a boring caption. 🔥",
    "Some silhouettes speak louder than words.",
    "You can pretend you're not impressed. 👀",
    "Confidence: dangerously high. 😏",
    "I don't compete. I make comparisons unfair.",
    "The camera caught what the mirror already knew.",
    "Your attention looks good on me. 🔥",
    "A bad influence with excellent curves. 😈",
    "Don't get comfortable. I'm just getting started.",
    "You found the post you weren't supposed to find. 👀",
    "Curves, confidence, and questionable decisions.",
    "Your feed just caught a felony of beauty. 🖤",
    "I could explain the obsession, but the picture already did.",
    "Stay curious. Stay distracted. 😏",
    "Pretty enough to stop traffic. Savage enough to keep it moving.",
    "You came for one post. Good luck leaving. 🔥",
    "The warning was hidden in the curves.",
    "Consider this your final excuse to stare. 🖤🍑",
]

# ============================================================
# COLLECT NEW PHOTOS FROM SOURCE CHANNEL
# ============================================================

async def collect_photo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    message = update.channel_post

    if not message or message.chat_id != SOURCE_CHANNEL_ID:
        return

    if not message.photo:
        return

    file_id = message.photo[-1].file_id
    db = load_db()

    existing_ids = {
        photo["file_id"] for photo in db["photos"]
    }

    if file_id in existing_ids:
        return

    db["photos"].append({
        "file_id": file_id,
        "source_message_id": message.message_id,
    })

    save_db(db)

    print(
        f"Saved new photo: {message.message_id} | "
        f"Total photos: {len(db['photos'])}"
    )


# ============================================================
# POST ONE RANDOM PHOTO
# ============================================================

async def post_one(context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    photos = db["photos"]
    posted = set(db["posted"])

    if not photos:
        print("No photos available yet.")
        return

    available = [
        photo for photo in photos
        if photo["file_id"] not in posted
    ]

    # Start a new cycle after every photo has been used
    if not available:
        print("All photos posted. Starting a new cycle.")
        posted.clear()
        available = photos

    selected = random.choice(available)
    caption = random.choice(CAPTIONS)

    try:
        await context.bot.send_photo(
            chat_id=TARGET_CHANNEL,
            photo=selected["file_id"],
            caption=caption,
        )

        posted.add(selected["file_id"])
        db["posted"] = list(posted)
        save_db(db)

        print("Photo posted successfully.")
        print("Next scheduled post: in 2 hours.")

    except Exception as error:
        print(f"Posting error: {error}")


# ============================================================
# STARTUP
# ============================================================

async def startup_post(context: ContextTypes.DEFAULT_TYPE):
    print("Attempting startup post...")
    await post_one(context)


def main():
    print("================================")
    print("BIGBOORI PHOTO BOT")
    print(f"Target: {TARGET_CHANNEL}")
    print("Interval: 2 hours")
    print("================================")

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(
        MessageHandler(
            filters.UpdateType.CHANNEL_POST & filters.PHOTO,
            collect_photo,
        )
    )

    # Attempt one post shortly after startup
    application.job_queue.run_once(
        startup_post,
        when=5,
    )

    # Then post every 2 hours
    application.job_queue.run_repeating(
        post_one,
        interval=POST_INTERVAL,
        first=POST_INTERVAL,
    )

    print("Bot is running. Posting every 2 hours.")

    application.run_polling(
        allowed_updates=["channel_post"]
    )


if __name__ == "__main__":
    main()
