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
    """Gọi Upstash REST API với lệnh Redis"""
    if not UPSTASH_URL or not UPSTASH_TOKEN:
        print("[storage] Chưa cấu hình UPSTASH_URL hoặc UPSTASH_TOKEN!")
        return None
    url = UPSTASH_URL + "/" + "/".join(str(p) for p in cmd_parts)
    resp = requests.get(url, headers={"Authorization": f"Bearer {UPSTASH_TOKEN}"})
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
