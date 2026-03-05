import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import sqlite3
from datetime import datetime
import random
import string
import os
import sys

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# ТОКЕН БОТА (берем из переменных окружения Railway)
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    logger.error("BOT_TOKEN не найден в переменных окружения!")
    BOT_TOKEN = "8408406226:AAGEYZV9CB1DQfPQE7w3QsmfNg3xCpck2xs"  # Запасной вариант

# ID АДМИНИСТРАТОРА (берем из переменных окружения)
try:
    admin_id = os.environ.get('ADMIN_ID', "5842443017")
    ADMIN_IDS = [int(admin_id)]
except:
    ADMIN_IDS = [5842443017]

# Цена 1 звезды в рублях
STAR_PRICE = 1.5

# Минимальная сумма покупки
MIN_STARS = 50

# База данных
def init_db():
    try:
        conn = sqlite3.connect('shop_bot.db')
        c = conn.cursor()
        
        # Таблица пользователей
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (user_id INTEGER PRIMARY KEY,
                      username TEXT,
                      first_name TEXT,
                      balance REAL DEFAULT 0,
                      total_purchased REAL DEFAULT 0,
                      referral_code TEXT UNIQUE,
                      referred_by INTEGER,
                      register_date TEXT,
                      last_active TEXT)''')
        
        # Таблица покупок
        c.execute('''CREATE TABLE IF NOT EXISTS purchases
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      item_type TEXT,
                      item_name TEXT,
                      amount REAL,
                      price REAL,
                      payment_method TEXT,
                      status TEXT,
                      date TEXT)''')
        
        # Таблица заказов (для ручной проверки)
        c.execute('''CREATE TABLE IF NOT EXISTS orders
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      item_type TEXT,
                      item_name TEXT,
                      amount REAL,
                      total_price REAL,
                      payment_method TEXT,
                      payment_details TEXT,
                      screenshot_file_id TEXT,
                      status TEXT DEFAULT 'pending',
                      admin_note TEXT,
                      date TEXT,
                      completed_date TEXT)''')
        
        # Таблица рефералов
        c.execute('''CREATE TABLE IF NOT EXISTS referrals
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      referrer_id INTEGER,
                      referred_id INTEGER,
                      bonus REAL,
                      date TEXT)''')
        
        # Таблица NFT
        c.execute('''CREATE TABLE IF NOT EXISTS nft_items
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT,
                      description TEXT,
                      price_ton REAL,
                      price_usd REAL,
                      price_rub REAL,
                      image_url TEXT,
                      external_link TEXT,
                      available INTEGER DEFAULT 1)''')
        
        # Таблица отзывов
        c.execute('''CREATE TABLE IF NOT EXISTS reviews
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      username TEXT,
                      review_text TEXT,
                      rating INTEGER,
                      date TEXT,
                      approved INTEGER DEFAULT 0)''')
        
        conn.commit()
        conn.close()
        
        # Добавляем тестовые NFT
        add_sample_nft()
        logger.info("База данных инициализирована успешно")
    except Exception as e:
        logger.error(f"Ошибка инициализации БД: {e}")

# Генерация реферального кода
def generate_referral_code(user_id):
    return f"REF{user_id}{''.join(random.choices(string.ascii_uppercase + string.digits, k=5))}"

# Добавляем тестовые NFT
def add_sample_nft():
    try:
        conn = sqlite3.connect('shop_bot.db')
        c = conn.cursor()
        
        # Проверяем, есть ли уже NFT
        c.execute("SELECT COUNT(*) FROM nft_items")
        count = c.fetchone()[0]
        
        if count == 0:
            sample_nfts = [
                ("Cosmic #001", "Уникальная космическая NFT", 5, 50, 4500, "https://example.com/nft1.jpg", "https://getgems.io/collection/..."),
                ("Cyber Punk #042", "Киберпанк коллекция", 7.5, 75, 6750, "https://example.com/nft2.jpg", "https://getgems.io/collection/..."),
                ("Abstract Art #123", "Абстрактное искусство", 10, 100, 9000, "https://example.com/nft3.jpg", "https://getgems.io/collection/..."),
            ]
            
            for nft in sample_nfts:
                c.execute("INSERT INTO nft_items (name, description, price_ton, price_usd, price_rub, image_url, external_link) VALUES (?, ?, ?, ?, ?, ?, ?)",
                          nft)
            conn.commit()
            logger.info("Тестовые NFT добавлены")
        
        conn.close()
    except Exception as e:
        logger.error(f"Ошибка добавления NFT: {e}")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        conn = sqlite3.connect('shop_bot.db')
        c = conn.cursor()
        
        # Проверяем реферальный код
        args = context.args
        referred_by = None
        if args and args[0].startswith('REF'):
            c.execute("SELECT user_id FROM users WHERE referral_code = ?", (args[0],))
            result = c.fetchone()
            if result:
                referred_by = result[0]
        
        # Проверяем, есть ли пользователь в БД
        c.execute("SELECT * FROM users WHERE user_id = ?", (user.id,))
        existing_user = c.fetchone()
        
        if not existing_user:
            referral_code = generate_referral_code(user.id)
            c.execute("""
                INSERT INTO users 
                (user_id, username, first_name, referral_code, referred_by, register_date, last_active) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user.id, user.username, user.first_name, referral_code, referred_by, 
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            # Если есть реферер, начисляем бонус
            if referred_by:
                c.execute("""
                    INSERT INTO referrals (referrer_id, referred_id, bonus, date)
                    VALUES (?, ?, ?, ?)
                """, (referred_by, user.id, 10, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                
                c.execute("UPDATE users SET balance = balance + 10 WHERE user_id = ?", (referred_by,))
        
        conn.commit()
        conn.close()
        
        # Главное меню
        welcome_text = f"""
🌟 Добро пожаловать в Star Shop, {user.first_name}!

Мы продаем:
✨ Telegram Stars (от 50 шт)
🖼️ Уникальные NFT

Выберите раздел в меню ниже:
        """
        
        keyboard = [
            [InlineKeyboardButton("✨ Купить звезды", callback_data="buy_stars")],
            [InlineKeyboardButton("🖼️ Купить NFT", callback_data="buy_nft")],
            [InlineKeyboardButton("👤 Мой профиль", callback_data="profile")],
            [InlineKeyboardButton("📋 Правила", callback_data="rules")],
            [InlineKeyboardButton("⭐ Отзывы", callback_data="reviews")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Ошибка в start: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")

# Обработчик сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        text = update.message.text
        
        # Проверяем, ожидаем ли мы ввод суммы звезд
        if context.user_data.get('action') == 'awaiting_stars_amount':
            try:
                stars_amount = int(text)
                if stars_amount < 50:
                    await update.message.reply_text("❌ Минимальная сумма: 50 звезд. Введите другое число:")
                    return
                
                # Рассчитываем цену
                price_rub = stars_amount * STAR_PRICE
                context.user_data['stars_amount'] = stars_amount
                context.user_data['price_rub'] = price_rub
                context.user_data['item_type'] = 'stars'
                context.user_data['item_name'] = f"{stars_amount} ⭐"
                
                # Показываем способы оплаты
                await show_payment_methods(update, context)
                
            except ValueError:
                await update.message.reply_text("❌ Пожалуйста, введите число (например: 100)")
        
        # Проверяем, ожидаем ли мы текст отзыва
        elif context.user_data.get('action') == 'awaiting_review':
            rating = context.user_data.get('review_rating', 5)
            
            conn = sqlite3.connect('shop_bot.db')
            c = conn.cursor()
            c.execute("""
                INSERT INTO reviews (user_id, username, review_text, rating, date)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, update.effective_user.username, text, rating, 
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()
            
            context.user_data['action'] = None
            await update.message.reply_text("✅ Спасибо за отзыв! Он появится после проверки администратором.")
        
        # Проверяем, не скриншот ли это
        elif update.message.photo:
            if context.user_data.get('awaiting_screenshot'):
                order_id = context.user_data.get('current_order_id')
                if order_id:
                    # Сохраняем ID скриншота
                    photo = update.message.photo[-1]
                    file_id = photo.file_id
                    
                    conn = sqlite3.connect('shop_bot.db')
                    c = conn.cursor()
                    c.execute("UPDATE orders SET screenshot_file_id = ?, status = 'paid' WHERE id = ?", (file_id, order_id))
                    
                    # Получаем информацию о заказе для уведомления админу
                    c.execute("""
                        SELECT o.*, u.username, u.first_name 
                        FROM orders o 
                        JOIN users u ON o.user_id = u.user_id 
                        WHERE o.id = ?
                    """, (order_id,))
                    order = c.fetchone()
                    conn.commit()
                    conn.close()
                    
                    # Уведомляем админа
                    await notify_admin_new_order(update, context, order)
                    
                    context.user_data['awaiting_screenshot'] = False
                    await update.message.reply_text("✅ Скриншот получен! Администратор проверит оплату и выдаст товар.")
            else:
                await update.message.reply_text("ℹ️ Чтобы отправить скриншот оплаты, сначала оформите заказ.")
    except Exception as e:
        logger.error(f"Ошибка в handle_message: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")

# Показ способов оплаты
async def show_payment_methods(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
💳 **Выберите способ оплаты:**

• 🤖 CryptoBot - быстро и удобно
• 💎 TON - криптовалюта
• 💵 USD - доллары (USDT)
    """
    
    keyboard = [
        [InlineKeyboardButton("🤖 CryptoBot", callback_data="pay_crypto")],
        [InlineKeyboardButton("💎 TON", callback_data="pay_ton")],
        [InlineKeyboardButton("💵 USD", callback_data="pay_usd")],
        [InlineKeyboardButton("◀️ Назад", callback_data="buy_stars")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# Уведомление админа о новом заказе
async def notify_admin_new_order(update: Update, context: ContextTypes.DEFAULT_TYPE, order):
    for admin_id in ADMIN_IDS:
        try:
            # Отправляем уведомление админу
            order_id, user_id, item_type, item_name, amount, total_price, payment_method, payment_details, screenshot_file_id, status, admin_note, date, completed_date, username, first_name = order
            
            text = f"""
🔔 **Новый заказ #{order_id}**

👤 Пользователь: {first_name} (@{username})
📦 Товар: {item_name}
💰 Сумма: {total_price} руб.
💳 Способ оплаты: {payment_method}
📅 Дата: {date}

🖼 Скриншот прилагается:
            """
            
            # Отправляем скриншот
            await context.bot.send_photo(
                chat_id=admin_id,
                photo=screenshot_file_id,
                caption=text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm_order_{order_id}"),
                    InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_order_{order_id}")
                ]])
            )
        except Exception as e:
            logger.error(f"Ошибка уведомления админа {admin_id}: {e}")

# Обработчик кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "buy_stars":
            await buy_stars_menu(query, context)
        elif data == "buy_nft":
            await buy_nft_menu(query, context)
        elif data == "profile":
            await show_profile(query, context)
        elif data == "rules":
            await show_rules(query, context)
        elif data == "reviews":
            await show_reviews(query, context)
        elif data == "history":
            await purchase_history(query, context)
        elif data == "referrals":
            await show_referrals(query, context)
        elif data == "write_review":
            await write_review(query, context)
        elif data == "main_menu":
            await return_to_main(query, context)
        elif data.startswith("nft_"):
            await process_nft_purchase(query, context)
        elif data in ["pay_crypto", "pay_ton", "pay_usd"]:
            await process_payment(query, context, data)
        elif data.startswith("confirm_order_"):
            await confirm_order(query, context)
        elif data.startswith("reject_order_"):
            await reject_order(query, context)
        elif data == "admin_panel":
            await admin_panel(query, context)
        elif data == "admin_orders":
            await admin_orders(query, context)
        elif data == "admin_stats":
            await admin_stats(query, context)
    except Exception as e:
        logger.error(f"Ошибка в button_handler: {e}")

async def buy_stars_menu(query, context):
    """Меню покупки звезд"""
    text = """
✨ **Покупка Telegram Stars**

Минимальная сумма: 50 звезд
Цена: 1.5 рубля за 1 звезду

Введите количество звезд (число от 50):
    """
    
    context.user_data['action'] = 'awaiting_stars_amount'
    
    keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def buy_nft_menu(query, context):
    """Меню покупки NFT"""
    try:
        conn = sqlite3.connect('shop_bot.db')
        c = conn.cursor()
        c.execute("SELECT id, name, description, price_ton, price_usd, price_rub FROM nft_items WHERE available = 1")
        nfts = c.fetchall()
        conn.close()
        
        if not nfts:
            text = "🖼️ В данный момент NFT отсутствуют в продаже"
            keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="main_menu")]]
        else:
            text = "🖼️ **Доступные NFT:**\n\n"
            keyboard = []
            
            for nft in nfts:
                nft_id, name, description, price_ton, price_usd, price_rub = nft
                text += f"**{name}**\n{description}\n💎 {price_ton} TON | 💵 {price_usd}$ | 💰 {price_rub} руб.\n\n"
                keyboard.append([InlineKeyboardButton(f"Купить {name}", callback_data=f"nft_{nft_id}")])
            
            keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="main_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Ошибка в buy_nft_menu: {e}")
        await query.edit_message_text("Произошла ошибка. Попробуйте позже.")

async def process_nft_purchase(query, context):
    """Обработка покупки NFT"""
    try:
        nft_id = int(query.data.split("_")[1])
        
        conn = sqlite3.connect('shop_bot.db')
        c = conn.cursor()
        c.execute("SELECT name, price_ton, price_usd, price_rub, external_link FROM nft_items WHERE id = ?", (nft_id,))
        nft = c.fetchone()
        conn.close()
        
        if not nft:
            await query.edit_message_text("❌ NFT не найдена")
            return
        
        name, price_ton, price_usd, price_rub, external_link = nft
        context.user_data['item_type'] = 'nft'
        context.user_data['item_name'] = name
        context.user_data['nft_id'] = nft_id
        context.user_data['price_ton'] = price_ton
        context.user_data['price_usd'] = price_usd
        context.user_data['price_rub'] = price_rub
        
        text = f"""
🖼️ **Покупка NFT: {name}**

💎 Цена: {price_ton} TON
💵 Цена: {price_usd}$
💰 Цена: {price_rub} руб.

Выберите способ оплаты:
        """
        
        keyboard = [
            [InlineKeyboardButton("🤖 CryptoBot", callback_data="pay_crypto")],
            [InlineKeyboardButton("💎 TON", callback_data="pay_ton")],
            [InlineKeyboardButton("💵 USD", callback_data="pay_usd")],
            [InlineKeyboardButton("◀️ Назад", callback_data="buy_nft")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Ошибка в process_nft_purchase: {e}")
        await query.edit_message_text("Произошла ошибка. Попробуйте позже.")

async def process_payment(query, context, payment_method):
    """Обработка выбора способа оплаты"""
    try:
        method_names = {
            'pay_crypto': '🤖 CryptoBot',
            'pay_ton': '💎 TON',
            'pay_usd': '💵 USD'
        }
        
        method_name = method_names.get(payment_method, payment_method)
        
        # ТВОИ РЕКВИЗИТЫ ДЛЯ ОПЛАТЫ
        payment_details = {
            'pay_crypto': "🤖 **CryptoBot**\nНик: `@CBACTOH_DEDA`\nID: `5842443017`",
            'pay_ton': "💎 **TON**\nАдрес кошелька:\n`UQDcg7iE65dSQy9yJGvAO_Qem0t-RE6lZA2BcuXyxdx6AsLO`",
            'pay_usd': "💵 **USD (USDT)**\nАдрес USDT (TRC20):\n`UQDcg7iE65dSQy9yJGvAO_Qem0t-RE6lZA2BcuXyxdx6AsLO`"
        }
        
        # Создаем заказ в БД
        user_id = query.from_user.id
        item_type = context.user_data.get('item_type')
        item_name = context.user_data.get('item_name')
        
        if item_type == 'stars':
            amount = context.user_data.get('stars_amount')
            total_price = context.user_data.get('price_rub')
        else:  # nft
            amount = context.user_data.get('price_rub')
            total_price = context.user_data.get('price_rub')
        
        conn = sqlite3.connect('shop_bot.db')
        c = conn.cursor()
        c.execute("""
            INSERT INTO orders (user_id, item_type, item_name, amount, total_price, payment_method, payment_details, date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, item_type, item_name, amount, total_price, method_name, payment_details[payment_method],
              datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        order_id = c.lastrowid
        conn.commit()
        conn.close()
        
        context.user_data['current_order_id'] = order_id
        context.user_data['awaiting_screenshot'] = True
        
        text = f"""
🧾 **Заказ #{order_id}**

Товар: {item_name}
Сумма: {total_price} руб.
Способ: {method_name}

**Реквизиты для оплаты:**
{payment_details[payment_method]}

📸 **После оплаты отправьте скриншот подтверждения в этот чат!**

Администратор проверит оплату и выдаст товар вручную.
        """
        
        keyboard = [[InlineKeyboardButton("◀️ Отмена", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Ошибка в process_payment: {e}")
        await query.edit_message_text("Произошла ошибка. Попробуйте позже.")

async def confirm_order(query, context):
    """Подтверждение заказа администратором"""
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("⛔ У вас нет прав администратора", show_alert=True)
        return
    
    try:
        order_id = int(query.data.split("_")[2])
        
        conn = sqlite3.connect('shop_bot.db')
        c = conn.cursor()
        
        # Обновляем статус заказа
        c.execute("""
            UPDATE orders 
            SET status = 'completed', completed_date = ?, admin_note = 'Подтверждено администратором'
            WHERE id = ?
        """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), order_id))
        
        # Получаем информацию о заказе и пользователе
        c.execute("""
            SELECT o.*, u.first_name, u.username 
            FROM orders o 
            JOIN users u ON o.user_id = u.user_id 
            WHERE o.id = ?
        """, (order_id,))
        order = c.fetchone()
        
        conn.commit()
        conn.close()
        
        if order:
            order_id, user_id, item_type, item_name, amount, total_price, payment_method, payment_details, screenshot_file_id, status, admin_note, date, completed_date, first_name, username = order
            
            # Уведомляем пользователя
            try:
                text = f"""
✅ **Заказ #{order_id} подтвержден!**

Товар: {item_name}
Сумма: {total_price} руб.

"""
                if item_type == 'stars':
                    text += f"✨ Вам начислено {amount} звезд!"
                else:
                    # Для NFT отправляем ссылку
                    conn = sqlite3.connect('shop_bot.db')
                    c = conn.cursor()
                    c.execute("SELECT external_link FROM nft_items WHERE name = ?", (item_name,))
                    nft_link = c.fetchone()
                    conn.close()
                    if nft_link:
                        text += f"🖼️ Ссылка на NFT: {nft_link[0]}"
                
                await context.bot.send_message(chat_id=user_id, text=text)
            except Exception as e:
                logger.error(f"Ошибка уведомления пользователя {user_id}: {e}")
        
        await query.edit_message_caption(
            caption=f"✅ Заказ #{order_id} подтвержден и выполнен",
            reply_markup=None
        )
    except Exception as e:
        logger.error(f"Ошибка в confirm_order: {e}")

async def reject_order(query, context):
    """Отклонение заказа администратором"""
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("⛔ У вас нет прав администратора", show_alert=True)
        return
    
    try:
        order_id = int(query.data.split("_")[2])
        
        conn = sqlite3.connect('shop_bot.db')
        c = conn.cursor()
        
        c.execute("""
            UPDATE orders 
            SET status = 'cancelled', admin_note = 'Отклонено администратором'
            WHERE id = ?
        """, (order_id,))
        
        c.execute("SELECT user_id, item_name FROM orders WHERE id = ?", (order_id,))
        user_id, item_name = c.fetchone()
        
        conn.commit()
        conn.close()
        
        # Уведомляем пользователя
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"❌ Заказ #{order_id} на {item_name} отклонен.\nПлатеж не подтвержден. Попробуйте оформить заказ заново или свяжитесь с поддержкой."
            )
        except Exception as e:
            logger.error(f"Ошибка уведомления пользователя {user_id}: {e}")
        
        await query.edit_message_caption(
            caption=f"❌ Заказ #{order_id} отклонен",
            reply_markup=None
        )
    except Exception as e:
        logger.error(f"Ошибка в reject_order: {e}")

async def show_profile(query, context):
    """Профиль пользователя"""
    try:
        user_id = query.from_user.id
        
        conn = sqlite3.connect('shop_bot.db')
        c = conn.cursor()
        
        c.execute("SELECT balance, total_purchased, referral_code FROM users WHERE user_id = ?", (user_id,))
        user_data = c.fetchone()
        
        if not user_data:
            await query.edit_message_text("❌ Пользователь не найден")
            return
        
        c.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (user_id,))
        referrals_count = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM purchases WHERE user_id = ? AND status = 'completed'", (user_id,))
        purchases_count = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM orders WHERE user_id = ? AND status = 'pending'", (user_id,))
        pending_orders = c.fetchone()[0]
        
        conn.close()
        
        balance, total_purchased, referral_code = user_data
        
        text = f"""
👤 **Мой профиль**

💰 Баланс: {balance} руб.
📊 Всего покупок: {purchases_count}
💎 Потрачено всего: {total_purchased} руб.
⏳ Ожидают проверки: {pending_orders}
👥 Рефералов: {referrals_count}

🔗 Ваша реферальная ссылка:
`https://t.me/DedyshkaSHOPbot?start={referral_code}`
        """
        
        keyboard = [
            [InlineKeyboardButton("📜 История покупок", callback_data="history")],
            [InlineKeyboardButton("👥 Рефералы", callback_data="referrals")],
            [InlineKeyboardButton("◀️ Назад", callback_data="main_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Ошибка в show_profile: {e}")
        await query.edit_message_text("Произошла ошибка. Попробуйте позже.")

async def purchase_history(query, context):
    """История покупок"""
    try:
        user_id = query.from_user.id
        
        conn = sqlite3.connect('shop_bot.db')
        c = conn.cursor()
        c.execute("""
            SELECT item_name, total_price, status, date 
            FROM orders 
            WHERE user_id = ? 
            ORDER BY date DESC LIMIT 10
        """, (user_id,))
        orders = c.fetchall()
        conn.close()
        
        if orders:
            text = "📜 **Последние заказы:**\n\n"
            for item_name, price, status, date in orders:
                status_emoji = "✅" if status == "completed" else "⏳" if status == "pending" else "❌"
                text += f"{status_emoji} {item_name} - {price} руб. ({date[:10]})\n"
        else:
            text = "📜 У вас пока нет заказов"
        
        keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="profile")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Ошибка в purchase_history: {e}")
        await query.edit_message_text("Произошла ошибка. Попробуйте позже.")

async def show_referrals(query, context):
    """Информация о рефералах"""
    try:
        user_id = query.from_user.id
        
        conn = sqlite3.connect('shop_bot.db')
        c = conn.cursor()
        c.execute("""
            SELECT u.first_name, u.username, r.date, r.bonus
            FROM referrals r
            JOIN users u ON r.referred_id = u.user_id
            WHERE r.referrer_id = ?
            ORDER BY r.date DESC
        """, (user_id,))
        referrals = c.fetchall()
        conn.close()
        
        if referrals:
            text = "👥 **Ваши рефералы:**\n\n"
            for first_name, username, date, bonus in referrals:
                text += f"• {first_name} (@{username}) - {date[:10]} (бонус: {bonus} руб.)\n"
        else:
            text = "👥 У вас пока нет рефералов\n\nПриглашайте друзей и получайте бонусы!"
        
        keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="profile")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Ошибка в show_referrals: {e}")
        await query.edit_message_text("Произошла ошибка. Попробуйте позже.")

async def show_rules(query, context):
    """Правила магазина"""
    text = """
📋 **Правила магазина Star Shop**

1. Минимальная сумма покупки звезд - 50 шт
2. Цена фиксированная - 1.5 рубля за звезду
3. После оплаты **обязательно отправьте скриншот**
4. Администратор проверяет оплату вручную
5. Время проверки - до 24 часов (обычно быстрее)
6. NFT выдаются ссылкой на внешний ресурс
7. Возврат средств возможен только до подтверждения заказа
8. Запрещено использовать бот для незаконных действий

По всем вопросам: @CBACTOH_DEDA
    """
    
    keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_reviews(query, context):
    """Отзывы покупателей"""
    try:
        conn = sqlite3.connect('shop_bot.db')
        c = conn.cursor()
        c.execute("SELECT username, review_text, rating, date FROM reviews WHERE approved = 1 ORDER BY date DESC LIMIT 10")
        reviews = c.fetchall()
        conn.close()
        
        if reviews:
            text = "⭐ **Отзывы наших покупателей:**\n\n"
            for username, review, rating, date in reviews:
                stars = "⭐" * rating
                text += f"{stars} **@{username}** ({date[:10]}):\n{review}\n\n"
        else:
            text = "⭐ Пока нет отзывов. Будьте первым!"
        
        keyboard = [
            [InlineKeyboardButton("✍️ Оставить отзыв", callback_data="write_review")],
            [InlineKeyboardButton("◀️ Назад", callback_data="main_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Ошибка в show_reviews: {e}")
        await query.edit_message_text("Произошла ошибка. Попробуйте позже.")

async def write_review(query, context):
    """Написать отзыв"""
    text = """
⭐ **Напишите ваш отзыв**

Отправьте сообщение с вашим отзывом.
После проверки администратором он появится в общем списке.
    """
    
    context.user_data['action'] = 'awaiting_review'
    context.user_data['review_rating'] = 5
    
    keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="reviews")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def admin_panel(query, context):
    """Админ-панель"""
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("⛔ У вас нет доступа", show_alert=True)
        return
    
    text = "🔐 **Админ-панель**\n\nВыберите действие:"
    
    keyboard = [
        [InlineKeyboardButton("📦 Новые заказы", callback_data="admin_orders")],
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("◀️ Назад", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def admin_orders(query, context):
    """Просмотр заказов для админа"""
    if query.from_user.id not in ADMIN_IDS:
        return
    
    try:
        conn = sqlite3.connect('shop_bot.db')
        c = conn.cursor()
        c.execute("""
            SELECT o.id, u.first_name, u.username, o.item_name, o.total_price, o.status, o.date
            FROM orders o
            JOIN users u ON o.user_id = u.user_id
            WHERE o.status = 'pending'
            ORDER BY o.date DESC
        """)
        orders = c.fetchall()
        conn.close()
        
        if orders:
            text = "📦 **Новые заказы:**\n\n"
            for order in orders[:5]:  # Показываем последние 5
                order_id, name, username, item, price, status, date = order
                text += f"#{order_id} {name} (@{username})\n{item} - {price} руб.\n{date[:16]}\n\n"
        else:
            text = "📦 Нет новых заказов"
        
        keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="admin_panel")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Ошибка в admin_orders: {e}")
        await query.edit_message_text("Произошла ошибка. Попробуйте позже.")

async def admin_stats(query, context):
    """Статистика для админа"""
    if query.from_user.id not in ADMIN_IDS:
        return
    
    try:
        conn = sqlite3.connect('shop_bot.db')
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM users")
        total_users = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM orders WHERE status = 'completed'")
        completed_orders = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM orders WHERE status = 'pending'")
        pending_orders = c.fetchone()[0]
        
        c.execute("SELECT SUM(total_price) FROM orders WHERE status = 'completed'")
        total_earned = c.fetchone()[0] or 0
        
        c.execute("SELECT COUNT(*) FROM users WHERE date(register_date) = date('now')")
        new_users_today = c.fetchone()[0]
        
        conn.close()
        
        text = f"""
📊 **Статистика магазина**

👥 Всего пользователей: {total_users}
🆕 Новых сегодня: {new_users_today}

📦 Всего заказов: {completed_orders + pending_orders}
✅ Выполнено: {completed_orders}
⏳ В ожидании: {pending_orders}

💰 Общая выручка: {total_earned} руб.
        """
        
        keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="admin_panel")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Ошибка в admin_stats: {e}")
        await query.edit_message_text("Произошла ошибка. Попробуйте позже.")

async def return_to_main(query, context):
    """Возврат в главное меню"""
    user = query.from_user
    
    text = f"""
🌟 Добро пожаловать в Star Shop, {user.first_name}!

Мы продаем:
✨ Telegram Stars (от 50 шт)
🖼️ Уникальные NFT

Выберите раздел в меню ниже:
    """
    
    keyboard = [
        [InlineKeyboardButton("✨ Купить звезды", callback_data="buy_stars")],
        [InlineKeyboardButton("🖼️ Купить NFT", callback_data="buy_nft")],
        [InlineKeyboardButton("👤 Мой профиль", callback_data="profile")],
        [InlineKeyboardButton("📋 Правила", callback_data="rules")],
        [InlineKeyboardButton("⭐ Отзывы", callback_data="reviews")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

# Запуск бота
def main():
    try:
        # Инициализация БД
        init_db()
        
        # Создание приложения
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Обработчики команд
        application.add_handler(CommandHandler("start", start))
        
        # Обработчик сообщений (текст и фото)
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_handler(MessageHandler(filters.PHOTO, handle_message))
        
        # Обработчик callback-запросов
        application.add_handler(CallbackQueryHandler(button_handler))
        
        print("✅ Бот запущен...")
        print(f"👑 Админ ID: {ADMIN_IDS}")
        print(f"🤖 Бот токен: {BOT_TOKEN[:10]}...")
        
        # Запускаем бота (исправленная строка)
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске: {e}")
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    main()
