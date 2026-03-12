import FAQ
import users

# ================================================================
# ADMIN.PY — Xử lý lệnh dành riêng cho admin
# Thêm lệnh mới cho admin: chỉ cần thêm điều kiện vào handle_admin()
# ================================================================

def handle_admin(text, user_id, chat_id, send_fn, raw_message=None):
    """
    Xử lý lệnh admin. Trả về True nếu đã xử lý, False nếu không phải lệnh admin.
    send_fn: hàm gửi tin nhắn (nhận chat_id, text)
    """

    # /debug — xem bot đang nhận được text gì (để diagnose lỗi)
    if text.startswith("/debug"):
        send_fn(chat_id, f"🔍 Bot nhận text:\n[{text}]\n\nRaw message:\n{str(raw_message)[:500]}")
        return True

    # /setlink <index> <url> — cập nhật link sản phẩm theo vị trí
    if text.startswith("/setlink"):
        parts = text.split(" ", 2)
        if len(parts) == 3:
            try:
                idx = int(parts[1])
                new_url = parts[2].strip()
                links = FAQ.load_links()
                while len(links) <= idx:
                    links.append("")
                links[idx] = new_url
                FAQ.save_links(links)
                send_fn(chat_id, f"✅ Đã cập nhật link sp {idx}:\n{new_url}")
            except ValueError:
                send_fn(chat_id, "❌ Sai định dạng. Dùng: /setlink <số> <url>")
        else:
            send_fn(chat_id, "❌ Dùng: /setlink <số> <url>\nVí dụ: /setlink 0 https://tiktok.com/...")
        return True

    # /xemlink — xem toàn bộ links hiện tại
    if text == "/xemlink":
        links = FAQ.load_links()
        if not links:
            send_fn(chat_id, "Chưa có link nào.")
        else:
            msg = "📋 Danh sách link hiện tại:\n"
            for i, link in enumerate(links):
                msg += f"  [{i}] {link if link else '(trống)'}\n"
            send_fn(chat_id, msg)
        return True

    # /xoalink <index> — xóa link theo vị trí
    if text.startswith("/xoalink"):
        parts = text.split(" ", 1)
        if len(parts) == 2:
            try:
                idx = int(parts[1])
                links = FAQ.load_links()
                if 0 <= idx < len(links):
                    links[idx] = ""
                    FAQ.save_links(links)
                    send_fn(chat_id, f"🗑️ Đã xóa link sp {idx}.")
                else:
                    send_fn(chat_id, f"❌ Không tìm thấy link số {idx}.")
            except ValueError:
                send_fn(chat_id, "❌ Dùng: /xoalink <số>")
        else:
            send_fn(chat_id, "❌ Dùng: /xoalink <số>\nVí dụ: /xoalink 2")
        return True

    # /sukien — broadcast links sản phẩm thật đến tất cả user
    if text == "/sukien":
        all_users = users.load_users()
        if not all_users:
            send_fn(chat_id, "❌ Chưa có user nào trong danh sách.")
            return True

        # Lấy links thật từ links.json và build nội dung gửi đi
        links = FAQ.load_links()
        broadcast_messages = []
        for i, link in enumerate(links):
            if link:
                broadcast_messages.append(f"🔥 link sp {i} : {link}")
        broadcast_messages.append("🏷️ Mã giảm giá : SINH2004")
        broadcast_messages.append("📌 Nhắn 'sos' để xem hướng dẫn đặt hàng")

        if not broadcast_messages:
            send_fn(chat_id, "❌ Chưa có link sản phẩm nào để gửi.")
            return True

        ok_count = 0
        for uid in all_users:
            for msg in broadcast_messages:
                send_fn(uid, msg)
            ok_count += 1

        send_fn(chat_id, f"📢 Đã gửi link sản phẩm đến {ok_count} user!")
        return True

    # /xemuser — xem số lượng user trong danh sách
    if text == "/xemuser":
        all_users = users.load_users()
        send_fn(chat_id, f"👥 Hiện có {len(all_users)} user đã từng nhắn bot:\n" +
                         "\n".join(f"  - {u}" for u in all_users) if all_users else "Chưa có user nào.")
        return True

    # /help_admin — xem danh sách lệnh admin
    if text == "/help_admin":
        msg = (
            "🔑 Lệnh dành cho Admin:\n\n"
            "/setlink <số> <url> — Cập nhật link sp\n"
            "/xoalink <số>       — Xóa link sp\n"
            "/xemlink            — Xem tất cả link\n"
            "/sukien             — Gửi tt1 đến tất cả user\n"
            "/xemuser            — Xem danh sách user\n"
            "/help_admin         — Xem lệnh này\n"
        )
        send_fn(chat_id, msg)
        return True

    return False  # Không phải lệnh admin
