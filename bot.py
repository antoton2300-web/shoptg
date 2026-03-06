import telebot
from telebot import types
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Токен бота
TOKEN = '8408406226:AAGEYZV9CB1DQfPQE7w3QsmfNg3xCpck2xs'

# ID владельца
OWNER_ID = 5842443017

# Ссылки
REVIEWS_LINK = "https://t.me/+3tHlMir3nBhhZTAy"
PROJECT_LINK = "https://t.me/+flRsTtJ6W3Y3N2Iy"

# Инициализация бота
bot = telebot.TeleBot(TOKEN)

# Тексты сообщений
WELCOME_TEXT = """Добро пожаловать в магазин Dedyshki!

У нас Вы можете приобрести Telegram Stars,Telegram Premium,арендовать NFT usernames и подарки.Приватный форум Дедушки,а также вы можете купить физические номера для ТГ аккаунтов.

Владелец магазина: @haliza

Выберите услугу которая вас интересует и с вами свяжется наш модератор.Удачи)"""

PHYSICAL_TEXT = """• Физы от Дедушки в наличии:

- США:75зв/0.9тон/1.25$
- ФИЛИППИНЫ:150зв/1.8тон/2.50$
- ЮАР:1300зв/16.3тон/22.60$
- Турция:185зв/2.3тон/3.20$
- Чили:95зв/1.2тон/1.70$
- Мексика:160зв/2.0тон/2.80$
- Египет:90зв/1.1тон/1.60$
- Бангладеш:80зв/1.0тон/1.50$
- Нигерия:80зв/1.0тон/1.50$
- Колумбия:80зв/1.0тон/1.50$

• Физы с отлегой в наличии:

-США 6 лет:500зв/6.3тон/8.80$"""

PRIVATE_TEXT = """Приват от Дедушки

Цена:4$/200⭐

•Регулярно обновляется
•Скрины содержания тем отправлю в ЛС

|Связь - @CBACTOH_DEDA"""

REVIEWS_TEXT = f"""📊 Отзывы о нашей работе

Здесь вы можете ознакомиться с реальными отзывами наших клиентов:

👉 [Перейти к отзывам]({REVIEWS_LINK})

Присоединяйтесь к нашему каналу с отзывами и будьте в курсе мнений других покупателей!"""

PROJECT_TEXT = f"""🔷 Проект Деда

Официальный канал проекта:

👉 [Перейти на канал]({PROJECT_LINK})

Подписывайтесь, чтобы быть в курсе всех новостей, обновлений и специальных предложений!"""

# Функция создания главного меню (кнопки под сообщением)
def create_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    # Основные кнопки из интерфейса (как на скрине)
    btn1 = types.KeyboardButton('Купить звёзды')
    btn2 = types.KeyboardButton('Аренда NFT')
    btn3 = types.KeyboardButton('Премиум')
    btn4 = types.KeyboardButton('Поддержка')
    btn5 = types.KeyboardButton('Отзывы')
    
    # Дополнительные кнопки по вашему запросу
    btn6 = types.KeyboardButton('Покупка физов')
    btn7 = types.KeyboardButton('Купить приват')
    btn8 = types.KeyboardButton('Проект Деда')
    
    # Добавляем кнопки в нужном порядке (сначала основные, потом дополнительные)
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8)
    
    return markup

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        markup = create_main_keyboard()
        # Отправляем одно сообщение с текстом и кнопками вместе
        bot.send_message(message.chat.id, WELCOME_TEXT, reply_markup=markup)
        logger.info(f"Пользователь {message.from_user.id} запустил бота")
    except Exception as e:
        logger.error(f"Ошибка в команде /start: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик всех текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    try:
        text = message.text
        chat_id = message.chat.id
        
        # Основные кнопки
        if text == 'Купить звёзды':
            bot.send_message(chat_id, "Выберите количество звёзд:\n\n100⭐ - 100₽\n500⭐ - 450₽\n1000⭐ - 850₽\n\nСвязь: @CBACTOH_DEDA")
        
        elif text == 'Аренда NFT':
            bot.send_message(chat_id, "Доступные NFT для аренды:\n\n• Username: @name - 500⭐/мес\n• Username: @shop - 1000⭐/мес\n\nПо всем вопросам: @CBACTOH_DEDA")
        
        elif text == 'Премиум':
            bot.send_message(chat_id, "Telegram Premium:\n\n• 1 месяц - 300⭐\n• 3 месяца - 850⭐\n• 6 месяцев - 1600⭐\n• 1 год - 3000⭐\n\nСвязь: @CBACTOH_DEDA")
        
        elif text == 'Поддержка':
            bot.send_message(chat_id, "По всем вопросам обращайтесь: @CBACTOH_DEDA")
        
        elif text == 'Отзывы':
            bot.send_message(chat_id, REVIEWS_TEXT, parse_mode='Markdown', disable_web_page_preview=True)
            logger.info(f"Пользователь {message.from_user.id} запросил отзывы")
        
        # Дополнительные кнопки
        elif text == 'Покупка физов':
            bot.send_message(chat_id, PHYSICAL_TEXT)
            logger.info(f"Пользователь {message.from_user.id} запросил список физов")
        
        elif text == 'Купить приват':
            bot.send_message(chat_id, PRIVATE_TEXT)
            logger.info(f"Пользователь {message.from_user.id} запросил приват")
        
        elif text == 'Проект Деда':
            bot.send_message(chat_id, PROJECT_TEXT, parse_mode='Markdown', disable_web_page_preview=True)
            logger.info(f"Пользователь {message.from_user.id} запросил информацию о проекте")
        
        # Скрытая команда для владельца
        elif text == '/owner' and message.from_user.id == OWNER_ID:
            bot.send_message(chat_id, "✅ Бот работает и готов к использованию!")
        
        # Если пользователь отправил что-то другое
        else:
            bot.send_message(
                chat_id, 
                "Пожалуйста, воспользуйтесь кнопками меню для навигации.\n"
                "Если кнопки не отображаются, нажмите /start"
            )
            
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения от {message.from_user.id}: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик команды /help
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "ℹ️ Доступные команды:\n\n"
        "/start - Запустить бота и показать меню\n"
        "/help - Показать это сообщение\n\n"
        "Используйте кнопки меню для навигации:"
    )
    bot.send_message(message.chat.id, help_text)

# Запуск бота
if __name__ == '__main__':
    logger.info("Бот запущен и готов к работе!")
    try:
        # Уведомление владельцу о запуске бота
        bot.send_message(OWNER_ID, "🚀 Бот успешно запущен и готов к работе!")
    except Exception as e:
        logger.error(f"Не удалось отправить уведомление владельцу: {e}")
    
    # Бесконечный polling с обработкой ошибок
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            logger.error(f"Ошибка polling: {e}")
            import time
            time.sleep(3)
