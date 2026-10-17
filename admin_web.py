"""Trang quản trị riêng cho shop Tân Minh."""
import os
from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

import storage

admin_web = Blueprint("admin_web", __name__, url_prefix="/admin")


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
    return render_template("admin_login.html")


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
    return render_template("admin_dashboard.html", products=list(products.values()), campaigns=campaigns, stats=stats)
