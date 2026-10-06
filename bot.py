import os
import random
import secrets

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Update,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    InlineQueryHandler,
    ContextTypes,
)

# ============================================================
# 50 TRUTHS
# ============================================================

TRUTHS = [
    "Who is the most attractive person you've ever had a crush on?",
    "Have you ever secretly liked a friend?",
    "Who was your last crush?",
    "What's the first thing you notice about someone you're attracted to?",
    "Have you ever flirted with someone to make someone else jealous?",
    "What's your biggest weakness when you like someone?",
    "Have you ever liked someone who didn't know?",
    "Would you date someone your best friend used to like?",
    "What's the boldest move you've ever made on a crush?",
    "Have you ever pretended not to like someone when you actually did?",
    "Who was the last person who made your heart beat faster?",
    "What's your biggest dating red flag?",
    "What's your biggest green flag?",
    "Have you ever fallen for someone unexpectedly?",
    "Would you choose looks or personality?",
    "What's your ideal first date?",
    "Have you ever repeatedly checked the profile of someone you liked?",
    "What's the most attractive personality trait?",
    "Have you ever sent a message and immediately regretted it?",
    "Who was the last person you wanted to impress?",
    "Would you date someone outside your usual type?",
    "What's the most romantic thing someone could do for you?",
    "Have you ever had a crush on someone unavailable?",
    "What's the longest you've secretly liked someone?",
    "Have you ever flirted through texting but acted shy in person?",
    "What's the most attractive thing someone can wear?",
    "Have you ever caught feelings after saying you wouldn't?",
    "Would you make the first move or wait?",
    "What's your favorite kind of compliment?",
    "Have you ever reread an old conversation with someone you liked?",
    "Who would you want to receive a surprise date invitation from?",
    "What instantly makes someone more attractive?",
    "Have you ever dressed extra well because your crush was there?",
    "Would you date your exact opposite?",
    "What's the most embarrassing thing you've done because you liked someone?",
    "Have you ever gotten jealous even though you weren't dating?",
    "What's your favorite flirting style?",
    "Have you ever practiced what to say before talking to your crush?",
    "What makes you lose interest in someone immediately?",
    "Would you rather receive flowers or a surprise date?",
    "Have you ever intentionally waited before replying to someone you liked?",
    "What's your dream date location?",
    "Have you ever liked someone your friends warned you about?",
    "What's more attractive: confidence or shyness?",
    "Have you ever had chemistry with someone you barely knew?",
    "What's one thing you'd want your future partner to understand?",
    "Would you rather make the first move or be surprised?",
    "What's the sweetest thing someone has ever said to you?",
    "If you could go on a date with anyone you know, who would you choose?",
]

# ============================================================
# 50 DARES
# ============================================================

DARES = [
    "Give someone your best pickup line.",
    "Send a cute selfie to someone you trust.",
    "Give another player a genuine compliment.",
    "Tell someone: 'Be honest... would you date me? 👀'",
    "Describe your ideal partner without saying their name.",
    "Send someone your favorite flirty emoji combination.",
    "Rate someone's flirting skills out of 10.",
    "Send a voice message saying your best pickup line.",
    "Tell the group your first impression of your crush.",
    "Change your profile picture to your best dressed-up photo for 10 minutes.",
    "Write a cheesy romantic message for someone.",
    "Tell someone what you find most attractive about their personality.",
    "Send someone: 'I have a question for you 👀'",
    "Give someone a ridiculous romantic nickname.",
    "Describe your perfect date in three sentences.",
    "Send your best non-explicit selfie to someone.",
    "Give someone your best celebrity-style introduction.",
    "Tell the group what your dream partner looks like.",
    "Write a pickup line using someone's name.",
    "Send someone three heart emojis.",
    "Tell someone one thing that makes them attractive.",
    "Record a 5-second voice message saying 'I think you're cute.'",
    "Let someone choose your status for 10 minutes.",
    "Give someone a dramatic romance-movie compliment.",
    "Tell the group your most embarrassing crush story.",
    "Send a selfie making your best confident expression.",
    "Give someone your best first-date invitation.",
    "Describe your ideal first date with someone in the chat.",
    "Send someone 'We need to talk 👀' and then reveal it's a dare.",
    "Rate someone's sense of humor out of 10.",
    "Tell the group three things you find attractive.",
    "Send your favorite romantic emoji combination.",
    "Give someone a compliment without mentioning appearance.",
    "Pretend to propose to someone for 10 seconds.",
    "Create a fake dating-app bio for yourself.",
    "Send a voice message introducing yourself as someone's future date.",
    "Tell the group your most attractive quality.",
    "Give someone a cheesy movie-style compliment.",
    "Send someone: 'Quick question... what's your type? 👀'",
    "Let someone choose one harmless emoji for your next five messages.",
    "Describe your perfect partner using five words.",
    "Give someone a playful compliment.",
    "Tell the group what would instantly make you interested in someone.",
    "Send a selfie with your best smile.",
    "Give someone a fake award for having the best personality.",
    "Tell someone their best quality.",
    "Make up a romantic movie title about you and your crush.",
    "Send a voice message saying your most dramatic love confession.",
    "Tell the group your dream date activity.",
    "Give someone your best harmless flirting attempt.",
]

# ============================================================
# PRIVATE GAME STORAGE
# ============================================================

games = {}


def create_game():
    code = secrets.token_urlsafe(6)

    games[code] = {
        "girl": None,
        "boy": None,
        "turn": None,
        "round": 0,
        "active": False,
    }

    return code


# ============================================================
# PRIVATE GAME
# ============================================================

def main_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🎮 CREATE 1-ON-1 GAME",
                callback_data="create"
            )
        ]
    ])


def role_keyboard(code):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "👩 GIRL",
                callback_data=f"role:g:{code}"
            ),
            InlineKeyboardButton(
                "👨 BOY",
                callback_data=f"role:b:{code}"
            ),
        ]
    ])


def challenge_keyboard(code):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "😈 TRUTH",
                callback_data=f"truth:{code}"
            ),
            InlineKeyboardButton(
                "🔥 DARE",
                callback_data=f"dare:{code}"
            ),
        ],
        [
            InlineKeyboardButton(
                "🎲 RANDOM",
                callback_data=f"random:{code}"
            ),
            InlineKeyboardButton(
                "🔄 NEXT",
                callback_data=f"next:{code}"
            ),
        ],
        [
            InlineKeyboardButton(
                "✅ DONE",
                callback_data=f"done:{code}"
            )
        ],
    ])


# ============================================================
# /START
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Handle deep-link:
    # /start GAMECODE

    if context.args:

        code = context.args[0]

        if code in games:

            game = games[code]

            await update.message.reply_text(
                "🔥 *YOU'VE BEEN INVITED!*\n\n"
                "Choose your role:",
                parse_mode="Markdown",
                reply_markup=role_keyboard(code),
            )

            return

    await update.message.reply_text(
        "🔥 *NAUGHTY TRUTH OR DARE* 🔥\n\n"
        "👩 Girl vs 👨 Boy\n"
        "😈 Truth\n"
        "🔥 Dare\n"
        "🎲 Random\n\n"
        "Create a private 1-on-1 game.",
        parse_mode="Markdown",
        reply_markup=main_menu(),
    )


# ============================================================
# INLINE MODE
# ============================================================

async def inline_query(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.inline_query.query.strip().lower()

    results = []

    if query in ["", "random", "r"]:

        # Random results
        for i in range(5):

            if random.choice([True, False]):

                text = (
                    "😈 TRUTH\n\n"
                    + random.choice(TRUTHS)
                )

else:
