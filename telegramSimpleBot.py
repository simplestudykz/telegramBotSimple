import os
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from notion_client import Client

# Получаем токен Telegram-бота
TOKEN = os.environ['TELEGRAM_TOKEN']

# Получаем токен API Notion
NOTION_TOKEN = os.environ['NOTION_API_KEY']

# Получаем идентификатор базы данных Notion
DATABASE_ID = os.environ['NOTION_DATABASE_ID']

# Создаем экземпляр бота
bot = telegram.Bot(TOKEN)

# Создаем экземпляр клиента Notion
notion = Client(auth=NOTION_TOKEN)

# Получаем объект базы данных Notion
database = notion.databases.retrieve(database_id=DATABASE_ID)

# Обработчик команды "/start"
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Чтобы получить информацию, выбери команду /auth и введи свой ID ученика.")

# Обработчик команды "/auth"
def auth(update, context):
    context.user_data['id'] = update.message.text
    context.bot.send_message(chat_id=update.effective_chat.id, text="Вы успешно авторизовались. Выберите предмет или день.")

# Обработчик текстовых сообщений
def text(update, context):
    if 'subject' not in context.user_data:
        context.user_data['subject'] = update.message.text
        context.bot.send_message(chat_id=update.effective_chat.id, text="Выберите день.")
    else:
        # Получаем список записей из базы данных Notion
        results = notion.databases.query(
            **{
                "database_id": DATABASE_ID,
                "filter": {
                    "and": [
                        {
                            "property": "ID ученика",
                            "title": {
                                "equals": context.user_data['id']
                            }
                        },
                        {
                            "property": "Предмет",
                            "title": {
                                "equals": context.user_data['subject']
                            }
                        },
                        {
                            "property": "Дата",
                            "date": {
                                "on_or_after": update.message.text,
                                "on_or_before": update.message.text
                            }
                        }
                    ]
                }
            }
                )

    # Обрабатываем результаты запроса и выводим информацию
    if len(results['results']) > 0:
        for page in results['results']:
            message = f"Комментарии: {page['properties']['Комментарии']['rich_text'][0]['plain_text']}\n"
            message += f"Оценка: {page['properties']['Оценка']['number']}\n"
            message += f"Посещаемость: {page['properties']['Посещаемость']['select']['name']}\n"
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Нет записей для выбранного предмета и даты.")

        start_handler = CommandHandler('start', start)
auth_handler = CommandHandler('auth', auth)
text_handler = MessageHandler(Filters.text, text)
updater = Updater(TOKEN, use_context=True)

#Регистрируем обработчики
updater.dispatcher.add_handler(start_handler)
updater.dispatcher.add_handler(auth_handler)
updater.dispatcher.add_handler(text_handler)

updater.start_polling()
updater.idle()


#Этот скрипт предоставляет пользователю команды "/start" и "/auth". Команда "/start" отправляет приветственное сообщение, а команда "/auth" запрашивает у пользователя ID ученика и сохраняет его в контексте пользователя. После этого пользователь может выбрать предмет и день, и бот выведет информацию по столбцам "Комментарии", "Оценка" и "Посещаемость". В коде используются переменные окружения для хранения токенов Telegram-бота и API Notion, а также идентификатора базы данных Notion. Вы можете изменить их значения в зависимости от ваших настроек.


