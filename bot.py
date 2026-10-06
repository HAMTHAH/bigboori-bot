import os
import random
import secrets

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    InlineQueryHandler,
    ContextTypes,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# =========================
# QUESTIONS
# =========================

TRUTHS = [
    "Who was the last person you secretly wanted to message?",
    "What is your biggest red flag?",
    "What is your biggest green flag?",
    "Have you ever had a crush on someone you shouldn't?",
    "What is the most embarrassing thing you've done for a crush?",
    "Have you ever flirted just to get attention?",
    "Who was your first serious crush?",
    "What instantly makes someone attractive to you?",
    "What is your biggest dating turn-off?",
    "Have you ever pretended not to like someone you actually liked?",
    "What's the boldest move you've made on someone?",
    "Have you ever stalked someone's social media after meeting them?",
    "What is your secret guilty pleasure?",
    "Have you ever fallen for a friend?",
    "What is the cutest thing someone has done for you?",
    "What is the worst pickup line you've ever heard?",
    "Have you ever lied about being busy to avoid someone?",
    "What personality trait attracts you the most?",
    "What is something you find irresistible?",
    "Have you ever sent a message and immediately regretted it?",
    "What's your biggest dating insecurity?",
    "Have you ever liked two people at the same time?",
    "What's the most romantic thing you'd actually do?",
    "Have you ever reread an old conversation because you missed someone?",
    "What makes you jealous?",
    "What's your ideal first date?",
    "Have you ever caught feelings unexpectedly?",
    "What is the longest you've had a crush on someone?",
    "Would you date someone completely different from your usual type?",
    "What is one thing you'd never tolerate in a relationship?",
    "Have you ever flirted with someone you just met?",
    "What's your favorite compliment to receive?",
    "Have you ever secretly hoped someone would make the first move?",
    "What is the most attractive thing someone can wear?",
    "Would you rather make the first move or be approached?",
    "Have you ever had a crush on someone unavailable?",
    "What's your weakness when someone is flirting with you?",
    "Have you ever pretended not to see someone's message?",
    "What's your favorite kind of attention?",
    "What would make you instantly lose interest in someone?",
    "Have you ever practiced what to say before talking to a crush?",
    "What's the most daring romantic thing you'd try?",
    "Would you ever date someone you met online?",
    "What is your biggest relationship fear?",
    "What makes you feel special?",
    "Have you ever flirted through texting for hours?",
    "What is your idea of perfect chemistry?",
    "Would you rather have a secret admirer or openly flirt with someone?",
    "What's one question you've always wanted to ask your crush?",
    "If you had to choose someone here for a date, who would it be?",
]

DARES = [
    "Send a 😏 emoji to the person you find most attractive.",
    "Give the other player a cheesy pickup line.",
    "Describe your perfect date in three words.",
    "Send a voice message saying 'You are dangerously attractive.'",
    "Change your profile picture for 5 minutes.",
    "Tell the other player their most attractive quality.",
    "Send three flirty emojis without explaining them.",
    "Write a ridiculously romantic compliment.",
    "Let the other player choose your next emoji.",
    "Send a message starting with 'I probably shouldn't tell you this, but...'",
    "Give the other player a nickname.",
    "Describe your dream kiss using only emojis.",
    "Send a dramatic 'I miss you' message.",
    "Pretend you're asking the other player on a first date.",
    "Send your best pickup line.",
    "Write a two-line romantic poem.",
    "Say something that would make the other player blush.",
    "Send a heart emoji and don't explain it.",
    "Describe what your ideal partner would be like.",
    "Send a voice message saying something sweet.",
    "Tell the other player what you noticed about them first.",
    "Pretend you're proposing and write your proposal.",
    "Send five different heart emojis.",
    "Give the other player a compliment without using the words 'beautiful' or 'handsome'.",
    "Write a flirty text you'd normally be too shy to send.",
    "Pretend you're jealous and explain why.",
    "Send a message containing only emojis that describes your feelings.",
    "Give the other player your best romantic one-liner.",
    "Describe your dream date without saying where it is.",
    "Send a 'goodnight' message as dramatically as possible.",
    "Tell the other player something you find irresistible.",
    "Pretend you are meeting the other player for the first time and flirt with them.",
    "Send a fake love confession.",
    "Write a text that would make someone smile immediately.",
    "Give the other player a cute nickname and use it for the next round.",
    "Send a voice message saying 'I think you're trouble.'",
    "Describe your perfect romantic evening.",
    "Send a mysterious message that makes the other player curious.",
    "Tell the other player what your first impression of them would be.",
    "Write a three-word confession.",
    "Send your most dramatic flirting emoji combination.",
    "Pretend you are trying to impress the other player at a party.",
    "Give the other player a compliment using exactly five words.",
    "Write a text that sounds like the beginning of a romance movie.",
    "Tell the other player one thing you would do on a perfect date.",
    "Send a message beginning with 'Don't get used to this, but...'",
    "Describe the other player as if they were a movie character.",
    "Send a playful challenge back to the other player.",
    "Give the other player your smoothest compliment.",
    "End your message with '...and that's why you're dangerous.'",
]

