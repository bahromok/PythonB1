import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import wikipediaapi
from telegram import ChatMember

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = "7670140223:AAEirSJpYiVEX7hRk8u6mOQ5WXi4yZslBz0"

# Initialize Wikipedia API
wiki_wiki = wikipediaapi.Wikipedia(
    language="uz", user_agent="TelegramWikiBot/1.0 (https://github.com/your_username)"
)

# A dictionary to manage user data for pagination
user_data = {}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start or /wiki command."""
    chat_ids = ["@eternaltrio", "@somethingtest13"]  # Replace with your required channel usernames
    user_id = update.message.from_user.id
    
    # Check which channels the user is subscribed to
    buttons = []
    for chat_id in chat_ids:
        try:
            member = await context.bot.get_chat_member(chat_id, user_id)
            if member.status not in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
                # Add button only if the user is not subscribed
                buttons.append(
                    InlineKeyboardButton(f"Join {chat_id}", url=f"https://t.me/{chat_id[1:]}")
                )
        except Exception as e:
            print(f"Error checking membership in {chat_id}: {e}")
            # Add button for channel even if there's an error (i.e., can't check membership)
            buttons.append(
                InlineKeyboardButton(f"Join {chat_id}", url=f"https://t.me/{chat_id[1:]}")
            )

    # If no buttons to show, user is already subscribed to all
    if buttons:
        reply_markup = InlineKeyboardMarkup([buttons])
        await update.message.reply_text("You are not a member of some channels. Please join them:", reply_markup=reply_markup)
        return

    # If the user is subscribed to all channels, send the main options
    keyboard = [
        [
            InlineKeyboardButton("🔍 Search Wikipedia", callback_data="search"),
            InlineKeyboardButton("ℹ️ About Bot", callback_data="about"),
        ],
        [
            InlineKeyboardButton("❤️ Donate", url="https://donate.wikimedia.org/"),
            InlineKeyboardButton("🌐 Visit Wikipedia", url="https://www.wikipedia.org/"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome to the Wikipedia Bot! Choose an option below:", reply_markup=reply_markup)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles inline button callbacks."""
    query = update.callback_query
    await query.answer()

    if query.data == "search":
        context.user_data["awaiting_search"] = True
        await query.message.reply_text("Please type the term you'd like to search for:")
    elif query.data == "about":
        await query.message.reply_text(
            "I am a Wikipedia Bot! 📝\n"
            "You can search Wikipedia articles and navigate through their content. "
            "Use the search button to get started or type a term directly."
        )


async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles search input from the user."""
    await start_command(update, context)  
    if context.user_data.get("awaiting_search"):
        search_term = update.message.text
        context.user_data["awaiting_search"] = False

        # Fetch page from Wikipedia
        page = wiki_wiki.page(search_term)

        if page.exists():
            # Prepare and store paginated content
            chunks = [page.summary[i : i + 500] for i in range(0, len(page.summary), 500)]
            user_id = update.message.from_user.id
            user_data[user_id] = {"chunks": chunks, "current_page": 0}
            await send_page(update, user_id, initial=True)
        else:
            await update.message.reply_text(f"No results found for '{search_term}'.") 
    else:
        await update.message.reply_text("Use /start to explore bot features.")
      


async def send_page(update: Update, user_id: int, initial=False):
    """Sends paginated content."""
    user_info = user_data.get(user_id)
    if not user_info:
        await update.message.reply_text("No content to display.")
        return

    current_page = user_info["current_page"]
    chunks = user_info["chunks"]

    # Navigation buttons
    keyboard = []
    if current_page > 0:
        keyboard.append(InlineKeyboardButton("⬅️ Previous", callback_data="prev"))
    if current_page < len(chunks) - 1:
        keyboard.append(InlineKeyboardButton("➡️ Next", callback_data="next"))

    # Ensure the keyboard is a list of lists
    if keyboard:
        reply_markup = InlineKeyboardMarkup([keyboard])
    else:
        reply_markup = None

    if initial:
        await update.message.reply_text(chunks[current_page], reply_markup=reply_markup)
    else:
        query = update.callback_query
        await query.edit_message_text(chunks[current_page], reply_markup=reply_markup)


async def paginate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles pagination button clicks."""
    query = update.callback_query
    user_id = query.from_user.id

    if user_id not in user_data:
        await query.answer("No content available for pagination.")
        return

    user_info = user_data[user_id]
    if query.data == "next" and user_info["current_page"] < len(user_info["chunks"]) - 1:
        user_info["current_page"] += 1
    elif query.data == "prev" and user_info["current_page"] > 0:
        user_info["current_page"] -= 1

    await send_page(update, user_id)


def main():
    """Main function to set up the bot."""
    application = Application.builder().token(TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("wiki", start_command))

    # Callback handlers for inline buttons
    application.add_handler(CallbackQueryHandler(handle_callback, pattern="^(search|about)$"))
    application.add_handler(CallbackQueryHandler(paginate, pattern="^(prev|next)$"))

    # Message handler for user input
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search))
    
    # Run the bot
    logger.info("Bot is running...")
    application.run_polling()


if __name__ == "__main__":
    main()