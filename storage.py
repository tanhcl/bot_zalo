import requests
import os
import json

# ================================================================
# STORAGE.PY — Lưu trữ bền vững qua Upstash Redis (miễn phí)
# Cần 2 biến môi trường trên Render:
#   UPSTASH_URL   = REST URL từ upstash.com (ví dụ: https://xxx.upstash.io)
#   UPSTASH_TOKEN = REST Token từ upstash.com
# ================================================================

UPSTASH_URL = os.environ.get("UPSTASH_URL", "").strip()
UPSTASH_TOKEN = os.environ.get("UPSTASH_TOKEN", "").strip()
_memory = {}

def _upstash(cmd_parts):
    """Gọi Upstash REST API với lệnh Redis (dùng POST để hỗ trợ value phức tạp)"""
    if not UPSTASH_URL or not UPSTASH_TOKEN:
        command = cmd_parts[0].upper()
        key = cmd_parts[1] if len(cmd_parts) > 1 else ""
        if command == "GET":
            return _memory.get(key)
        if command == "SET":
            _memory[key] = cmd_parts[2]
            return "OK"
        if command == "DEL":
            _memory.pop(key, None)
            return 1
        return None
    try:
        resp = requests.post(
            UPSTASH_URL,
            headers={"Authorization": f"Bearer {UPSTASH_TOKEN}", "Content-Type": "application/json"},
            json=cmd_parts,
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json().get("result")
        print(f"[storage] Lỗi {resp.status_code}: {resp.text[:300]}")
    except requests.RequestException as exc:
        print(f"[storage] Không kết nối được Upstash: {exc}")
    return None

# -------- LINKS --------

def load_links():
    raw = _upstash(["GET", "links"])
    if raw:
        return json.loads(raw)
    return []

def save_links(links):
    _upstash(["SET", "links", json.dumps(links, ensure_ascii=False)])


def load_products():
    raw = _upstash(["GET", "products"])
    if raw:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}
    return {}


def save_products(products):
    _upstash(["SET", "products", json.dumps(products, ensure_ascii=False)])


def load_marketing():
    raw = _upstash(["GET", "marketing"])
    if raw:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return []
    return []


def save_marketing(campaigns):
    _upstash(["SET", "marketing", json.dumps(campaigns, ensure_ascii=False)])

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
        print(f"[storage] Registered new user: {chat_id}")

# -------- PENDING STATE (cho /setlink 2 bước) --------

def set_pending(key, value, expire_seconds=300):
    """Lưu trạng thái chờ (tự xóa sau expire_seconds giây)"""
    if not UPSTASH_URL or not UPSTASH_TOKEN:
        _memory[key] = json.dumps(value, ensure_ascii=False)
    else:
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