# =========================
# GAME STORAGE
# =========================

games = {}


def create_game(creator_id=None):
    code = secrets.token_urlsafe(6)
    games[code] = {
        "girl": None,
        "boy": None,
        "turn": None,
        "round": 0,
        "active": False,
        "creator_id": creator_id,
    }
    return code


def get_player(game, role):
    return game.get(role)


def role_keyboard(code):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👩 GIRL", callback_data=f"role:g:{code}"),
            InlineKeyboardButton("👨 BOY", callback_data=f"role:b:{code}"),
        ]
    ])


def game_keyboard(code):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("😈 TRUTH", callback_data=f"truth:{code}"),
            InlineKeyboardButton("🔥 DARE", callback_data=f"dare:{code}"),
        ],
        [
            InlineKeyboardButton("🎲 RANDOM", callback_data=f"random:{code}"),
        ],
        [
            InlineKeyboardButton("🔄 NEXT", callback_data=f"next:{code}"),
            InlineKeyboardButton("✅ DONE", callback_data=f"done:{code}"),
        ],
    ])


async def send_to_players(context, game, text, reply_markup=None):
    for role in ["girl", "boy"]:
        player = game.get(role)

        if player and player.get("chat_id"):
            try:
                await context.bot.send_message(
                    chat_id=player["chat_id"],
                    text=text,
                    reply_markup=reply_markup,
                )
            except Exception:
                pass


async def send_challenge(context, code, challenge_type="random"):
    game = games.get(code)

    if not game:
        return

    if not game["girl"] or not game["boy"]:
        return

    if challenge_type == "truth":
        challenge = random.choice(TRUTHS)
        emoji = "😈 TRUTH"
    elif challenge_type == "dare":
        challenge = random.choice(DARES)
        emoji = "🔥 DARE"
    else:
        if random.choice([True, False]):
            challenge = random.choice(TRUTHS)
            emoji = "😈 TRUTH"
        else:
            challenge = random.choice(DARES)
            emoji = "🔥 DARE"

    game["round"] += 1

    if game["turn"] is None:
        game["turn"] = random.choice(["girl", "boy"])
    else:
        game["turn"] = "boy" if game["turn"] == "girl" else "girl"

    current_player = "👩 GIRL" if game["turn"] == "girl" else "👨 BOY"

    text = (
        f"🔥 ROUND {game['round']}\n\n"
        f"🎯 Turn: {current_player}\n\n"
        f"{emoji}\n\n"
        f"👉 {challenge}\n\n"
        f"Choose your response below:"
    )

    await send_to_players(
        context,
        game,
        text,
        game_keyboard(code),
    )


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    # Deep-link game
    if context.args:
        code = context.args[0]
        game = games.get(code)

        if not game:
            await update.message.reply_text(
                "❌ This game no longer exists.\n\n"
                "Start a new game using @NAUGHTYDARE_bot in any chat."
            )
            return

        await update.message.reply_text(
            "🔥 PRIVATE TRUTH OR DARE\n\n"
            "👩 Girl vs 👨 Boy\n\n"
            "Choose your role:",
            reply_markup=role_keyboard(code),
        )
        return

    # Normal /start
    await update.message.reply_text(
        "🔥 NAUGHTY TRUTH OR DARE 🔥\n\n"
        "👩 Girl vs 👨 Boy\n"
        "😈 Spicy truths\n"
        "🔥 Flirty dares\n"
        "🎲 Random challenges\n\n"
        "To start a private game, type:\n"
        "@NAUGHTYDARE_bot\n\n"
        "Then tap:\n"
        "🎮 START 1-ON-1 GAME"
    )


# =========================
# INLINE MODE
# =========================

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query.strip().lower()

    results = []

    # Empty query = GAME START
    if not query:
        code = create_game(update.inline_query.from_user.id)

        results.append(
            InlineQueryResultArticle(
                id="start_game",
                title="🎮 START 1-ON-1 GAME",
                description="Create a private Girl vs Boy Truth or Dare game",
                input_message_content=InputTextMessageContent(
                    "🔥 NAUGHTY TRUTH OR DARE 🔥\n\n"
                    "A private Girl vs Boy game is ready!\n\n"
                    "Tap the button below to open the game."
                ),
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "🎮 OPEN GAME",
                            url=f"https://t.me/{context.bot.username}?start={code}",
                        )
                    ]
                ]),
            )
        )

        # Also show normal random options
        for i in range(4):
            kind = random.choice(["truth", "dare"])

            if kind == "truth":
                text = random.choice(TRUTHS)
                title = "😈 TRUTH"
            else:
                text = random.choice(DARES)
                title = "🔥 DARE"

            results.append(
                InlineQueryResultArticle(
                    id=f"random_{i}_{secrets.token_hex(4)}",
                    title=title,
                    description=text,
                    input_message_content=InputTextMessageContent(
                        f"{title}\n\n{text}"
                    ),
                    reply_markup=InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton(
                                "🎲 NEW",
                                switch_inline_query_current_chat=""
                            )
                        ]
                    ]),
                )
            )

        await update.inline_query.answer(
            results,
            cache_time=0,
            is_personal=True,
            switch_pm_text="🎮 START 1-ON-1 GAME",
            switch_pm_parameter=code,
        )
        return

    # Truth search
    if "truth" in query:
        for i in range(10):
            text = random.choice(TRUTHS)

            results.append(
                InlineQueryResultArticle(
                    id=f"truth_{i}_{secrets.token_hex(4)}",
                    title="😈 TRUTH",
                    description=text,
                    input_message_content=InputTextMessageContent(
                        f"😈 TRUTH\n\n{text}"
                    ),
                )
            )

    # Dare search
    elif "dare" in query:
        for i in range(10):
            text = random.choice(DARES)

            results.append(
                InlineQueryResultArticle(
                    id=f"dare_{i}_{secrets.token_hex(4)}",
                    title="🔥 DARE",
                    description=text,
                    input_message_content=InputTextMessageContent(
                        f"🔥 DARE\n\n{text}"
                    ),
                )
            )

    # Random search
    else:
        for i in range(10):
            if random.choice([True, False]):
                text = random.choice(TRUTHS)
                title = "😈 TRUTH"
            else:
                text = random.choice(DARES)
                title = "🔥 DARE"

            results.append(
                InlineQueryResultArticle(
                    id=f"random_{i}_{secrets.token_hex(4)}",
                    title=title,
                    description=text,
                    input_message_content=InputTextMessageContent(
                        f"{title}\n\n{text}"
                    ),
                )
            )

    await update.inline_query.answer(
        results,
        cache_time=0,
        is_personal=True,
    )


