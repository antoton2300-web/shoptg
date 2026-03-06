import telebot
from telebot import types
import logging
import sqlite3
from datetime import datetime
import random
import string

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Токен бота
TOKEN = '8408406226:AAGEYZV9CB1DQfPQE7w3QsmfNg3xCpck2xs'

# ID владельца
OWNER_ID = 5842443017

# Инициализация бота
bot = telebot.TeleBot(TOKEN)

# База данных
def init_db():
    conn = sqlite3.connect('shop_bot.db')
    c = conn.cursor()
    
    # Таблица пользователей
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY,
                  username TEXT,
                  first_name TEXT,
                  balance REAL DEFAULT 0,
                  total_deposit REAL DEFAULT 0,
                  register_date TEXT,
                  referral_link TEXT,
                  referrer_id INTEGER)''')
    
    # Таблица заказов
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  order_type TEXT,
                  amount REAL,
                  price REAL,
                  status TEXT,
                  details TEXT,
                  created_at TEXT)''')
    
    # Таблица транзакций
    c.execute('''CREATE TABLE IF NOT EXISTS transactions
                 (tx_id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  tx_type TEXT,
                  amount REAL,
                  status TEXT,
                  created_at TEXT)''')
    
    # Таблица чеков
    c.execute('''CREATE TABLE IF NOT EXISTS checks
                 (check_id TEXT PRIMARY KEY,
                  user_id INTEGER,
                  amount REAL,
                  check_type TEXT,
                  uses_left INTEGER,
                  total_uses INTEGER,
                  status TEXT,
                  created_at TEXT)''')
    
    conn.commit()
    conn.close()

init_db()

# Тексты сообщений
WELCOME_TEXT = """Добро пожаловать! У нас Вы можете приобрести Telegram Stars, Telegram Premium и арендовать NFT.

🔒 Текущий баланс: 0₽.

Выберите действие"""

# Функция создания главного меню
def create_main_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    btn1 = types.InlineKeyboardButton('Купить звёзды', callback_data='buy_stars_menu')
    btn2 = types.InlineKeyboardButton('Продать звёзды', callback_data='sell_stars_menu')
    btn3 = types.InlineKeyboardButton('Аренда NFT', callback_data='rent_nft')
    btn4 = types.InlineKeyboardButton('Купить NFT', callback_data='buy_nft')
    btn5 = types.InlineKeyboardButton('Купить обычный подарок', callback_data='buy_gift')
    btn6 = types.InlineKeyboardButton('Премиум', callback_data='premium')
    btn7 = types.InlineKeyboardButton('Пополнить баланс', callback_data='deposit')
    btn8 = types.InlineKeyboardButton('Профиль', callback_data='profile')
    btn9 = types.InlineKeyboardButton('Поддержка', callback_data='support')
    btn10 = types.InlineKeyboardButton('Калькулятор', callback_data='calculator')
    btn11 = types.InlineKeyboardButton('Информация', callback_data='info')
    btn12 = types.InlineKeyboardButton('Отзывы', callback_data='reviews')
    btn13 = types.InlineKeyboardButton('Реферальная система', callback_data='referral')
    
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10, btn11, btn12, btn13)
    
    return markup

# Функция создания клавиатуры для покупки звезд
def buy_stars_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton('🛒 Купить Telegram Stars', callback_data='buy_stars_input')
    btn2 = types.InlineKeyboardButton('Чеки', callback_data='checks_menu')
    btn3 = types.InlineKeyboardButton('◀️ Назад', callback_data='back_to_main')
    markup.add(btn1, btn2, btn3)
    return markup

# Функция для меню чеков
def checks_menu_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton('➕ Создать чек', callback_data='create_check')
    btn2 = types.InlineKeyboardButton('◀️ Назад', callback_data='buy_stars_menu')
    markup.add(btn1, btn2)
    return markup

# Функция для выбора типа чека
def check_type_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton('Одиночный чек', callback_data='create_single_check')
    btn2 = types.InlineKeyboardButton('Мульти-чек', callback_data='create_multi_check')
    btn3 = types.InlineKeyboardButton('◀️ Назад', callback_data='checks_menu')
    markup.add(btn1, btn2, btn3)
    return markup

