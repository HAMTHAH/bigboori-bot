
import os
import json
import random
from pathlib import Path
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.constants import ParseMode
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

POST_INTERVAL = 2 * 60 * 60  # 2 hours
CHANNEL_URL = "https://t.me/bigboori"
CAPTION = f'<a href="{CHANNEL_URL}">βΟΟTΨҒUL</a>'

# Watermark opacity: 0 is invisible, 255 is fully opaque
WATERMARK_OPACITY = 45

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
# WATERMARK
# ============================================================

def add_watermark(image_bytes):
    with Image.open(BytesIO(image_bytes)) as original:
        image = original.convert("RGBA")

    width, height = image.size

    # Scale watermark to image dimensions
    font_size = max(12, min(30, width // 30, height // 30))

    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            font_size,
        )
    except OSError:
        font = ImageFont.load_default()

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    text = "@bigboori"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    margin = max(10, width // 40)

    x = max(margin, width - text_width - margin)
    y = max(margin, height - text_height - margin)

    # Subtle white watermark at lower-right
    draw.text(
        (x, y),
        text,
        font=font,
        fill=(255, 255, 255, WATERMARK_OPACITY),
        stroke_width=0,
    )

    result = Image.alpha_composite(image, overlay)

    output = BytesIO()
    result.convert("RGB").save(
        output,
        format="JPEG",
        quality=95,
        optimize=True,
    )
    output.seek(0)
    output.name = "bigboori_watermarked.jpg"

    return output


# ============================================================
# COLLECT NEW PHOTOS
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
        f"Total: {len(db['photos'])}"
    )


# ============================================================
# POST ONE WATERMARKED PHOTO
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

    # Start another cycle after all photos are used
    if not available:
        print("All photos posted. Starting a new cycle.")
        posted.clear()
        available = photos

    selected = random.choice(available)

    try:
        # Download original photo from Telegram
        telegram_file = await context.bot.get_file(
            selected["file_id"]
        )

        original_bytes = BytesIO()
        await telegram_file.download_to_memory(
            out=original_bytes
        )

        # Add subtle watermark
        watermarked_photo = add_watermark(
            original_bytes.getvalue()
        )

        # Publish with clickable channel-name caption
        await context.bot.send_photo(
            chat_id=TARGET_CHANNEL,
            photo=watermarked_photo,
            caption=CAPTION,
            parse_mode=ParseMode.HTML,
        )

        posted.add(selected["file_id"])
        db["posted"] = list(posted)
        save_db(db)

        print("Watermarked photo posted successfully.")
        print("Caption: βΟΟTΨҒUL")
        print("Next scheduled post: in 2 hours.")

    except Exception as error:
        print(f"Posting error: {error}")


# ============================================================
# MAIN
# ============================================================

def main():
    print("================================")
    print("BIGBOORI PHOTO BOT")
    print(f"Target: {TARGET_CHANNEL}")
    print("Interval: 2 hours")
    print("Watermark: subtle lower-right")
    print("Caption: clickable βΟΟTΨҒUL")
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

    # No immediate startup post.
    # First scheduled post happens after 2 hours.
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
