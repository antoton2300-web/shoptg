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

PHYSICAL_TEXT = """•Физы от Дедушки в наличии:

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

•Физы с отлегой в наличии:

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

# Функция создания inline клавиатуры (кнопки под сообщением)
def create_inline_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # Основные кнопки
    btn1 = types.InlineKeyboardButton('🌟 Купить звёзды', callback_data='buy_stars')
    btn2 = types.InlineKeyboardButton('🎨 Аренда NFT', callback_data='rent_nft')
    btn3 = types.InlineKeyboardButton('💎 Премиум', callback_data='premium')
    btn4 = types.InlineKeyboardButton('🆘 Поддержка', callback_data='support')
    btn5 = types.InlineKeyboardButton('⭐️ Отзывы', callback_data='reviews')
    
    # Дополнительные кнопки
    btn6 = types.InlineKeyboardButton('📱 Покупка физов', callback_data='physical')
    btn7 = types.InlineKeyboardButton('🔐 Купить приват', callback_data='private')
    btn8 = types.InlineKeyboardButton('📢 Проект Деда', callback_data='project')
    
    # Добавляем кнопки в markup
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8)
    
    return markup

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        # Отправляем сообщение с inline кнопками
        bot.send_message(
            message.chat.id, 
            WELCOME_TEXT, 
            reply_markup=create_inline_keyboard(),
            parse_mode='HTML'
        )
        logger.info(f"Пользователь {message.from_user.id} запустил бота")
    except Exception as e:
        logger.error(f"Ошибка в команде /start: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик нажатий на inline кнопки
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        
        if call.data == 'buy_stars':
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, "Выберите количество звёзд:\n\n100⭐ - 100₽\n500⭐ - 450₽\n1000⭐ - 850₽\n\nСвязь: @CBACTOH_DEDA")
        
        elif call.data == 'rent_nft':
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, "Доступные NFT для аренды:\n\n• Username: @name - 500⭐/мес\n• Username: @shop - 1000⭐/мес\n\nПо всем вопросам: @CBACTOH_DEDA")
        
        elif call.data == 'premium':
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, "Telegram Premium:\n\n• 1 месяц - 300⭐\n• 3 месяца - 850⭐\n• 6 месяцев - 1600⭐\n• 1 год - 3000⭐\n\nСвязь: @CBACTOH_DEDA")
        
        elif call.data == 'support':
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, "По всем вопросам обращайтесь: @CBACTOH_DEDA")
        
        elif call.data == 'reviews':
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, REVIEWS_TEXT, parse_mode='Markdown', disable_web_page_preview=True)
            logger.info(f"Пользователь {call.from_user.id} запросил отзывы")
        
        elif call.data == 'physical':
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, PHYSICAL_TEXT)
            logger.info(f"Пользователь {call.from_user.id} запросил список физов")
        
        elif call.data == 'private':
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, PRIVATE_TEXT)
            logger.info(f"Пользователь {call.from_user.id} запросил приват")
        
        elif call.data == 'project':
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, PROJECT_TEXT, parse_mode='Markdown', disable_web_page_preview=True)
            logger.info(f"Пользователь {call.from_user.id} запросил информацию о проекте")
            
    except Exception as e:
        logger.error(f"Ошибка при обработке callback: {e}")
        bot.answer_callback_query(call.id, "Произошла ошибка")

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    try:
        if message.text == '/help':
            help_text = (
                "ℹ️ Доступные команды:\n\n"
                "/start - Запустить бота и показать меню\n"
                "/help - Показать это сообщение"
            )
            bot.send_message(message.chat.id, help_text)
        elif message.text == '/owner' and message.from_user.id == OWNER_ID:
            bot.send_message(message.chat.id, "✅ Бот работает и готов к использованию!")
        else:
            # Если пользователь пишет что-то другое, показываем меню с кнопками
            bot.send_message(
                message.chat.id, 
                "Пожалуйста, воспользуйтесь кнопками ниже:", 
                reply_markup=create_inline_keyboard()
            )
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")

# Запуск бота
if __name__ == '__main__':
    logger.info("Бот запущен и готов к работе!")
    try:
        bot.send_message(OWNER_ID, "🚀 Бот успешно запущен и готов к работе!")
    except Exception as e:
        logger.error(f"Не удалось отправить уведомление владельцу: {e}")
    
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            logger.error(f"Ошибка polling: {e}")
            import time
            time.sleep(3)
