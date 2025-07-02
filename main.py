import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes,
    CommandHandler,
)
import logging

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Bot Settings
BOT_TOKEN = "7771617416:AAHO5HDPONMfmUQkfzU6dcQmdeEGk8tU7uE"
OWNER_ID = 7886646898  # Karin sama's Telegram ID
default_delete_time = 600  # 10 minutes
group_delete_times = {}  # Stores per-group delete delay

# Delete message after delay
async def delete_later(context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.delete_message(
            chat_id=context.job.chat_id,
            message_id=context.job.data
        )
    except Exception as e:
        print(f"Failed to delete message: {e}")

# Handle all group messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        chat_id = update.effective_chat.id
        msg_id = update.message.message_id
        delay = group_delete_times.get(chat_id, default_delete_time)

        context.job_queue.run_once(
            delete_later,
            delay,
            chat_id=chat_id,
            data=msg_id
        )

# /settime command — only Karin sama
async def settime_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    if user.id != OWNER_ID:
        await update.message.reply_text("❌ You're not allowed to use this command.")
        return

    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("⚠️ Usage: /settime <seconds> (e.g., /settime 300)")
        return

    seconds = int(context.args[0])
    if seconds < 10 or seconds > 86400:
        await update.message.reply_text("⏱️ Choose a time between 10 and 86400 seconds.")
        return

    group_delete_times[chat.id] = seconds
    await update.message.reply_text(f"✅ Auto-delete time set to {seconds} seconds.")

# /start command — responds to everyone
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This bot only works for Karin sama, Sayonara Baka.")

# /help command — responds to everyone
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This bot only works for Karin sama, Sayonara Baka.")

# Main
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command Handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("settime", settime_command))

    # Message Handler
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()
      
