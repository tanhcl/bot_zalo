"""Trang quản trị riêng cho shop Tân Minh."""
import os
from functools import wraps

from flask import Blueprint, flash, redirect, render_template_string, request, session, url_for

import storage

admin_web = Blueprint("admin_web", __name__, url_prefix="/admin")

LOGIN_HTML = """<!doctype html><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Admin Tân Minh</title><style>body{font-family:system-ui;background:#f3f6fb;display:grid;place-items:center;min-height:100vh}.card{background:white;padding:32px;border-radius:18px;width:min(90%,380px);box-shadow:0 12px 35px #183b6730}input,button{width:100%;padding:12px;box-sizing:border-box;margin-top:10px;border-radius:9px;border:1px solid #d7deea}button{background:#1463ff;color:white;border:0;cursor:pointer}.err{color:#b42318}</style><main class='card'><h1>Quản trị Tân Minh</h1><p>Quản lý sản phẩm, marketing và sale.</p>{% for m in get_flashed_messages(category_filter=['error']) %}<p class='err'>{{m}}</p>{% endfor %}<form method='post'><input name='password' type='password' placeholder='Mật khẩu admin' required autofocus><button>Đăng nhập</button></form></main>"""

DASHBOARD_HTML = """<!doctype html><html lang='vi'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Admin · Tân Minh</title><style>:root{font-family:system-ui;color:#172033;background:#f5f7fb}body{margin:0}.top{background:#102a43;color:white;padding:18px 5%;display:flex;justify-content:space-between}.wrap{max-width:1200px;margin:28px auto;padding:0 18px}.stats,.grid{display:grid;gap:14px}.stats{grid-template-columns:repeat(4,1fr)}.grid{grid-template-columns:1.3fr .9fr;margin-top:18px}.stat,.panel{background:white;border-radius:14px;padding:18px;box-shadow:0 5px 20px #1a365d12}.stat b{display:block;font-size:26px;color:#1463ff}input,textarea,select{width:100%;box-sizing:border-box;padding:10px;margin:5px 0 10px;border:1px solid #d7deea;border-radius:8px}textarea{min-height:70px}button{border:0;border-radius:8px;padding:10px 14px;cursor:pointer;background:#1463ff;color:white}.danger{background:#d92d20}.muted{color:#667085;font-size:13px}.product{border-top:1px solid #edf0f5;padding:12px 0;display:flex;justify-content:space-between;gap:10px}.badge{font-size:12px;padding:3px 7px;border-radius:12px;background:#e8f1ff;color:#1456b8}@media(max-width:800px){.stats,.grid{grid-template-columns:1fr}}</style><header class='top'><b>Tân Minh · Admin</b><form method='post' action='{{url_for("admin_web.logout")}}'><button>Đăng xuất</button></form></header><main class='wrap'>{% for c,m in get_flashed_messages(with_categories=true) %}<p class='badge'>{{m}}</p>{% endfor %}<section class='stats'><div class='stat'>Sản phẩm đang bán<b>{{stats.products}}</b></div><div class='stat'>Người đã nhắn bot<b>{{stats.users}}</b></div><div class='stat'>Chiến dịch<b>{{stats.campaigns}}</b></div><div class='stat'>Mã giảm giá<b>{{stats.discount}}</b></div></section><section class='grid'><div class='panel'><h2>Quản lý sản phẩm</h2><p class='muted'>Dùng mã trùng để cập nhật sản phẩm.</p><form method='post'><input type='hidden' name='action' value='save_product'><input name='code' placeholder='Mã TM01' required><input name='name' placeholder='Tên sản phẩm' required><input name='price' placeholder='Giá hiển thị'><input name='stock' placeholder='Tồn kho'><textarea name='description' placeholder='Mô tả'></textarea><input name='link' type='url' placeholder='Link đặt hàng'><label><input name='active' type='checkbox' checked style='width:auto'> Đang bán</label><br><button>Lưu sản phẩm</button></form><h3>Danh mục</h3>{% for p in products %}<article class='product'><div><b>{{p.code}} · {{p.name}}</b><br><span class='muted'>{{p.price or 'Liên hệ'}} · {{p.stock or 'Chưa cập nhật tồn kho'}}</span><br><span class='badge'>{{'Đang bán' if p.active else 'Đang ẩn'}}</span></div><form method='post'><input type='hidden' name='action' value='delete_product'><input type='hidden' name='code' value='{{p.code}}'><button class='danger'>Xóa</button></form></article>{% else %}<p class='muted'>Chưa có sản phẩm.</p>{% endfor %}</div><div class='panel'><h2>Marketing & Sale</h2><form method='post'><input type='hidden' name='action' value='save_campaign'><input name='title' placeholder='Tên chiến dịch' required><textarea name='content' placeholder='Nội dung quảng bá'></textarea><input name='discount' placeholder='Mã ưu đãi'><select name='status'><option value='draft'>Bản nháp</option><option value='active'>Đang chạy</option><option value='done'>Đã kết thúc</option></select><button>Lưu chiến dịch</button></form><h3>Chiến dịch đã lưu</h3>{% for c in campaigns %}<article class='product'><div><b>{{c.title}}</b><br><span class='muted'>{{c.content}}</span><br><span class='badge'>{{c.status}}{% if c.discount %} · {{c.discount}}{% endif %}</span></div></article>{% else %}<p class='muted'>Chưa có chiến dịch.</p>{% endfor %}</div></section></main></html>"""


