import os
import logging
from datetime import datetime, timedelta

import sqlite3
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Константы для базы данных
DB_NAME = 'vacation_planner.db'
TABLE_NAME = 'users'


def create_table():
    """Создает таблицу в базе данных для хранения информации о пользователях."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER UNIQUE,
            start_date DATE,
            end_date DATE,
            is_approved BOOLEAN DEFAULT FALSE,
            places_to_visit TEXT,
            tasks TEXT,
            tickets_booked BOOLEAN DEFAULT FALSE
   
        )
    """)
    conn.commit()
    conn.close()


def save_vacation(chat_id, vacation):
    """Сохраняет информацию об отпуске в базу данных."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"""
        INSERT OR REPLACE INTO {TABLE_NAME} 
        (chat_id, start_date, end_date, is_approved, places_to_visit, tasks, tickets_booked)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (chat_id, vacation['start_date'], vacation['end_date'], vacation['is_approved'],
          vacation.get('places_to_visit', ''), vacation.get('tasks', ''), vacation['tickets_booked']))
    conn.commit()
    conn.close()


def get_vacations(chat_id):
    """Получает информацию об отпусках пользователя из базы данных."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE chat_id = ?", (chat_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None