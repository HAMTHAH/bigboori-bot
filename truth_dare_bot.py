import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TRUTHS = [
    "What is your most embarrassing moment?",
    "Who was your first crush?",
    "What is the biggest lie you've ever told?",
    "What's something you've never told your friends?",
    "Who in this group would you trust with your biggest secret?",
    "What is the weirdest thing you do when nobody is watching?",
    "What's your biggest guilty pleasure?",
    "Have you ever had a crush on someone you shouldn't have?",
    "What's the most embarrassing message you've ever sent?",
    "What is one thing you would change about yourself?",
]

DARES = [
    "Send the last selfie in your gallery to the group.",
    "Do your best impression of someone in the group.",
    "Send a voice message saying 'I am the main character.'",
    "Change your Telegram profile picture for 10 minutes.",
    "Type the first thing that comes to your mind.",
    "Send 😂 to the last person you messaged.",
    "Write a completely ridiculous status and keep it for 10 minutes.",
    "Send a voice message singing the first song that comes to mind.",
    "Let the group choose your next Telegram status.",
    "Say something nice about the person above you.",
]


def game_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("😈 TRUTH", callback_data="truth"),
            InlineKeyboardButton("🔥 DARE", callback_data="dare"),
        ],
        [
            InlineKeyboardButton("🎲 RANDOM", callback_data="random"),
        ],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🎭 *TRUTH OR DARE* 🔥\n\n"
        "Welcome to the game!\n\n"
        "Choose your challenge below 👇"
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=game_keyboard(),
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    choice = query.data

    if choice == "truth":
        question = random.choice(TRUTHS)
        title = "😈 TRUTH"

    elif choice == "dare":
        question = random.choice(DARES)
        title = "🔥 DARE"

    else:
        if random.choice([True, False]):
            question = random.choice(TRUTHS)
            title = "😈 TRUTH"
        else:
            question = random.choice(DARES)
            title = "🔥 DARE"

    user = query.from_user.first_name

    text = (
        f"🎯 *{title}*\n\n"
        f"👤 Player: *{user}*\n\n"
        f"👉 {question}"
    )

    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=game_keyboard(),
    )


def main():
    token = "YOUR_BOT_TOKEN"

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    print("Truth or Dare bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
