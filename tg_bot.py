from pathlib import Path
from dotenv import load_dotenv
import os
from telegram.error import NetworkError, TelegramError
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters



load_dotenv(Path(__file__).parent / '.env', encoding='utf-8-sig')
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PROTECTED_MODE = True
USER_ID = int(os.getenv("USER_IDENT"))


