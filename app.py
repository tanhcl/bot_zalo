from flask import Flask, request
import requests
import os
import datetime
import FAQ
import admin
import users

app = Flask(__name__)

# ================================================================
# APP.PY — Server chính, chỉ nhận webhook và điều phối
# Không cần sửa file này khi thêm lệnh mới
# ================================================================

BOT_TOKEN = os.environ.get("BOT_TOKEN")
SECRET_TOKEN = "12345678"
ADMIN_ID = os.environ.get("ADMIN_ID", "a164988332d4db8a82c5")  # Lấy ADMIN_ID từ biến môi trường Render

print("BOT_TOKEN:", BOT_TOKEN)


@app.route("/bot", methods=["POST"])
def webhook():
    # Kiểm tra secret token
    received_secret = request.headers.get("X-Bot-Api-Secret-Token")
    if received_secret != SECRET_TOKEN:
        return "sai secret token", 403

    data = request.json
    print("Received data:", data)

    # Ghi log
    with open("log.txt", "a") as f:
        f.write(f"CALLED {datetime.datetime.now()}\n")
        f.write(str(data) + "\n\n")

    if "message" in data:
        message = data["message"]
        chat_id  = message["chat"]["id"]
        user_id  = message["from"]["id"]
        text     = message.get("text", "").strip()

        print("Chat ID:", chat_id)
        print("User ID:", user_id)

        # Tự động lưu chat_id vào danh sách user
        users.register_user(chat_id)

        # /myid — ai nhắn cũng được, trả về ID của chính họ
        if text == "/myid":
            send_message(chat_id, f"🪪 ID Zalo của bạn là:\n{user_id}")
            return "OK", 200

        # Điều phối: admin hay user thường?
        if user_id == ADMIN_ID:
            handled = admin.handle_admin(text, user_id, chat_id, send_message)
            if handled:
                return "OK", 200

        # Xử lý tin nhắn user thường
        for msg in FAQ.handle_message(text):
            send_message(chat_id, msg)

    return "OK", 200


def send_message(chat_id, text):
    url = f"https://bot-api.zaloplatforms.com/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    response = requests.post(url, json=payload)
    print("=== SEND MESSAGE ===")
    print("Payload:", payload)
    print("Response:", response.text)
    print("====================")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
