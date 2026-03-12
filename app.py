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

        # --- Xử lý trường hợp Zalo preview URL làm thay đổi cấu trúc ---
        # Zalo đôi khi tách URL ra khỏi text, thử ghép lại từ các field phụ
        if text and not text.startswith("/"):
            pass  # text thường, không cần xử lý thêm
        elif text.startswith("/setlink"):
            # Kiểm tra xem URL có trong entities không
            entities = message.get("entities", [])
            for entity in entities:
                href = entity.get("href", "") or entity.get("url", "")
                if href and href not in text:
                    text = text + " " + href
                    break
            # Kiểm tra attachment
            attachment = message.get("attachment", {})
            if attachment:
                href = attachment.get("payload", {}).get("url", "")
                if href and href not in text:
                    text = text + " " + href

        print("Chat ID:", chat_id)
        print("User ID:", user_id)
        print("Text cuối cùng:", text)
        print("Full message:", message)  # Log để debug Zalo format

        # Tự động lưu chat_id vào danh sách user
        users.register_user(chat_id)

        # /myid — ai nhắn cũng được, trả về ID của chính họ
        if text == "/myid":
            send_message(chat_id, f"🪪 ID Zalo của bạn là:\n{user_id}")
            return "OK", 200

        # Điều phối: admin hay user thường?
        if user_id == ADMIN_ID:
            # Bước 2 của /setlink: khi admin gửi URL (text là URL hoặc text rỗng do Zalo tách)
            import storage as st
            pending = st.get_pending(f"pending_setlink_{user_id}")
            if pending:
                # Lấy URL từ text (nếu có) hoặc từ attachment của Zalo
                url_to_save = text.strip() if text.strip() else None
                # Thử lấy từ attachment nếu text rỗng
                if not url_to_save:
                    for field in ["href", "url", "link"]:
                        url_to_save = message.get(field, "")
                        if url_to_save:
                            break
                if url_to_save and (url_to_save.startswith("http") or url_to_save.startswith("www")):
                    idx = pending["index"]
                    links = FAQ.load_links()
                    while len(links) <= idx:
                        links.append("")
                    links[idx] = url_to_save
                    FAQ.save_links(links)
                    st.clear_pending(f"pending_setlink_{user_id}")
                    send_message(chat_id, f"✅ Đã lưu link sp {idx}:\n{url_to_save}")
                    return "OK", 200
                elif text and not text.startswith("/"):
                    # Text không phải URL cũng không phải lệnh → hỏi lại
                    send_message(chat_id, f"❌ Đây không phải URL. Vui lòng gửi URL bắt đầu bằng http://\nHoặc nhắn /huy để hủy.")
                    return "OK", 200

            handled = admin.handle_admin(text, user_id, chat_id, send_message, raw_message=message)
            if handled:
                return "OK", 200
            # Text rỗng (Zalo link preview event) hoặc không match lệnh → bỏ qua
            if not text:
                return "OK", 200
            # Có text nhưng không phải lệnh → debug cho admin
            send_message(chat_id, f"⚙️ [Admin Debug]\nText nhận được:\n[{text}]")
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
