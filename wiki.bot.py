from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

import random

# List of fantasy names and magical quotes
FANTASY_NAMES = ["Elandor", "Thalindra", "Zorath", "Myrla", "Kalzimir"]
MAGICAL_QUOTES = [
    "The stars guide your path.",
    "Magic lies within your soul.",
    "Beware of the shadows; they speak truths.",
    "The winds of fate are ever-changing.",
    "A brave heart is the strongest spell."
]

# Function to start the bot
async def start(update: Update, context):
    user = update.effective_user.first_name
    welcome_message = (
        f"Greetings, {user}! I am FantasyBot, your magical companion. "
        "Ask me for a story, wisdom, or roll the dice to determine your fate!"
    )
    await update.message.reply_text(welcome_message)

# Function to roll a dice
async def roll_dice(update: Update, context):
    result = random.randint(1, 6)
    await update.message.reply_text(f"You rolled a {result}. The winds of destiny have spoken!")

# Function to generate a fantasy story
async def story(update: Update, context):
    name = random.choice(FANTASY_NAMES)
    quest = random.choice(["seeking the lost gem of Valdor", "facing the dragon of the dark peaks", "unraveling the curse of the silent forest"])
    story = (
        f"Once upon a time, a brave adventurer named {name} set forth on a quest, {quest}. "
        "The journey was perilous, but with courage and a spark of magic, they discovered "
        "that destiny always favors the bold."
    )
    await update.message.reply_text(story)

# Function to provide magical wisdom
async def wisdom(update: Update, context):
    quote = random.choice(MAGICAL_QUOTES)
    await update.message.reply_text(quote)

# Function to handle unrecognized commands or messages
async def handle_message(update: Update, context):
    response = "Ah, a curious mind! Use /story, /wisdom, or /roll_dice to explore the realms of magic!"
    await update.message.reply_text(response)

# Main function to set up the bot
def main():
    TOKEN = "7670140223:AAEirSJpYiVEX7hRk8u6mOQ5WXi4yZslBz0"
    application = ApplicationBuilder().token(TOKEN).build()

    # Adding handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("roll_dice", roll_dice))
    application.add_handler(CommandHandler("story", story))
    application.add_handler(CommandHandler("wisdom", wisdom))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    print("FantasyBot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
