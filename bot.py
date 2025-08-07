from flask import Flask, request
import requests
import os
import re

app = Flask(__name__)

# Токен бота Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN", "8273457113:AAEwKVgBULKkKA3pFkqa-dI_qZiaHryKGDw")
# Твой Telegram chat_id
CHAT_ID = int(os.getenv("CHAT_ID", "962399273"))

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Память задач (в ОЗУ)
tasks = {}

def escape_markdown_v2(text):
    return re.sub(r'([_*\[\]()~`>#+=|{}.!\\-])', r'\\\1', text)

@app.route("/", methods=["GET"])
def index():
    return "Bot is running"

@app.route("/", methods=["POST"])
def telegram_webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text.strip():
            send_task(chat_id, text.strip())

    elif "callback_query" in data:
        query = data["callback_query"]
        chat_id = query["message"]["chat"]["id"]
        message_id = query["message"]["message_id"]
        task_text = query["message"]["text"]
        callback_id = query["id"]

        if message_id in tasks and tasks[message_id] == "done":
            answer_callback(callback_id, "Уже выполнено.")
        else:
            tasks[message_id] = "done"
            updated_text = f"✅ ~{task_text}~"
            edit_message(chat_id, message_id, updated_text)
            answer_callback(callback_id, "Отмечено как выполнено ✅")

    return "OK", 200

@app.route("/new-task", methods=["POST"])
def create_task_from_shortcut():
    data = request.get_json()
    text = data.get("text", "").strip()

    if text:
        send_task(CHAT_ID, text)
        return "Task sent", 200
    return "No text provided", 400

def send_task(chat_id, task_text):
    payload = {
        "chat_id": chat_id,
        "text": task_text,
        "reply_markup": {
            "inline_keyboard": [[
                {"text": "✅ Выполнено", "callback_data": "done"}
            ]]
        }
    }
    response = requests.post(f"{API_URL}/sendMessage", json=payload)
    if response.ok:
        message_id = response.json()["result"]["message_id"]
        tasks[message_id] = "pending"

def edit_message(chat_id, message_id, new_text):
    escaped_text = escape_markdown_v2(f"✅ ~{new_text}~")
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": escaped_text,
        "parse_mode": "MarkdownV2"
    }
    requests.post(f"{API_URL}/editMessageText", json=payload)

def answer_callback(callback_id, text):
    payload = {
        "callback_query_id": callback_id,
        "text": text
    }
    requests.post(f"{API_URL}/answerCallbackQuery", json=payload)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
