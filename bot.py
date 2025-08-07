from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Получаем токен и chat_id из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN", "8273457113:AAEwKVgBULKkKA3pFkqa-dI_qZiaHryKGDw")
CHAT_ID = os.getenv("CHAT_ID", "962399273")  # Подставь свой chat_id, если не используешь переменные

# Главная страница (проверка работоспособности)
@app.route("/", methods=["GET"])
def index():
    return "Bot is running"

# Прием webhook от Telegram
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    message = data.get("message", {}).get("text", "")
    chat_id = data.get("message", {}).get("chat", {}).get("id", CHAT_ID)

    if message:
        reply = f"Принято: {message}"
        send_message(chat_id, reply)

    return "OK", 200

# Функция отправки сообщения
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")

# Запуск Flask-приложения с динамическим портом для Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
