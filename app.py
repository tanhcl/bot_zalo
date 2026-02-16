from flask import Flask, request
import requests
import os
import datetime

app = Flask(__name__)

BOT_TOKEN = "YOUR_BOT_TOKEN"
SECRET_TOKEN = "12345678"

@app.route("/bot", methods=["POST"])
def webhook():
    # Verify secret token
    received_secret = request.headers.get("X-Bot-Api-Secret-Token")
    if received_secret != SECRET_TOKEN:
        return "Unauthorized", 403

    data = request.json

    # Log
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
    requests.post(url, json=payload)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
