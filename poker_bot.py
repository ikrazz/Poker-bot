import json
import os
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8178314234:AAGbsPzufZBjWvVvQ2ka1ytdqiZXQnzCvUk"
YOUR_USER_ID = 5252767835
DB_FILE = "users.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE) as f:
            return json.load(f)
    return {}

def save_db(db):
    with open(DB_FILE, 'w') as f:
        json.dump(db, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db = load_db()
    user_id_str = str(user.id)
    
    if user_id_str not in db:
        db[user_id_str] = {
            "username": user.username,
            "chips": 1000
        }
        save_db(db)
        await update.message.reply_text(
            "🎲 Добро пожаловать в Poker Club!\n"
            "💰 Ваш стартовый баланс: 1000 фишек\n\n"
            "🃏 Доступные команды:\n"
            "/dice - Играть в кости (ставка 50 фишек)\n"
            "/balance - Проверить баланс\n"
            "/help - Справка по командам"
        )
    else:
        balance = db[user_id_str]["chips"]
        await update.message.reply_text(f"♠️ С возвращением! Ваш баланс: {balance} фишек")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db = load_db()
    user_id_str = str(user.id)
    
    if user_id_str in db:
        balance = db[user_id_str]["chips"]
        await update.message.reply_text(f"💰 Ваш баланс: {balance} фишек")
    else:
        await update.message.reply_text("⚠️ Вы не зарегистрированы. Введите /start")

async def add_chips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != YOUR_USER_ID:
        await update.message.reply_text("⛔ Доступ запрещён!")
        return
    
    try:
        username = context.args[0].lstrip('@')
        amount = int(context.args[1])
        
        db = load_db()
        for user_id, data in db.items():
            if data["username"] == username:
                db[user_id]["chips"] += amount
                save_db(db)
                await update.message.reply_text(f"✅ Добавлено {amount} фишек игроку @{username}")
                return
        
        await update.message.reply_text("❌ Игрок не найден")
    except:
        await update.message.reply_text("ℹ️ Использование: /add_chips @username количество")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🃏 Команды покер-бота:
/start - Регистрация и стартовый баланс
/dice - Играть в кости (ставка 50 фишек)
/balance - Проверить баланс
/help - Справка по командам

👑 Админ-команды:
/add_chips @username сумма - Добавить фишки игроку
"""
    await update.message.reply_text(help_text)

async def play_dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db = load_db()
    user_id_str = str(user.id)
    
    if user_id_str not in db:
        await update.message.reply_text("⚠️ Вы не зарегистрированы. Введите /start")
        return
    
    # Ставка
    bet = 50
    if db[user_id_str]["chips"] < bet:
        await update.message.reply_text("❌ Недостаточно фишек! Минимальная ставка: 50 фишек")
        return
    
    # Вычитаем ставку
    db[user_id_str]["chips"] -= bet
    save_db(db)
    
    # Генерируем результаты
    player_dice = random.randint(1, 6)
    bot_dice = random.randint(1, 6)
    
    # Определяем победителя
    if player_dice > bot_dice:
        win_amount = bet * 2
        db[user_id_str]["chips"] += win_amount
        save_db(db)
        result = f"🎯 Вы выиграли {win_amount} фишек!"
    elif player_dice < bot_dice:
        result = "💥 Вы проиграли!"
    else:
        db[user_id_str]["chips"] += bet  # возвращаем ставку при ничье
        save_db(db)
        result = "🤝 Ничья! Ставка возвращена"
    
    # Отправляем результат
    await update.message.reply_text(
        f"🎲 Ваш кубик: {player_dice}\n"
        f"🤖 Кубик бота: {bot_dice}\n\n"
        f"{result}\n"
        f"💰 Новый баланс: {db[user_id_str]['chips']} фишек\n\n"
        "➡️ Сыграть еще: /dice"
    )

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("add_chips", add_chips))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("dice", play_dice))  # Добавили новую команду
    
    print("Покер-бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
