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

    # /setlink — cập nhật links theo format:
    # /setlink
    # [0] https://link0
    # [1] https://link1
    if text.startswith("/setlink"):
        lines = text.split("\n")
        links = FAQ.load_links()
        updated = []
        for line in lines[1:]:  # bỏ dòng đầu "/setlink"
            line = line.strip()
            if not line:
                continue
            # Tìm pattern [N] url
            import re
            match = re.match(r'\[(\d+)\]\s*(https?://\S+)', line)
            if match:
                idx = int(match.group(1))
                url = match.group(2)
                while len(links) <= idx:
                    links.append("")
                links[idx] = url
                updated.append(f"  [{idx}] {url}")

        if updated:
            FAQ.save_links(links)
            send_fn(chat_id, "✅ Đã cập nhật:\n" + "\n".join(updated))
        else:
            send_fn(chat_id,
                "❌ Không tìm thấy link nào.\n\n"
                "📝 Dùng đúng format:\n"
                "/setlink\n"
                "[0] https://link0\n"
                "[1] https://link1"
            )
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

    # /mabuff <mã> — Đổi mã giảm giá
    if text.startswith("/mabuff"):
        parts = text.split(" ", 1)
        if len(parts) == 2:
            new_code = parts[1].strip()
            import storage as st
            st.save_mabuff(new_code)
            send_fn(chat_id, f"✅ Đã cập nhật mã giảm giá mới: {new_code}")
        else:
            send_fn(chat_id, "❌ Dùng: /mabuff <mã>\nVí dụ: /mabuff KHUYENMAI2024")
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
        broadcast_messages.append(f"🏷️ Mã giảm giá : {FAQ.load_mabuff()}")
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
            "/mabuff <mã>        — Đổi mã giảm giá\n"
            "/sukien             — Gửi tt1 đến tất cả user\n"
            "/xemuser            — Xem danh sách user\n"
            "/help_admin         — Xem lệnh này\n"
        )
        send_fn(chat_id, msg)
        return True

    return False  # Không phải lệnh admin
