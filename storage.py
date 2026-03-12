import requests
import os
import json

# ================================================================
# STORAGE.PY — Lưu trữ bền vững qua Upstash Redis (miễn phí)
# Cần 2 biến môi trường trên Render:
#   UPSTASH_URL   = REST URL từ upstash.com (ví dụ: https://xxx.upstash.io)
#   UPSTASH_TOKEN = REST Token từ upstash.com
# ================================================================

UPSTASH_URL   = os.environ.get("UPSTASH_URL", "https://immortal-grizzly-69189.upstash.io")
UPSTASH_TOKEN = os.environ.get("UPSTASH_TOKEN", "gQAAAAAAAQ5FAAIncDEyMDk4YjgwZmRhNjg0YjY1OGMxNmEyMmI1NTI4YzNlMXAxNjkxODk")

def _upstash(cmd_parts):
    """Gọi Upstash REST API với lệnh Redis (dùng POST để hỗ trợ value phức tạp)"""
    if not UPSTASH_URL or not UPSTASH_TOKEN:
        print("[storage] Chưa cấu hình UPSTASH_URL hoặc UPSTASH_TOKEN!")
        return None
    resp = requests.post(
        UPSTASH_URL,
        headers={
            "Authorization": f"Bearer {UPSTASH_TOKEN}",
            "Content-Type": "application/json"
        },
        json=cmd_parts  # gửi command dạng ["SET", "key", "value"]
    )
    if resp.status_code == 200:
        return resp.json().get("result")
    print(f"[storage] Lỗi {resp.status_code}: {resp.text}")
    return None

# -------- LINKS --------

def load_links():
    raw = _upstash(["GET", "links"])
    if raw:
        return json.loads(raw)
    return []

def save_links(links):
    _upstash(["SET", "links", json.dumps(links, ensure_ascii=False)])

# -------- MABUFF --------

def load_mabuff():
    raw = _upstash(["GET", "mabuff"])
    if raw:
        return json.loads(raw)
    return "SINH2004"  # Giá trị mặc định nếu chưa ai set

def save_mabuff(code):
    _upstash(["SET", "mabuff", json.dumps(code, ensure_ascii=False)])


# -------- USERS --------

def load_users():
    raw = _upstash(["GET", "users"])
    if raw:
        return json.loads(raw)
    return []

def save_users(users_list):
    _upstash(["SET", "users", json.dumps(users_list, ensure_ascii=False)])

def register_user(chat_id):
    """Thêm user vào danh sách nếu chưa có"""
    current = load_users()
    if chat_id not in current:
        current.append(chat_id)
        save_users(current)
        print(f"[storage] Đã đăng ký user mới: {chat_id}")

# -------- PENDING STATE (cho /setlink 2 bước) --------

def set_pending(key, value, expire_seconds=300):
    """Lưu trạng thái chờ (tự xóa sau expire_seconds giây)"""
    _upstash(["SET", key, json.dumps(value), "EX", expire_seconds])

def get_pending(key):
    """Lấy trạng thái chờ"""
    raw = _upstash(["GET", key])
    if raw:
        return json.loads(raw)
    return None

def clear_pending(key):
    """Xóa trạng thái chờ"""
    _upstash(["DEL", key])