# Функция для продажи звезд
def sell_stars_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton('📜 История', callback_data='sell_history')
    btn2 = types.InlineKeyboardButton('◀️ Назад', callback_data='back_to_main')
    markup.add(btn1, btn2)
    return markup

# Функция для NFT меню
def nft_menu_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # Коллекции NFT
    collections = [
        ('Plush Pepes', 'nft_plush_pepes'),
        ('Heart Lockets', 'nft_heart_lockets'),
        ('Durov\'s Caps', 'nft_durov_caps'),
        ('Precious Peaches', 'nft_precious_peaches'),
        ('Heroic Helmets', 'nft_heroic_helmets'),
        ('Mighty Arms', 'nft_mighty_arms'),
        ('Nail Bracelets', 'nft_nail_bracelets'),
        ('Artisan Bricks', 'nft_artisan_bricks'),
        ('Astral Shards', 'nft_astral_shards'),
        ('Mini Oscars', 'nft_mini_oscars')
    ]
    
    for name, callback in collections:
        btn = types.InlineKeyboardButton(name, callback_data=callback)
        markup.add(btn)
    
    # Навигация
    nav_row = [
        types.InlineKeyboardButton('« 1/11 »', callback_data='nft_pagination'),
        types.InlineKeyboardButton('🔍 Поиск', callback_data='nft_search'),
        types.InlineKeyboardButton('🌐 Веб-каталог', callback_data='nft_web_catalog'),
        types.InlineKeyboardButton('◀️ Назад в меню', callback_data='back_to_main')
    ]
    markup.add(*nav_row)
    
    return markup

# Функция для покупки подарка (выбор получателя)
def gift_recipient_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton('Купить для себя', callback_data='gift_for_self')
    btn2 = types.InlineKeyboardButton('❌ Отмена', callback_data='back_to_main')
    markup.add(btn1, btn2)
    return markup

# Функция для выбора подарка
def gift_selection_keyboard(recipient):
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    gifts = [
        ('❤️ 14 февраля - 74.73₽', 'gift_valentine_1'),
        ('💝 14 февраля - 74.73₽', 'gift_valentine_2'),
        ('🧸 Мишка - 74.73₽', 'gift_bear'),
        ('🎁 -74.73₽', 'gift_1'),
        ('🎁 -74.73₽', 'gift_2'),
        ('🎁 -149.46₽', 'gift_3'),
        ('🎁 -149.46₽', 'gift_4'),
        ('🎁 -37.36₽', 'gift_5'),
        ('🎁 -37.36₽', 'gift_6')
    ]
    
    for name, callback in gifts:
        btn = types.InlineKeyboardButton(name, callback_data=callback)
        markup.add(btn)
    
    btn_cancel = types.InlineKeyboardButton('❌ Отмена', callback_data='back_to_main')
    markup.add(btn_cancel)
    
    return markup

# Функция для премиум меню
def premium_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton('3 месяца — 1004.21₽', callback_data='premium_3months')
    btn2 = types.InlineKeyboardButton('6 месяцев — 1339.22₽', callback_data='premium_6months')
    btn3 = types.InlineKeyboardButton('12 месяцев — 2428.02₽', callback_data='premium_12months')
    btn4 = types.InlineKeyboardButton('◀️ Назад', callback_data='back_to_main')
    markup.add(btn1, btn2, btn3, btn4)
    return markup

# Функция для способов пополнения
def deposit_methods_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    methods = [
        ('💳 СБП #1', 'deposit_sbp'),
        ('💳 Карты РФ', 'deposit_cards'),
        ('🏦 СберПей', 'deposit_sberpay'),
        ('🤖 CryptoBot', 'deposit_cryptobot'),
        ('💰 Криптовалюта', 'deposit_crypto'),
        ('💱 Прямой перевод (USDT | TON)', 'deposit_direct'),
        ('◀️ Назад', 'back_to_main')
    ]
    
    for name, callback in methods:
        btn = types.InlineKeyboardButton(name, callback_data=callback)
        markup.add(btn)
    
    return markup

