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

# Функция создания inline клавиатуры
def create_inline_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # Кнопки как на скрине (в том же порядке)
    btn1 = types.InlineKeyboardButton('💰 Купить звёзды', callback_data='buy_stars')
    btn2 = types.InlineKeyboardButton('💸 Продать звёзды', callback_data='sell_stars')
    btn3 = types.InlineKeyboardButton('🎨 Аренда NFT', callback_data='rent_nft')
    btn4 = types.InlineKeyboardButton('🖼 Купить NFT', callback_data='buy_nft')
    btn5 = types.InlineKeyboardButton('🎁 Купить обычный подарок', callback_data='buy_gift')
    btn6 = types.InlineKeyboardButton('💎 Премиум', callback_data='premium')
    btn7 = types.InlineKeyboardButton('💳 Пополнить баланс', callback_data='balance')
    btn8 = types.InlineKeyboardButton('👤 Профиль', callback_data='profile')
    btn9 = types.InlineKeyboardButton('🆘 Поддержка', callback_data='support')
    btn10 = types.InlineKeyboardButton('🧮 Калькулятор', callback_data='calculator')
    btn11 = types.InlineKeyboardButton('📄 Информация', callback_data='info')
    btn12 = types.InlineKeyboardButton('⭐️ Отзывы', callback_data='reviews')
    btn13 = types.InlineKeyboardButton('👥 Реферальная система', callback_data='referral')
    
    # Ваши дополнительные кнопки
    btn14 = types.InlineKeyboardButton('📱 Покупка физов', callback_data='physical')
    btn15 = types.InlineKeyboardButton('🔐 Купить приват', callback_data='private')
    btn16 = types.InlineKeyboardButton('📢 Проект Деда', callback_data='project')
    
    # Добавляем кнопки в markup (соблюдая порядок с вашими в конце)
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10, btn11, btn12, btn13, btn14, btn15, btn16)
    
    return markup

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
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
        
        # Кнопки со скрина (все в разработке)
        if call.data == 'buy_stars':
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, "🚧 Раздел «Купить звёзды» находится в разработке. Скоро здесь появится информация!")
        
        elif call.data == 'sell_stars':
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, "🚧 Раздел «Продать звёзды» находится в разработке. Скоро здесь появится информация!")
        
        elif call.data == 'rent_nft':
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, "🚧 Раздел «Аренда NFT» находится в разработке. Скоро здесь появится информация!")
        
        elif call.data == 'buy_nft':
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, "🚧 Раздел «Купить NFT» находится в разработке. Скоро здесь появится информация!")
        
        elif call.data == 'buy_gift':
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, "🚧 Раздел «Купить обычный подарок» находится в разработке. Скоро здесь появится информация!")
        
        elif call.data == 'premium':
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, "🚧 Раздел «Премиум» находится в разработке. Скоро здесь появится информация!")
        
        elif call.data == 'balance':
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, "🚧 Раздел «Пополнить баланс» находится в разработке. Скоро здесь появится информация!")
        
        elif call.data == 'profile':
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, "🚧 Раздел «Профиль» находится в разработке. Скоро здесь появится информация!")
        
        elif call.data == 'support':
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, "🚧 Раздел «Поддержка» находится в разработке. Скоро здесь появится информация!")
        
        elif call.data == 'calculator':
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, "🚧 Раздел «Калькулятор» находится в разработке. Скоро здесь появится информация!")
        
        elif call.data == 'info':
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, "🚧 Раздел «Информация» находится в разработке. Скоро здесь появится информация!")
        
        elif call.data == 'referral':
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, "🚧 Раздел «Реферальная система» находится в разработке. Скоро здесь появится информация!")
        
        # Ваши кнопки (рабочие)
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
