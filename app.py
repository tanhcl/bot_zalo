from flask import Flask, request
import requests
import os
import datetime

app = Flask(__name__)

# LẤY TOKEN TỪ RENDER ENVIRONMENT
BOT_TOKEN = os.environ.get("BOT_TOKEN")
SECRET_TOKEN = "12345678"

print("BOT_TOKEN:", BOT_TOKEN)


@app.route("/bot", methods=["POST"])
def webhook():
    # Kiểm tra secret token
    received_secret = request.headers.get("X-Bot-Api-Secret-Token")
    if received_secret != SECRET_TOKEN:
        return "Unauthorized", 403

    data = request.json

    # Log debug
    print("Received data:", data)

    # Ghi log file (Render vẫn cho ghi file tạm)
    with open("log.txt", "a") as f:
        f.write(f"CALLED {datetime.datetime.now()}\n")
        f.write(str(data) + "\n\n")

    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]

        reply = f"Bạn vừa nói: {text}"

        send_message(chat_id, reply)

    return "OK", 200


def send_message(chat_id, text):
    url = f"https://bot-api.zaloplatforms.com/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }

    response = requests.post(url, json=payload)

    print("=== SEND MESSAGE DEBUG ===")
    print("URL:", url)
    print("Payload:", payload)
    print("Response:", response.text)
    print("==========================")



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