# Функция для профиля
def profile_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton('📜 История покупок', callback_data='purchase_history')
    btn2 = types.InlineKeyboardButton('🎫 Активировать промокод', callback_data='activate_promo')
    btn3 = types.InlineKeyboardButton('🏠 В меню', callback_data='back_to_main')
    markup.add(btn1, btn2, btn3)
    return markup

# Функция для поддержки
def support_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton('📨 Создать тикет', callback_data='create_ticket')
    btn2 = types.InlineKeyboardButton('◀️ Назад', callback_data='back_to_main')
    markup.add(btn1, btn2)
    return markup

# Функция для калькулятора
def calculator_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton('⭐️ Звёзды —> Рубли', callback_data='calc_stars_to_rub')
    btn2 = types.InlineKeyboardButton('💰 Рубли —> Звёзды', callback_data='calc_rub_to_stars')
    btn3 = types.InlineKeyboardButton('🏠 В меню', callback_data='back_to_main')
    markup.add(btn1, btn2, btn3)
    return markup

# Функция для информации
INFO_TEXT = """Часто задаваемые вопросы:

— Как происходит выдача товара?
Звёзды вы получаете прямо на указанный при оформлении заказа аккаунт, и сразу же можете использовать их так, как пожелаете.

— Как вы даётся премиум?
Премиум выдаётся прямо на аккаунт, указанный при оформлении заказа (подарком), и вы сразу же получаете доступ ко всем премиум-функциям.

— Как быстро приходят звезды?
Заказы отправляются автоматически и, как правило, приходят в течение 15 секунд.

— Могу ли я покупать звезды только для себя?
Нет, вы можете отправлять подарки любым пользователям, у которых есть @username.

— Есть ли риск блокировки моего аккаунта или рефаунда звезд?
Нет, риск отсутствует, так как мы используем официальную платформу Telegram для покупки звёзд. Блокировка или потеря звёзд невозможна."""

