import os
import logging
from datetime import datetime, timedelta
from database import create_table, get_vacations
import sqlite3
from dotenv import load_dotenv
from telegram import ForceReply, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

load_dotenv()
TOKEN = os.getenv('TOKEN')

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

DB_NAME = 'vacation_planner.db'
TABLE_NAME = 'users'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}! Этот бот создан для планирования отусков. Что хочешь сделать?",
        reply_markup=ForceReply(selective=True),
    )
    keyboard = [
        [
            InlineKeyboardButton("Запланировать отпуск", callback_data="plan_vacation"),
            InlineKeyboardButton("Посмотреть запланированное", callback_data="get_vacations"),
        ],
        # [InlineKeyboardButton("Option 3", callback_data="option_3")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)


async def plan_vacation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    existing_vacations = get_vacations(chat_id)

    if existing_vacations:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("У вас уже есть запланированные отпуска.")
        return
    # Создаем пустую таблицу, если она не существует
    create_table()

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        f"Введите дату начала отпуска (YYYY-MM-DD):",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Закрепить", callback_data=f"confirm_plan_{chat_id}"),
             InlineKeyboardButton("Отмена", callback_data=f"cancel_plan_{chat_id}")]
        ])
    )


async def confirm_plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    query = update.callback_query

    message_text = query.message.text

    # Разделяем текст на строки
    lines = message_text.split('\n')

    # Проверяем, что у нас хотя бы две строки
    if len(lines) < 0:
        await query.answer()
        await query.edit_message_text("Произошла ошибка при получении информации об отпуске.")
        return

    start_date = lines[1].strip()

    end_date = datetime.strptime(start_date, "YYYY-MM-DD") + timedelta(days=14)
    end_date_str = end_date.strftime("YYYY-MM-DD")

    vacation_info = {"start_date": start_date, "end_date": end_date_str}

    # Сохраняем информацию об отпуске в базе данных
    save_vacation(chat_id, vacation_info)

    query.answer()
    query.edit_message_text(f"Отпуск запланирован:\n"
                            f"Начало: {start_date}\n"
                            f"Конец: {end_date_str}")


async def view_planned(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id

    # Получаем информацию о существующих отпусках из базы данных
    existing_vacations = get_vacations(chat_id)

    if existing_vacations:
        vacation_info = eval(existing_vacations)
        vacation_text = "\n".join([f"{v['start_date']} - {v['end_date']}" for v in vacation_info])
        await update.message.reply_text(vacation_text)
    else:
        await update.message.reply_text("У вас нет запланированных отпусков.")
