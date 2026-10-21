"""Bộ tư vấn bán hàng cho Bot Tân Minh."""
import re
import unicodedata
import storage


def load_links(): return storage.load_links()
def save_links(links): storage.save_links(links)
def load_mabuff(): return storage.load_mabuff()
def load_products(): return storage.load_products()


def _key(text):
    text = unicodedata.normalize("NFD", (text or "").lower().strip())
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


def _context(chat_id):
    return storage.load_conversations().get(str(chat_id), {}) if chat_id else {}


def _save_context(chat_id, **values):
    if not chat_id: return
    contexts = storage.load_conversations()
    current = contexts.get(str(chat_id), {})
    current.update(values)
    contexts[str(chat_id)] = current
    storage.save_conversations(contexts)


def _active_products():
    return [p for p in load_products().values() if p.get("active", True)]


def product_messages(products=None, chat_id=None):
    active = products if products is not None else _active_products()
    if not active:
        return ["Hiện shop chưa cập nhật sản phẩm mới. Bạn cho mình biết loại sản phẩm đang cần để mình kiểm tra và hỗ trợ nhé."]
    codes = [p.get("code", "").upper() for p in active]
    _save_context(chat_id, last_products=codes)
    lines = ["Dạ, đây là các sản phẩm Tân Minh đang có ạ:"]
    for p in active[:12]:
        lines.append(f"• {p.get('code')} · {p.get('name')} — {p.get('price') or 'Liên hệ'}")
    lines.append("Bạn nhắn mã sản phẩm để mình tư vấn chi tiết và gửi link đặt hàng nhé.")
    return ["\n".join(lines)]


def product_detail(code, products=None, chat_id=None):
    products = products or load_products()
    product = products.get(code.upper())
    if not product or not product.get("active", True):
        return [f"Chưa tìm thấy sản phẩm {code.upper()} trong danh mục đang bán ạ. Bạn nhắn 'sanpham' để xem mã hiện có nhé."]
    _save_context(chat_id, last_product=product.get("code"))
    return [f"Dạ, sản phẩm {product['name']} ({product['code']}) hiện có giá {product.get('price') or 'liên hệ'} ạ.", product.get("description") or "Shop sẽ tư vấn thêm theo nhu cầu của bạn ạ.", f"Đặt hàng tại: {product.get('link') or 'Bạn gửi khu vực nhận hàng, mình hỗ trợ chốt đơn.'}", "Anh/chị cần tư vấn thêm về mẫu, giá hay cách đặt hàng ạ?"]


def _find_product(text, products):
    key = _key(text)
    match = re.search(r"\b([a-z]{1,5}\d{1,5})\b", key)
    if match and match.group(1).upper() in products:
        return products[match.group(1).upper()]
    for product in products.values():
        name = _key(product.get("name", ""))
        if name and (name in key or any(w in key for w in name.split() if len(w) > 3)):
            return product
    return None


def _sale_guide():
    return ["Mình hỗ trợ anh/chị đặt hàng theo 3 bước ạ:", "1. Chọn sản phẩm và gửi mã sản phẩm.", "2. Gửi khu vực nhận hàng để shop kiểm tra phí giao.", "3. Shop gửi link đặt hàng và hướng dẫn áp mã ưu đãi.", "Anh/chị đang quan tâm sản phẩm nào để mình hỗ trợ ngay ạ?"]


def handle_message(text, chat_id=None):
    raw = (text or "").strip()
    key = _key(raw)
    products = load_products()
    active = {k: v for k, v in products.items() if v.get("active", True)}
    context = _context(chat_id)
    if key in {"menu", "hi", "hello", "xin chao", "chao", "alo", "em oi"}:
        return ["Dạ em chào anh/chị 👋 Em là nhân viên tư vấn của Tân Minh.\n\nEm có thể hỗ trợ xem sản phẩm, giá, ưu đãi và hướng dẫn đặt hàng.\n\nAnh/chị đang muốn mua sản phẩm nào ạ? Nhắn 'sanpham' để xem danh mục nhé."]
    if any(x in key for x in ["cam on", "thanks", "thank you"]):
        return ["Dạ em rất vui được hỗ trợ anh/chị ạ 😊 Khi cần xem thêm sản phẩm hoặc đặt hàng, anh/chị cứ nhắn em nhé."]
    if key in {"sanpham", "san pham", "danh muc", "danh muc san pham", "xem hang"}:
        return product_messages(list(active.values()), chat_id)
    if key.startswith("sp ") or key.startswith("ma "):
        return product_detail(raw.split(maxsplit=1)[1].strip(), products, chat_id)
    product = _find_product(raw, active)
    if product and any(x in key for x in ["gia", "bao nhieu", "mua", "dat", "con hang", "tu van", "thich"]):
        return product_detail(product.get("code", ""), products, chat_id)
    if key in {"uudai", "uu dai", "khuyen mai", "ma giam gia", "voucher", "sale"} or "giam gia" in key:
        campaigns = [c for c in storage.load_marketing() if c.get("status") == "active"]
        extra = "\n".join(f"• {c.get('title')}: {c.get('content')}" for c in campaigns[:3])
        return [f"Dạ, mã ưu đãi hiện tại của Tân Minh là: {load_mabuff()}." + (f"\n\n{extra}" if extra else "") + "\nAnh/chị muốn áp mã cho sản phẩm nào ạ?"]
    if any(x in key for x in ["ship", "giao hang", "phi van chuyen", "dia chi", "khu vuc"]):
        return ["Dạ anh/chị gửi giúp em tỉnh/thành hoặc khu vực nhận hàng nhé. Em sẽ kiểm tra hướng giao phù hợp cho mình ạ."]
    if any(x in key for x in ["dat hang", "mua hang", "thanh toan", "chot don", "order"]):
        return _sale_guide()
    if key in {"hotro", "ho tro", "tu van", "tu van vien", "gap nguoi"}:
        return ["Dạ em đây ạ. Anh/chị gửi tên/mã sản phẩm, số lượng và khu vực nhận hàng; em tư vấn và hỗ trợ chốt đơn ngay nhé."]
    if "tt1" in key:
        links = [f"Link sản phẩm {i}: {link}" for i, link in enumerate(load_links()) if link]
        return (links or ["Shop đang cập nhật link đặt hàng ạ."]) + [f"Mã ưu đãi: {load_mabuff()}", "Anh/chị gửi mã sản phẩm để em hỗ trợ tiếp nhé."]
    if raw.isdigit() and context.get("last_products"):
        index = int(raw) - 1
        codes = context["last_products"]
        if 0 <= index < len(codes):
            return product_detail(codes[index], products, chat_id)
    return ["Dạ để tư vấn đúng hơn, anh/chị cho em biết sản phẩm, mức giá hoặc nhu cầu sử dụng nhé. Anh/chị có thể nhắn 'sanpham' để xem danh mục hoặc 'tt1' để xem link đặt hàng ạ."]
