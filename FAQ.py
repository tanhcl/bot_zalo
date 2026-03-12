import storage

# ================================================================
# FAQ.PY — Xử lý tin nhắn của user thường
# Thêm FAQ mới: bổ sung vào FAQ_STATIC bên dưới
# Links sản phẩm (tt1) được lưu bền vững qua JSONBin (storage.py)
# ================================================================

# Các hàm load/save links — dùng storage để lưu bền vững
def load_links():
    return storage.load_links()

def save_links(links):
    storage.save_links(links)

def load_mabuff():
    return storage.load_mabuff()

FAQ_STATIC = {
    "hi": ["tôi đây !"],
    "sos": [
        "1️⃣ Bước 1: vào link sản phẩm đã cung cấp ở trên để đặt hàng.",
        "2️⃣ Bước 2: chỉ địa chỉ nhận hàng về , hà nội , hai bà trưng ,vinh tuy , trường đh kinh công, lưu ý nếu ship gọi thì gừi số ship cho tan để xử lý ",
        "3️⃣ Bước 3: nhập mã giảm giá shop đã cung cấp khi chọn shop đặt",
        "4️⃣ Bước 4: chụp ảnh dơn đã gửi cho tan để thanh toán khi dơn thanh công",
        "lưu ý lên dùng 3g khi đặt hàng"
    ],
}

def handle_message(text):
    text_lower = text.lower().strip()

    # Xử lý tt1: lấy links động từ storage (JSONBin)
    if "tt1" in text_lower:
        links = load_links()
        messages = []
        for i, link in enumerate(links):
            if link:
                messages.append(f"link sp {i} : {link}")
        messages.append(f"mã giảm giá cần áp : {load_mabuff()}")
        messages.append("nhắn tin ,sos, để hiển thị hướng dẫn đặt")
        return messages if messages else ["Chưa có link sản phẩm nào."]

    # Các FAQ tĩnh
    for key, replies in FAQ_STATIC.items():
        if key in text_lower:
            return replies

    return ["🤖 Mình chưa hiểu câu hỏi. Nhắn 'tt1' để xem link sản phẩm."]
