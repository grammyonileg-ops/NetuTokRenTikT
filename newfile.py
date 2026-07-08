import telebot
import requests
import time
import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8842792581:AAGORDlGA2bObTyYffs3T0b1lyGJuOVmPZ8"
bot = telebot.TeleBot(TOKEN)

# ТВОИ ПРОКСИ
PROXY_LIST = [
    "socks5://G7A76j:k2NxjB@217.29.53.211:10702",
    "socks5://G7A76j:k2NxjB@217.29.53.211:10701",
    "socks5://G7A76j:k2NxjB@217.29.53.211:10700",
    "socks5://G7A76j:k2NxjB@217.29.53.211:10699",
    "socks5://G7A76j:k2NxjB@217.29.53.211:10698"
]

# Доступные причины
REASONS = {
    "spam": "📩 Спам",
    "violence": "🔪 Насилие",
    "harassment": "🚫 Домогательства",
    "self_harm": "⚠️ Опасный контент",
    "illegal": "⚖️ Незаконный контент",
    "misinformation": "❌ Недостоверная инфа"
}

user_data = {}

def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🎯 Новая цель", callback_data="new_target"),
        InlineKeyboardButton("📛 Причина", callback_data="reason"),
        InlineKeyboardButton("⏱ Интервал", callback_data="interval"),
        InlineKeyboardButton("⏳ Длительность", callback_data="duration"),
        InlineKeyboardButton("🚀 Старт атаки", callback_data="start_attack"),
        InlineKeyboardButton("🛑 Стоп", callback_data="stop")
    )
    return markup

def reason_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    for key, label in REASONS.items():
        markup.add(InlineKeyboardButton(label, callback_data=f"set_reason_{key}"))
    markup.add(InlineKeyboardButton("🔙 Назад", callback_data="back"))
    return markup

@bot.message_handler(commands=['start', 'menu'])
def start(message):
    user_data[message.chat.id] = {
        "video_url": "",
        "video_id": "",
        "reason": "spam",
        "interval": 5,
        "duration": 60
    }
    bot.send_message(message.chat.id, "🔥 Бот для жалоб на видео\nНастрой параметры:", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "new_target":
        msg = bot.send_message(call.message.chat.id, "Пришли ссылку на видео TikTok")
        bot.register_next_step_handler(msg, save_video)
    elif call.data == "reason":
        bot.edit_message_text("Выбери причину жалобы:", call.message.chat.id, call.message.message_id, reply_markup=reason_menu())
    elif call.data == "interval":
        msg = bot.send_message(call.message.chat.id, "Интервал между жалобами (сек):")
        bot.register_next_step_handler(msg, save_interval)
    elif call.data == "duration":
        msg = bot.send_message(call.message.chat.id, "Длительность атаки (минуты):")
        bot.register_next_step_handler(msg, save_duration)
    elif call.data == "start_attack":
        bot.edit_message_text("🚀 Запускаю...", call.message.chat.id, call.message.message_id)
        start_attack(call.message.chat.id)
    elif call.data == "stop":
        bot.send_message(call.message.chat.id, "🛑 Остановлено")
        raise SystemExit
    elif call.data == "back":
        bot.edit_message_text("Главное меню", call.message.chat.id, call.message.message_id, reply_markup=main_menu())
    elif call.data.startswith("set_reason_"):
        reason_key = call.data.replace("set_reason_", "")
        user_data[call.message.chat.id]["reason"] = reason_key
        bot.answer_callback_query(call.id, f"Причина: {REASONS[reason_key]}")
        bot.edit_message_text(f"✅ Причина выбрана: {REASONS[reason_key]}", call.message.chat.id, call.message.message_id, reply_markup=main_menu())

def save_video(message):
    url = message.text.strip()
    try:
        video_id = url.split("/video/")[1].split("?")[0]
        user_data[message.chat.id]["video_url"] = url
        user_data[message.chat.id]["video_id"] = video_id
        bot.reply_to(message, f"✅ Видео сохранено: {url}")
    except:
        bot.reply_to(message, "❌ Неверная ссылка")

def save_interval(message):
    try:
        val = int(message.text)
        user_data[message.chat.id]["interval"] = val
        bot.reply_to(message, f"✅ Интервал: {val} сек")
    except:
        bot.reply_to(message, "❌ Введи число")

def save_duration(message):
    try:
        val = int(message.text) * 60
        user_data[message.chat.id]["duration"] = val
        bot.reply_to(message, f"✅ Длительность: {val//60} мин")
    except:
        bot.reply_to(message, "❌ Введи число")

def start_attack(chat_id):
    data = user_data.get(chat_id, {})
    video_id = data.get("video_id")
    if not video_id:
        bot.send_message(chat_id, "❌ Сначала задай видео", reply_markup=main_menu())
        return

    reason = data.get("reason", "spam")
    interval = data.get("interval", 5)
    duration = data.get("duration", 60)
    start_time = time.time()
    sent = 0
    success = 0
    failed = 0
    proxy_index = 0
    report = []

    bot.send_message(chat_id, f"⏳ Атака на видео {video_id}\nПричина: {REASONS[reason]}\nДлительность: {duration//60} мин")

    while time.time() - start_time < duration:
        proxy = PROXY_LIST[proxy_index % len(PROXY_LIST)]
        try:
            resp = requests.post(
                "https://www.tiktok.com/api/video/report/",
                data={"video_id": video_id, "reason": reason},
                proxies={"http": proxy, "https": proxy},
                timeout=5
            )
            sent += 1
            if resp.status_code == 200:
                success += 1
                status = "✅ УСПЕШНО"
            else:
                failed += 1
                status = f"⚠️ ОШИБКА {resp.status_code}"
            report.append(f"#{sent} | {status} | {proxy[:30]}")
        except Exception as e:
            sent += 1
            failed += 1
            report.append(f"#{sent} | ❌ СБОЙ | {proxy[:30]} | {str(e)[:20]}")
        proxy_index += 1
        time.sleep(interval)

        if sent % 5 == 0:
            bot.send_message(chat_id, f"📊 Промежуточный итог: Успешно {success}, Ошибок {failed} из {sent}")

    final_msg = (
        f"🏁 **Атака завершена**\n"
        f"📦 Всего отправлено: {sent}\n"
        f"✅ Успешно: {success}\n"
        f"❌ Ошибок: {failed}\n"
        f"📋 **Последние 10 результатов:**\n" + "\n".join(report[-10:])
    )
    bot.send_message(chat_id, final_msg, reply_markup=main_menu(), parse_mode="Markdown")

# === ОТКЛЮЧЕНИЕ ВЕБХУКА ===
bot.remove_webhook()

bot.polling(none_stop=True)