def _password():
    return os.environ.get("ADMIN_WEB_PASSWORD", "").strip()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_web.login"))
        return view(*args, **kwargs)
    return wrapped


@admin_web.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if not _password():
            flash("Chưa cấu hình ADMIN_WEB_PASSWORD trên Render.", "error")
        elif request.form.get("password", "") == _password():
            session["admin_logged_in"] = True
            return redirect(url_for("admin_web.dashboard"))
        else:
            flash("Mật khẩu không đúng.", "error")
    return render_template_string(LOGIN_HTML)


@admin_web.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("admin_web.login"))


@admin_web.route("/", methods=["GET", "POST"])
@login_required
def dashboard():
    products = storage.load_products()
    if request.method == "POST":
        action = request.form.get("action")
        code = request.form.get("code", "").strip().upper()
        if action == "save_product" and code:
            products[code] = {
                "code": code,
                "name": request.form.get("name", "").strip(),
                "price": request.form.get("price", "").strip(),
                "stock": request.form.get("stock", "").strip(),
                "description": request.form.get("description", "").strip(),
                "link": request.form.get("link", "").strip(),
                "active": request.form.get("active") == "on",
            }
            storage.save_products(products)
            flash(f"Đã lưu sản phẩm {code}.", "success")
        elif action == "delete_product" and code in products:
            products.pop(code)
            storage.save_products(products)
            flash(f"Đã xóa sản phẩm {code}.", "success")
        elif action == "save_campaign":
            campaigns = storage.load_marketing()
            campaigns.insert(0, {
                "title": request.form.get("title", "").strip(),
                "content": request.form.get("content", "").strip(),
                "discount": request.form.get("discount", "").strip(),
                "status": request.form.get("status", "draft"),
            })
            storage.save_marketing(campaigns[:50])
            flash("Đã lưu chiến dịch marketing.", "success")
        return redirect(url_for("admin_web.dashboard"))

    users = storage.load_users()
    campaigns = storage.load_marketing()
    active_products = [p for p in products.values() if p.get("active", True)]
    stats = {
        "products": len(active_products),
        "users": len(users),
        "campaigns": len(campaigns),
        "discount": storage.load_mabuff(),
    }
    return render_template_string(DASHBOARD_HTML, products=list(products.values()), campaigns=campaigns, stats=stats)