# =========================
# BUTTONS
# =========================

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user = query.from_user

    parts = data.split(":")
    action = parts[0]

    if len(parts) < 2:
        return

    code = parts[-1]
    game = games.get(code)

    if not game:
        await query.message.reply_text("❌ This game has expired.")
        return

    # =====================
    # ROLE SELECTION
    # =====================

    if action == "role":
        role = parts[1]

        if game["girl"] and game["girl"]["user_id"] == user.id:
            if role == "boy":
                await query.answer(
                    "You already joined as Girl.",
                    show_alert=True
                )
                return

        if game["boy"] and game["boy"]["user_id"] == user.id:
            if role == "girl":
                await query.answer(
                    "You already joined as Boy.",
                    show_alert=True
                )
                return

        if game[role] is not None:
            await query.answer(
                "That role is already taken.",
                show_alert=True
            )
            return

        game[role] = {
            "user_id": user.id,
            "name": user.first_name,
            "chat_id": update.effective_chat.id,
        }

        role_name = "👩 GIRL" if role == "girl" else "👨 BOY"

        await query.message.reply_text(
            f"✅ You joined as {role_name}!"
        )

        # Both players ready
        if game["girl"] and game["boy"]:

            await send_to_players(
                context,
                game,
                "🔥 BOTH PLAYERS ARE READY!\n\n"
                "👩 Girl: "
                + game["girl"]["name"]
                + "\n"
                "👨 Boy: "
                + game["boy"]["name"]
                + "\n\n"
                "Get ready for some spicy Truth or Dare 😈🔥",
                InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "🎮 START GAME",
                            callback_data=f"begin:{code}"
                        )
                    ]
                ]),
            )

        else:
            await query.message.reply_text(
                "⏳ Waiting for the other player...\n\n"
                "Share this game link with them:\n"
                f"https://t.me/{context.bot.username}?start={code}"
            )

        return

    # =====================
    # BEGIN GAME
    # =====================

    if action == "begin":
        if not game["girl"] or not game["boy"]:
            await query.answer(
                "Both players must join first.",
                show_alert=True
            )
            return

        if game["active"]:
            await query.answer("Game already started.")
            return

        game["active"] = True
        game["turn"] = None

        await send_to_players(
            context,
            game,
            "🔥 GAME STARTED 🔥\n\n"
            "👩 Girl vs 👨 Boy\n\n"
            "Let's see who survives 😈",
        )

        await send_challenge(context, code, "random")
        return

    # =====================
    # TRUTH
    # =====================

    if action == "truth":
        if not game["active"]:
            await query.answer(
                "Start the game first.",
                show_alert=True
            )
            return

        await send_challenge(context, code, "truth")
        return

    # =====================
    # DARE
    # =====================

    if action == "dare":
        if not game["active"]:
            await query.answer(
                "Start the game first.",
                show_alert=True
            )
            return

        await send_challenge(context, code, "dare")
        return

    # =====================
    # RANDOM
    # =====================

    if action == "random":
        if not game["active"]:
            await query.answer(
                "Start the game first.",
                show_alert=True
            )
            return

        await send_challenge(context, code, "random")
        return

    # =====================
    # NEXT
    # =====================

    if action == "next":
        if not game["active"]:
            return

        await send_challenge(context, code, "random")
        return

    # =====================
    # DONE
    # =====================

    if action == "done":
        await query.message.reply_text(
            "✅ Challenge completed!\n\n"
            "Ready for the next one? 😈🔥",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🔥 NEXT",
                        callback_data=f"next:{code}"
                    )
                ]
            ])
        )
        return


# =========================
# RUN BOT
# =========================

def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable is missing.")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(InlineQueryHandler(inline_query))

    print("🔥 NAUGHTYDARE BOT IS RUNNING 🔥")

    app.run_polling()


if __name__ == "__main__":
    main()
