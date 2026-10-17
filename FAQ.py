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


def load_products():
    return storage.load_products()

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


def product_messages(products):
    active = [p for p in products.values() if p.get("active", True)]
    if not active:
        return ["Hiện Tân Minh chưa cập nhật sản phẩm. Nhắn 'hotro' để được hỗ trợ."]
    messages = ["🛍️ Sản phẩm tại Tân Minh:"]
    for product in active:
        messages.append(f"• {product['code']} – {product['name']} – {product.get('price', 'Liên hệ')}\n  Nhắn: sp {product['code']}")
    return messages


def product_detail(code, products):
    product = products.get(code.upper())
    if not product or not product.get("active", True):
        return [f"Chưa tìm thấy sản phẩm {code.upper()}. Nhắn 'sanpham' để xem danh mục."]
    return [
        f"🛒 {product['code']} – {product['name']}",
        f"Giá: {product.get('price', 'Liên hệ')}",
        product.get("description", "Tân Minh đang cập nhật mô tả sản phẩm."),
        f"Đặt hàng: {product.get('link', 'Nhắn hotro để được hỗ trợ')}",
        "Nhắn 'sos' để xem hướng dẫn đặt hàng."
    ]

def handle_message(text):
    text_lower = text.lower().strip()

    products = load_products()
    if text_lower in {"menu", "hi", "xin chao", "hello"}:
        return ["👋 Chào mừng bạn đến Tân Minh!\n\nNhắn 'sanpham' để xem sản phẩm.\nNhắn 'uudai' để xem ưu đãi.\nNhắn 'hotro' để được tư vấn."]
    if text_lower in {"sanpham", "sản phẩm", "danh muc", "danh mục"}:
        return product_messages(products)
    if text_lower.startswith("sp "):
        return product_detail(text_lower.split(maxsplit=1)[1], products)
    if text_lower in {"uudai", "ưu đãi"}:
        return [f"🏷️ Mã ưu đãi hiện tại của Tân Minh: {load_mabuff()}\nNhắn 'sanpham' để chọn sản phẩm."]
    if text_lower in {"hotro", "hỗ trợ", "tu van", "tư vấn"}:
        return ["☎️ Tân Minh sẽ hỗ trợ bạn sớm. Vui lòng gửi tên sản phẩm và nhu cầu cần tư vấn."]

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