# Функция для реферальной системы
def referral_keyboard(user_id):
    referral_link = f"https://t.me/nasvoystarss_bot?start=ref_{user_id}"
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton('🔗 Скопировать ссылку', callback_data='copy_referral_link')
    btn2 = types.InlineKeyboardButton('◀️ Назад', callback_data='back_to_main')
    markup.add(btn1, btn2)
    return referral_link, markup

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "NoUsername"
        first_name = message.from_user.first_name
        
        # Проверяем реферальный код
        args = message.text.split()
        referrer_id = None
        if len(args) > 1 and args[1].startswith('ref_'):
            try:
                referrer_id = int(args[1].replace('ref_', ''))
            except:
                pass
        
        # Сохраняем пользователя в БД
        conn = sqlite3.connect('shop_bot.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        if not c.fetchone():
            register_date = datetime.now().strftime("%d.%m.%Y %H:%M")
            referral_link = f"https://t.me/nasvoystarss_bot?start=ref_{user_id}"
            c.execute("INSERT INTO users (user_id, username, first_name, register_date, referral_link, referrer_id) VALUES (?, ?, ?, ?, ?, ?)",
                     (user_id, username, first_name, register_date, referral_link, referrer_id))
            conn.commit()
            
            # Если есть реферер, начисляем бонус
            if referrer_id:
                logger.info(f"Пользователь {user_id} пришел по реферальной ссылке от {referrer_id}")
        
        conn.close()
        
        # Получаем баланс пользователя
        balance = get_user_balance(user_id)
        
        welcome_text = f"""Добро пожаловать! У нас Вы можете приобрести Telegram Stars, Telegram Premium и арендовать NFT.

🔒 Текущий баланс: {balance}₽.

Выберите действие"""
        
        bot.send_message(
            message.chat.id, 
            welcome_text, 
            reply_markup=create_main_keyboard()
        )
        logger.info(f"Пользователь {user_id} запустил бота")
    except Exception as e:
        logger.error(f"Ошибка в команде /start: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка. Пожалуйста, попробуйте позже.")

def get_user_balance(user_id):
    try:
        conn = sqlite3.connect('shop_bot.db')
        c = conn.cursor()
        c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else 0
    except:
        return 0

# Обработчик нажатий на inline кнопки
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
        chat_id = call.message.chat.id
        user_id = call.from_user.id
        message_id = call.message.message_id
        
        # Назад в главное меню
        if call.data == 'back_to_main':
            balance = get_user_balance(user_id)
            welcome_text = f"""Добро пожаловать! У нас Вы можете приобрести Telegram Stars, Telegram Premium и арендовать NFT.

🔒 Текущий баланс: {balance}₽.

Выберите действие"""
            bot.edit_message_text(
                welcome_text,
                chat_id,
                message_id,
                reply_markup=create_main_keyboard()
            )
            bot.answer_callback_query(call.id)
        
        # Меню покупки звезд
        elif call.data == 'buy_stars_menu':
            text = """Покупка Telegram Stars

- Цена Telegram Stars: 1.37₽/шт.

Нажмите кнопку ниже для покупки 🛒"""
            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=buy_stars_keyboard()
            )
            bot.answer_callback_query(call.id)
        
        # Ввод количества звезд
        elif call.data == 'buy_stars_input':
            text = """Покупка звёзд

- Цена за 1 звезду: **1.37₽/шт.;**
- Минимум: 50 звёзд;
- Максимум (за один заказ): 10 000 звёзд.
- Баланса хватает на покупку: ~0 звёзд (0₽).

---

**Введите количество звёзд для покупки:**"""
            
            markup = types.InlineKeyboardMarkup()
            btn = types.InlineKeyboardButton('❌ Отмена', callback_data='buy_stars_menu')
            markup.add(btn)
            
            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=markup
            )
            bot.answer_callback_query(call.id)
            # Здесь можно добавить регистратор следующего шага для ввода количества
        
        # Меню чеков
        elif call.data == 'checks_menu':
            text = """# Чеки

## Статистика:
- Всего чеков: 0;
- Активных: 0;
- Завершённых: 0.

Здесь вы можете создать чек для мгновенной отправки звёзд любому пользователю.

❌ Чеков не было"""
            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=checks_menu_keyboard()
            )
            bot.answer_callback_query(call.id)
        
        # Создание чека
        elif call.data == 'create_check':
            text = """# Создание чека

Выберите тип чека:
- Одноразовый — активируется один раз;
- Мульти-чек — можно активировать несколько раз."""
            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=check_type_keyboard()
            )
            bot.answer_callback_query(call.id)
        
        # Продажа звезд
        elif call.data == 'sell_stars_menu':
            text = """Продажа звёзд

- Цена за 1 звезду: 0.0118$.

Введите количество звёзд для продажи (минимум 100 звёзд):"""
            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=sell_stars_keyboard()
            )
            bot.answer_callback_query(call.id)
        
        # История продаж
        elif call.data == 'sell_history':
            text = """История продажи звезд

Всего транзакций: 0.
Страница 1 из 1.

Нажмите на транзакцию для просмотра деталей:

❌ История продажи звезд пуста"""
            
            markup = types.InlineKeyboardMarkup()
            btn = types.InlineKeyboardButton('◀️ Назад', callback_data='sell_stars_menu')
            markup.add(btn)
            
            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=markup
            )
            bot.answer_callback_query(call.id)
        
        # Аренда NFT
        elif call.data == 'rent_nft':
            text = "🚧 Раздел «Аренда NFT» находится в разработке. Скоро здесь появится информация!"
            bot.send_message(chat_id, text)
            bot.answer_callback_query(call.id)
        
        # Покупка NFT
        elif call.data == 'buy_nft':
            text = """Покупка NFT-подарка

Выберите коллекцию или воспользуйтесь веб-каталогом, чтобы посмотреть подробности и приобрести подарок 👏"""
            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=nft_menu_keyboard()
            )
            bot.answer_callback_query(call.id)
        
        # Веб-каталог NFT
        elif call.data == 'nft_web_catalog':
            # Здесь можно добавить ссылку на веб-каталог
            web_app = types.WebAppInfo("https://example.com/nft-catalog")
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton("🌐 Открыть каталог", web_app=web_app)
            btn2 = types.InlineKeyboardButton("◀️ Назад", callback_data='buy_nft')
            markup.add(btn1, btn2)
            
            bot.edit_message_text(
                "Открываю веб-каталог NFT...",
                chat_id,
                message_id,
                reply_markup=markup
            )
            bot.answer_callback_query(call.id)
        
        # Покупка обычного подарка
        elif call.data == 'buy_gift':
            text = """Покупка подарка.

Введите юзернейм пользователя, которому будем дарить подарок:
— Пример: @username"""
            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=gift_recipient_keyboard()
            )
            bot.answer_callback_query(call.id)
        
        # Покупка для себя
        elif call.data == 'gift_for_self':
            recipient = "@" + call.from_user.username if call.from_user.username else "пользователь"
            text = f"""Покупка подарка 🎁 Получатель: {recipient}.
Текущий баланс: 0 RUB.

Подарок для покупки:"""
            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=gift_selection_keyboard(recipient)
            )
            bot.answer_callback_query(call.id)
        
        # Премиум
        elif call.data == 'premium':
            text = """# Покупка Telegram Premium

Выберите период подписки:"""
            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=premium_keyboard()
            )
            bot.answer_callback_query(call.id)
        
        # Пополнение баланса
        elif call.data == 'deposit':
            text = """# Пополнение баланса

Выберите удобный способ пополнения:"""
            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=deposit_methods_keyboard()
            )
            bot.answer_callback_query(call.id)
        
        # Профиль
        elif call.data == 'profile':
            # Получаем данные пользователя из БД
            conn = sqlite3.connect('shop_bot.db')
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user_data = c.fetchone()
            conn.close()
            
            username = call.from_user.username or "NoUsername"
            register_date = user_data[5] if user_data and len(user_data) > 5 else datetime.now().strftime("%d.%m.%Y %H:%M")
            
            text = f"""Профиль

ID: {user_id};
Username: @{username}.

Баланс: 0Р;
Общий депозит: 0Р.

Заказы:
- Всего заказов: 0;
- Выполнено: 0;
- В обработке: 0;
- Арендовано NFT-подарков: 0 шт. (~0Р);
- Арендовано NFT-username: 0 шт. (~0Р);
- Куплено подарков: 0 шт. (~0Р);
- Всего куплено звёзд: 0 шт. (~0Р).

Регистрация: {register_date}."""
            
            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=profile_keyboard()
            )
            bot.answer_callback_query(call.id)
        
        # Поддержка
        elif call.data == 'support':
            text = """Техническая поддержка

В этом разделе Вы можете создать тикет для связи с поддержкой.

Статистика:
- Активных тикетов: 0

Вы можете создать новый тикет для обращения в поддержку."""
            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=support_keyboard()
            )
            bot.answer_callback_query(call.id)
        
        # Создание тикета
        elif call.data == 'create_ticket':
            bot.send_message(chat_id, "🚧 Функция создания тикетов в разработке. Пока можете написать в поддержку: @CBACTOH_DEDA")
            bot.answer_callback_query(call.id)
        
        # Калькулятор
        elif call.data == 'calculator':
            text = """# Калькулятор

**Курс:** 1 звезда = 1.37₽.

Выберите направление конвертации ⬇️"""
            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=calculator_keyboard()
            )
            bot.answer_callback_query(call.id)
        
        # Конвертация звезды -> рубли
        elif call.data == 'calc_stars_to_rub':
            bot.send_message(chat_id, "Введите количество звёзд для конвертации в рубли:")
            bot.answer_callback_query(call.id)
        
        # Конвертация рубли -> звезды
        elif call.data == 'calc_rub_to_stars':
            bot.send_message(chat_id, "Введите сумму в рублях для конвертации в звёзды:")
            bot.answer_callback_query(call.id)
        
        # Информация
        elif call.data == 'info':
            bot.edit_message_text(
                INFO_TEXT,
                chat_id,
                message_id,
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton('◀️ Назад', callback_data='back_to_main')
                )
            )
            bot.answer_callback_query(call.id)
        
        # Отзывы
        elif call.data == 'reviews':
            # Открывается отдельное приложение в ТГ
            reviews_app = types.WebAppInfo("https://example.com/reviews")  # Замените на реальный URL
            markup = types.InlineKeyboardMarkup()
            btn = types.InlineKeyboardButton("📱 Открыть отзывы", web_app=reviews_app)
            btn_back = types.InlineKeyboardButton("◀️ Назад", callback_data='back_to_main')
            markup.add(btn, btn_back)
            
            bot.edit_message_text(
                "Открываю приложение с отзывами...",
                chat_id,
                message_id,
                reply_markup=markup
            )
            bot.answer_callback_query(call.id)
        
        # Реферальная система
        elif call.data == 'referral':
            referral_link, markup = referral_keyboard(user_id)
            text = f"""# Реферальная система

- Ваша личная реферальная ссылка:  
  {referral_link}

Приглашайте новых пользователей и получайте **50% от прибыли сервиса с их покупок!**

- Количество рефералов: **0 человек**;
- Заработано с рефералов: **0₽**."""
            
            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=markup
            )
            bot.answer_callback_query(call.id)
        
        # Копирование реферальной ссылки
        elif call.data == 'copy_referral_link':
            referral_link = f"https://t.me/nasvoystarss_bot?start=ref_{user_id}"
            bot.answer_callback_query(call.id, text="Ссылка скопирована! (тест)", show_alert=True)
        
        # Обработка выбора подарков (заглушки)
        elif call.data.startswith('gift_'):
            bot.answer_callback_query(call.id, text="🚧 Покупка подарков в разработке", show_alert=True)
        
        # Обработка выбора NFT коллекций (заглушки)
        elif call.data.startswith('nft_'):
            bot.answer_callback_query(call.id, text="🚧 Просмотр коллекций в разработке", show_alert=True)
        
        # Обработка способов оплаты (заглушки)
        elif call.data.startswith('deposit_'):
            bot.answer_callback_query(call.id, text="🚧 Пополнение в разработке", show_alert=True)
        
        # Обработка премиум периодов (заглушки)
        elif call.data.startswith('premium_'):
            bot.answer_callback_query(call.id, text="🚧 Покупка Premium в разработке", show_alert=True)
        
        # Остальные callback'и
        else:
            bot.answer_callback_query(call.id, text="🚧 В разработке")
            
    except Exception as e:
        logger.error(f"Ошибка при обработке callback: {e}")
        bot.answer_callback_query(call.id, "Произошла ошибка")

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    try:
        chat_id = message.chat.id
        text = message.text
        
        # Обработка ввода количества звезд
        if text.isdigit():
            amount = int(text)
            if amount < 50:
                bot.send_message(chat_id, "❌ Минимальное количество: 50 звёзд")
            elif amount > 10000:
                bot.send_message(chat_id, "❌ Максимальное количество: 10 000 звёзд")
            else:
                price = amount * 1.37
                bot.send_message(
                    chat_id, 
                    f"✅ К покупке: {amount} звёзд\nСумма: {price:.2f}₽\n\nДля подтверждения свяжитесь с @CBACTOH_DEDA"
                )
        
        # Обработка ввода юзернейма для подарка
        elif text.startswith('@') or text.isalnum():
            if text.startswith('@'):
                username = text
            else:
                username = f"@{text}"
            
            gift_text = f"""Покупка подарка 🎁 Получатель: {username}.
Текущий баланс: 0 RUB.

Подарок для покупки:"""
            
            bot.send_message(
                chat_id,
                gift_text,
                reply_markup=gift_selection_keyboard(username)
            )
        
        # Обработка команд
        elif text == '/help':
            bot.send_message(chat_id, "Используйте кнопки меню для навигации. /start - главное меню")
        elif text == '/owner' and message.from_user.id == OWNER_ID:
            bot.send_message(chat_id, "✅ Бот работает и готов к использованию!")
        else:
            bot.send_message(
                chat_id, 
                "Пожалуйста, воспользуйтесь кнопками меню.", 
                reply_markup=create_main_keyboard()
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
