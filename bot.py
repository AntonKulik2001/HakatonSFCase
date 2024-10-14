import os
import logging
from datetime import datetime, timedelta

from dotenv import load_dotenv
from telegram import ForceReply, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

import vacation_planner

load_dotenv()
TOKEN = os.getenv('TOKEN')

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", vacation_planner.start))
    application.add_handler(CallbackQueryHandler(vacation_planner.plan_vacation, pattern=r"^plan_vacation$"))
    application.add_handler(CallbackQueryHandler(vacation_planner.confirm_plan, pattern=r"^confirm_plan_(.+)$"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, vacation_planner.view_planned))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
