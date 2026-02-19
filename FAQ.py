FAQ = {
    "tt1": ["👋 Xin chào!", "Tôi là trợ lý ảo của shop!", "Bạn có thể hỏi tôi về địa chỉ, giờ mở cửa, giao hàng và menu sản phẩm."],
    "địa chỉ": "🏠 Shop ở 123 Nguyễn Văn A, TP.HCM",
    "giờ mở cửa": "⏰ Shop mở cửa 8h - 22h mỗi ngày",
    "ship": "🚚 Shop có giao hàng toàn quốc",
    "menu": "📋 Menu:\n1️⃣ Sản phẩm A\n2️⃣ Sản phẩm B"
}
# Hàm xử lý tin nhắn
def handle_message(text):
    text = text.lower()

    for keyword, messages in FAQ.items():
        if keyword in text:
            return messages   # trả về nhiều tin nhắn

    return ["🤖 Mình chưa hiểu câu hỏi."]
