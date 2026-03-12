import storage

# ================================================================
# USERS.PY — Quản lý danh sách user đã từng nhắn bot
# Dùng storage.py (JSONBin) để lưu bền vững qua Render restart
# ================================================================

def load_users():
    return storage.load_users()

def save_users(users_list):
    storage.save_users(users_list)

def register_user(chat_id):
    storage.register_user(chat_id)
