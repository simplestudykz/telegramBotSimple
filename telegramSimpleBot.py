import os
from datetime import datetime, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
NOTION_API_KEY = os.getenv('NOTION_API_KEY')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

notion = Client(auth=NOTION_API_KEY)
database = notion.databases.retrieve(database_id=NOTION_DATABASE_ID)

# Определяем словарь, где ключ - это имя ученика, а значение - это список всех доступных ему предметов
students_subjects = {}

# Проходимся по каждой записи в базе данных и формируем словарь
for page in database.query():
    student_name = page.properties['Ученик'].title[0].text.content
    subject_name = page.properties['Предмет'].multi_select[0].name
    if student_name not in students_subjects:
        students_subjects[student_name] = []
    if subject_name not in students_subjects[student_name]:
        students_subjects[student_name].append(subject_name)


def start(update, context):
    message = "Добро пожаловать в наш образовательный центр! Чем мы можем вам помочь?"
    keyboard = [
        [
            InlineKeyboardButton("Авторизация", callback_data='authorization'),
            InlineKeyboardButton("Запись на диагностику знаний", callback_data='registration')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(message, reply_markup=reply_markup)


def authorization(update, context):
    update.callback_query.answer()
    update.callback_query.message.delete()
    message = "Введите свое имя"
    context.chat_data['last_action'] = 'authorization'
    update.callback_query.message.reply_text(message)


def check_authorization(update, context):
    student_name = update.message.text
    if student_name in students_subjects:
        message = f"Добро пожаловать, {student_name}! Вы успешно авторизовались."
        context.chat_data['student_name'] = student_name
        keyboard = [
            [
                InlineKeyboardButton("Предметы", callback_data='subjects'),
                InlineKeyboardButton("Дата", callback_data='dates')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(message, reply_markup=reply_markup)
    else:
        message = f"Извините, {student_name}, мы не нашли вас в нашей базе данных. Попробуйте еще раз."
        update.message.reply_text(message)


def registration(update, context):
    update.callback_query.answer()
    update.callback_query.message.delete()
    message = "Введите номер телефона в формате 79991234567"
    context.chat_data['last_action'] = 'registration'
    update.callback_query.message.reply_text(message)


def check_registration(update, context):
    phone_number = update.message.text
    message = f"Введите ваше имя"
    context.chat_data['phone_number'] = phone_number
    context.chat_data['last_action'] = 'check_registration'
    update.message.reply

from telegram.ext import MessageHandler, Filters

def handle_message(update, context):
    message_text = update.message.text
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # Здесь будет обработка пользовательского ввода

dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))


from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ConversationHandler

# Определение констант для ConversationHandler
NAME, PHONE, DATE, SUBJECT = range(4)

# Функции для отображения форм и кнопок
def start(update, context):
    reply_keyboard = [['Авторизация', 'Запись на диагностику знаний']]
    update.message.reply_text(
        'Здравствуйте! Чем я могу вам помочь?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return ConversationHandler.END

def ask_name(update, context):
    update.message.reply_text('Введите ваше имя:')
    return NAME

def ask_phone(update, context):
    user_name = update.message.text.strip()
    context.user_data['name'] = user_name
    update.message.reply_text('Введите ваш номер телефона в формате +7XXXXXXXXXX:')
    return PHONE

def ask_date(update, context):
    user_phone = update.message.text.strip()
    context.user_data['phone'] = user_phone
    update.message.reply_text('Введите дату, на которую вы хотите записаться, в формате ДД.ММ.ГГГГ:')
    return DATE

def show_subjects(update, context):
    user_date = update.message.text.strip()
    context.user_data['date'] = user_date
    user_id = update.effective_user.id

    # Здесь будет обработка выбора предмета и отображение кнопок
    subject_buttons = []

    # Получаем список предметов, доступных пользователю
    # ...

    reply_keyboard = build_menu(subject_buttons, 2)
    update.message.reply_text('Выберите предмет:', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return SUBJECT

def show_dates(update, context):
    user_subject = update.message.text.strip()
    context.user_data['subject'] = user_subject
    user_id = update.effective_user.id

    # Здесь будет обработка выбора даты и отображение кнопок
    date_buttons = []

    # Получаем список дат, доступных пользователю
    # ...

    reply_keyboard = build_menu(date_buttons, 2)
    update.message.reply_text('Выберите дату:', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
def handle_date_callback(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    user_name = query.from_user.full_name
    user_data = get_user_data(user_id)

    if user_data is None:
        query.answer()
        query.edit_message_text(f"Произошла ошибка! Вы не авторизованы. "
                                f"Для авторизации введите /auth")
        return

    date = query.data
    feedback_entries = get_feedback_entries(user_data['Ученик'], date)

    if not feedback_entries:
        query.answer()
        query.edit_message_text(f"Записей на {date} не найдено.")
        return

    message_text = f"Записи на {date}:\n"
    for entry in feedback_entries:
        message_text += f"\nДата: {entry['Дата']}\n" \
                        f"Предмет: {entry['Предмет']} ({entry['Преподаватель']})\n" \
                        f"Simple: {entry['Simple']}\n" \
                        f"Комментарий: {entry['Комментарий']}\n"

    query.answer()
    query.edit_message_text(message_text)


def handle_dates_callback(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    user_name = query.from_user.full_name
    user_data = get_user_data(user_id)

    if user_data is None:
        query.answer()
        query.edit_message_text(f"Произошла ошибка! Вы не авторизованы. "
                                f"Для авторизации введите /auth")
        return

    dates = get_feedback_dates(user_data['Ученик'])
    if not dates:
        query.answer()
        query.edit_message_text(f"Записей не найдено.")
        return

    buttons = [[InlineKeyboardButton(date, callback_data=date)] for date in dates]
    reply_markup = InlineKeyboardMarkup(buttons)

    query.answer()
    query.edit_message_text("Выберите дату:", reply_markup=reply_markup)

    def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start_command))
    dp.add_handler(CommandHandler('auth', auth_command))
    dp.add_handler(CommandHandler('subjects', subjects_command))
    dp.add_handler(CommandHandler('dates', dates_command))
    dp.add_handler(CallbackQueryHandler(handle_subjects_callback))
    dp.add_handler(CallbackQueryHandler(handle_date_callback))
    dp.add_handler(CallbackQueryHandler(handle_dates_callback))

    updater.start_polling()
    updater.idle()

