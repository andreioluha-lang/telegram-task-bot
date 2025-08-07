from flask import Flask, request
import requests

BOT_TOKEN = '8273457113:AAEwKVgBULKkKA3pFkqa-dI_qZiaHryKGDw'
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    data = request.json

    if "callback_query" in data:
        query = data["callback_query"]
        chat_id = query["message"]["chat"]["id"]
        message_id = query["message"]["message_id"]
        original_text = query["message"]["text"]

        updated_text = original_text.replace("📝 Задача:", "✅ Задача выполнена:").replace("\n", "\n~") + "~"

        requests.post(f"{API_URL}/editMessageText", json={
            "chat_id": chat_id,
            "message_id": message_id,
            "text": updated_text,
            "parse_mode": "Markdown"
        })

        requests.post(f"{API_URL}/editMessageReplyMarkup", json={
            "chat_id": chat_id,
            "message_id": message_id,
            "reply_markup": {"inline_keyboard": []}
        })

        return "ok", 200

    elif "message" in data:
        msg = data["message"]
        text = msg.get("text", "").strip()
        chat_id = msg["chat"]["id"]

        task_text = f"📝 Задача:\n{text}"

        requests.post(f"{API_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": task_text,
            "reply_markup": {
                "inline_keyboard": [
                    [{"text": "✅ Выполнено", "callback_data": "done"}]
                ]
            }
        })

        return "ok", 200

    return "ignored", 200
