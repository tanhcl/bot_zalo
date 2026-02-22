FAQ = {
    "tt1": ["link sp 1: https://vt.tiktok.com/ZSmurHves/ ","link sp 2 : https://vt.tiktok.com/ZS9eBByfnjjwQ-iZi2i/","link sp 3: https://vt.tiktok.com/ZS9eBBXJNT37m-v2e0l/", "mã giả cần áp :", "SINH2004","nhắn tin ,sos, để hiển thi hướng đẫn đặt"],
    "hi": ["tôi đây !"],
    "sos": ["1️⃣ Bước 1: vào link sản phẩm đã cung cấp ở trên để đặt hàng.",
            "2️⃣ Bước 2: chỉ địa chỉ nhận hàng về , hà nội , hai bà trưng ,vinh tuy , trường đh kinh công, lưu ý nếu ship gọi thì gừi số ship cho tan để xử lý ",
            "3️⃣ Bước 3: nhập mã giảm giá shop đã cung cấp khi chọn shop đặt",
            "4️⃣ Bước 4: chụp ảnh dơn đã gửi cho tan để thanh toán khi dơn thanh công",
            "lưu ý lên dùng 3g khi đặt hàng"],
    
}
# Hàm xử lý tin nhắn
def handle_message(text):
    text = text.lower()

    for key, messages in FAQ.items():
        if key in text:
            return messages   # trả về nhiều tin nhắn

    return ["🤖 Mình chưa hiểu câu hỏi."]


