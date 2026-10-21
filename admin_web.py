"""Professional admin dashboard for Tan Minh."""
import datetime as dt
import os
import secrets
from functools import wraps
from flask import Blueprint, flash, redirect, render_template_string, request, session, url_for, jsonify
import storage

admin_web = Blueprint("admin_web", __name__, url_prefix="/admin")

LOGIN_HTML = """<!doctype html><html lang='vi'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Admin Tân Minh</title><style>*{box-sizing:border-box}body{margin:0;min-height:100vh;display:grid;place-items:center;background:#eef3f9;font-family:Inter,system-ui;color:#102a43}.login{width:min(420px,92vw);background:#fff;border:1px solid #e6edf5;border-radius:24px;padding:34px;box-shadow:0 20px 60px #102a4320}.brand{display:flex;align-items:center;gap:12px;margin-bottom:28px}.logo{width:44px;height:44px;border-radius:14px;display:grid;place-items:center;color:#fff;background:linear-gradient(135deg,#1463ff,#7c3aed);font-weight:800;font-size:20px}.eyebrow{font-size:12px;text-transform:uppercase;letter-spacing:.12em;color:#667085;font-weight:700}h1{font-size:26px;margin:10px 0 8px}p{color:#667085}label{display:block;font-size:13px;font-weight:700;margin-top:22px}input,button{width:100%;padding:13px 14px;border-radius:11px;border:1px solid #d8e0ea;margin-top:8px;font:inherit}button{border:0;background:#1463ff;color:#fff;font-weight:700;cursor:pointer}.error{background:#fff1f0;color:#b42318;border-radius:10px;padding:10px}</style><main class='login'><div class='brand'><div class='logo'>TM</div><div><div class='eyebrow'>Shop workspace</div><b>Tân Minh</b></div></div><h1>Chào mừng trở lại</h1><p>Đăng nhập để quản lý bot, sản phẩm và doanh thu.</p>{% for m in get_flashed_messages(category_filter=['error']) %}<div class='error'>{{m}}</div>{% endfor %}<form method='post'><label>Mật khẩu quản trị</label><input name='password' type='password' placeholder='Nhập mật khẩu' required autofocus><button>Vào trang quản trị</button></form></main></html>"""

DASHBOARD_HTML = r"""<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{{shop_name}} · Admin</title><style>body{margin:0;background:#f6f8fb;color:#172033;font-family:Inter,system-ui}.shell{display:flex;min-height:100vh}.side{width:240px;background:#fff;border-right:1px solid #e8edf3;padding:22px 14px;position:fixed;inset:0 auto 0 0}.main{margin-left:240px;flex:1}.brand{display:flex;gap:10px;align-items:center;padding:0 10px 24px}.logo{display:grid;place-items:center;width:38px;height:38px;border-radius:12px;background:linear-gradient(135deg,#1463ff,#7c3aed);color:#fff;font-weight:800}.nav-title{font-size:11px;color:#98a2b3;font-weight:800;text-transform:uppercase;padding:14px 10px 6px}.nav a{display:block;padding:10px;border-radius:9px;color:#667085;text-decoration:none;font-weight:600;font-size:14px}.nav a:hover,.nav a.active{background:#edf4ff;color:#1463ff}.top{height:72px;background:#fff;border-bottom:1px solid #e8edf3;display:flex;align-items:center;justify-content:space-between;padding:0 30px}.top h1{margin:0;font-size:20px}.content{padding:28px;max-width:1400px}.btn{display:inline-block;border:0;border-radius:9px;padding:10px 13px;background:#1463ff;color:#fff;text-decoration:none;font-weight:700;font-size:13px;cursor:pointer}.btn.gray{background:#eef4ff;color:#175cd3}.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:15px}.card,.panel{background:#fff;border:1px solid #e8edf3;border-radius:15px;padding:20px;box-shadow:0 5px 18px #102a4308}.card b{display:block;font-size:28px;margin-top:10px}.muted{color:#667085;font-size:13px}.grid{display:grid;grid-template-columns:1.2fr .8fr;gap:18px;margin-top:18px}.table{width:100%;border-collapse:collapse;font-size:13px}.table th,.table td{padding:12px 8px;border-bottom:1px solid #f0f2f5;text-align:left}.table th{font-size:11px;color:#98a2b3;text-transform:uppercase}.pill{display:inline-flex;padding:4px 8px;border-radius:99px;background:#eef4ff;color:#175cd3;font-size:11px;font-weight:700}.green{background:#ecfdf3;color:#027a48}.red{background:#fff1f0;color:#b42318}.input,.select,.textarea{width:100%;box-sizing:border-box;padding:10px;border:1px solid #d8e0ea;border-radius:8px;font:inherit;margin:7px 0 12px}.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.empty{padding:28px;text-align:center;color:#667085}.flash{padding:12px;border-radius:9px;background:#ecfdf3;color:#027a48;margin-bottom:15px}@media(max-width:800px){.side{display:none}.main{margin:0}.cards{grid-template-columns:1fr 1fr}.grid{grid-template-columns:1fr}.content{padding:18px}.form-grid{grid-template-columns:1fr}}</style><div class="shell"><aside class="side"><div class="brand"><div class="logo">TM</div><b>{{shop_name}}<small style="display:block;color:#667085;font-size:11px">Admin workspace</small></b></div><nav class="nav"><div class="nav-title">Tổng quan</div><a class="{{'active' if tab=='overview'}}" href="{{url_for('admin_web.dashboard',tab='overview')}}">⌂ Dashboard</a><div class="nav-title">Kinh doanh</div><a class="{{'active' if tab=='products'}}" href="{{url_for('admin_web.dashboard',tab='products')}}">▣ Sản phẩm</a><a class="{{'active' if tab=='orders'}}" href="{{url_for('admin_web.dashboard',tab='orders')}}">▤ Đơn hàng <span class="pill">{{stats.orders}}</span></a><a href="{{url_for('admin_web.people')}}">♙ Người nhắn</a><a href="{{url_for('admin_web.groups')}}">◉ Nhóm Zalo</a><div class="nav-title">Tăng trưởng</div><a class="{{'active' if tab=='marketing'}}" href="{{url_for('admin_web.dashboard',tab='marketing')}}">✦ Marketing & Sale</a><a class="{{'active' if tab=='broadcast'}}" href="{{url_for('admin_web.dashboard',tab='broadcast')}}">➤ Broadcast nháp</a><div class="nav-title">Hệ thống</div><a class="{{'active' if tab=='settings'}}" href="{{url_for('admin_web.dashboard',tab='settings')}}">⚙ Cài đặt shop</a></nav></aside><main class="main"><header class="top"><div><h1>{{page_title}}</h1><div class="muted">Quản lý vận hành và tăng trưởng cho {{shop_name}}</div></div><div><span class="pill green">● Bot đang online</span> <a class="btn gray" href="{{url_for('admin_web.groups')}}">Nhóm & người nhắn</a></div></header><section class="content">{% for category,message in get_flashed_messages(with_categories=true) %}<div class="flash">{{message}}</div>{% endfor %}{% if tab=='overview' %}<div class="cards"><div class="card"><span class="muted">Khách hàng</span><b>{{stats.users}}</b><span class="muted">Người đã nhắn bot</span></div><div class="card"><span class="muted">Sản phẩm đang bán</span><b>{{stats.products}}</b><span class="muted">{{stats.total_products}} trong kho</span></div><div class="card"><span class="muted">Chiến dịch active</span><b>{{stats.active_campaigns}}</b><span class="muted">Marketing & sale</span></div><div class="card"><span class="muted">Đơn hàng</span><b>{{stats.orders}}</b><span class="muted">Theo dõi sale</span></div></div><div class="grid"><div class="panel"><h2>Hoạt động 7 ngày</h2><div style="height:150px;display:flex;align-items:end;gap:12px">{% for value,label in chart %}<div style="height:{{value}}%;flex:1;background:#1463ff;border-radius:7px 7px 0 0;position:relative"><small style="position:absolute;top:100%;color:#667085">{{label}}</small></div>{% endfor %}</div></div><div class="panel"><h2>Truy cập nhanh</h2><p class="muted">Quản lý người nhắn và nhóm để theo dõi chăm sóc khách hàng.</p><a class="btn" href="{{url_for('admin_web.people')}}">Xem người nhắn</a> <a class="btn gray" href="{{url_for('admin_web.groups')}}">Xem nhóm</a></div></div>{% elif tab=='products' %}<div class="grid"><div class="panel"><h2>Danh mục sản phẩm</h2><table class="table"><tr><th>Mã / tên</th><th>Giá</th><th>Trạng thái</th></tr>{% for p in products %}<tr><td><b>{{p.code}}</b><br>{{p.name}}</td><td>{{p.price or 'Liên hệ'}}</td><td><span class="pill {{'green' if p.active else 'red'}}">{{'Đang bán' if p.active else 'Đang ẩn'}}</span></td></tr>{% else %}<tr><td colspan="3" class="empty">Chưa có sản phẩm.</td></tr>{% endfor %}</table></div><div class="panel"><h2>Thêm sản phẩm</h2><form method="post"><input type="hidden" name="csrf_token" value="{{csrf_token}}"><input type="hidden" name="action" value="save_product"><div class="form-grid"><div><label>Mã *</label><input class="input" name="code" required></div><div><label>Tên *</label><input class="input" name="name" required></div><div><label>Giá</label><input class="input" name="price"></div><div><label>Tồn kho</label><input class="input" name="stock"></div></div><label>Mô tả</label><textarea class="textarea" name="description"></textarea><button class="btn">Lưu sản phẩm</button></form></div></div>{% elif tab=='customers' %}<div class="panel"><h2>Khách hàng cũ</h2><p class="muted">Để xem chi tiết và lịch sử, mở <a href="{{url_for('admin_web.people')}}">Quản lý từng người nhắn</a>.</p></div>{% elif tab=='orders' %}<div class="panel"><h2>Đơn hàng & Sale</h2><p class="muted">Module sẵn sàng kết nối nguồn đơn hàng/CRM. Hiện có {{stats.orders}} đơn.</p></div>{% elif tab=='marketing' %}<div class="grid"><div class="panel"><h2>Chiến dịch</h2>{% for c in campaigns %}<p><b>{{c.title}}</b><br><span class="muted">{{c.status}} · {{c.discount}}</span></p>{% else %}<div class="empty">Chưa có chiến dịch.</div>{% endfor %}</div><div class="panel"><h2>Tạo chiến dịch</h2><form method="post"><input type="hidden" name="csrf_token" value="{{csrf_token}}"><input type="hidden" name="action" value="save_campaign"><label>Tên</label><input class="input" name="title" required><label>Nội dung</label><textarea class="textarea" name="content"></textarea><button class="btn">Lưu chiến dịch</button></form></div></div>{% elif tab=='broadcast' %}<div class="panel"><h2>Broadcast nháp</h2><p class="muted">Soạn và lưu nháp, chưa gửi tự động.</p><form method="post"><input type="hidden" name="csrf_token" value="{{csrf_token}}"><input type="hidden" name="action" value="save_broadcast"><input class="input" name="title" placeholder="Tiêu đề"><textarea class="textarea" name="content" rows="7" placeholder="Nội dung"></textarea><button class="btn">Lưu bản nháp</button></form></div>{% elif tab=='settings' %}<div class="panel"><h2>Cài đặt shop</h2><form method="post"><input type="hidden" name="csrf_token" value="{{csrf_token}}"><input type="hidden" name="action" value="save_settings"><label>Tên shop</label><input class="input" name="shop_name" value="{{shop_name}}"><label>Mô tả</label><textarea class="textarea" name="shop_description">{{shop_description}}</textarea><button class="btn">Lưu cài đặt</button></form></div>{% endif %}</section></main></div></html>"""


def _password():
    return os.environ.get("ADMIN_WEB_PASSWORD", "").strip()


def _csrf():
    session.setdefault("admin_csrf", secrets.token_urlsafe(24))
    return session["admin_csrf"]


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
        elif secrets.compare_digest(request.form.get("password", ""), _password()):
            session.clear()
            session["admin_logged_in"] = True
            session["admin_csrf"] = secrets.token_urlsafe(24)
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
    if request.method == "POST":
        if request.form.get("csrf_token") != session.get("admin_csrf"):
            flash("Phiên thao tác hết hạn, vui lòng tải lại trang.", "error")
            return redirect(url_for("admin_web.dashboard"))
        action = request.form.get("action")
        products = storage.load_products()
        if action == "save_product":
            code = request.form.get("code", "").strip().upper()
            name = request.form.get("name", "").strip()
            if not code or not name:
                flash("Mã và tên sản phẩm là bắt buộc.", "error")
            else:
                products[code] = {"code": code, "name": name, "price": request.form.get("price", "").strip(), "stock": request.form.get("stock", "").strip(), "description": request.form.get("description", "").strip(), "link": request.form.get("link", "").strip(), "active": request.form.get("active") == "on"}
                storage.save_products(products)
                flash(f"Đã lưu sản phẩm {code}.", "success")
        elif action == "delete_product":
            code = request.form.get("code", "").strip().upper()
            if code in products:
                products.pop(code)
                storage.save_products(products)
                flash(f"Đã xóa sản phẩm {code}.", "success")
        elif action == "save_campaign":
            campaigns = storage.load_marketing()
            campaigns.insert(0, {"title": request.form.get("title", "").strip(), "content": request.form.get("content", "").strip(), "discount": request.form.get("discount", "").strip(), "status": request.form.get("status", "draft"), "created_at": dt.datetime.now(dt.timezone.utc).isoformat()})
            storage.save_marketing(campaigns[:50])
            flash("Đã lưu chiến dịch marketing.", "success")
        elif action == "delete_campaign":
            campaigns = storage.load_marketing()
            try:
                campaigns.pop(int(request.form.get("campaign_index", "-1")))
                storage.save_marketing(campaigns)
                flash("Đã xóa chiến dịch.", "success")
            except (ValueError, IndexError):
                flash("Không tìm thấy chiến dịch.", "error")
        elif action == "save_discount":
            storage.save_mabuff(request.form.get("discount", "").strip())
            flash("Đã cập nhật mã giảm giá cho bot.", "success")
        elif action == "save_broadcast":
            drafts = storage.load_broadcasts()
            drafts.insert(0, {"title": request.form.get("title", "").strip(), "content": request.form.get("content", "").strip(), "status": "draft", "created_at": dt.datetime.now(dt.timezone.utc).isoformat()})
            storage.save_broadcasts(drafts[:50])
            flash("Đã lưu bản nháp broadcast, chưa gửi cho khách.", "success")
        elif action == "save_settings":
            storage.save_settings({"shop_name": request.form.get("shop_name", "").strip() or "Tân Minh", "shop_description": request.form.get("shop_description", "").strip()})
            flash("Đã lưu cài đặt shop.", "success")
        return redirect(url_for("admin_web.dashboard", tab=request.args.get("tab", "overview")))

    products = storage.load_products()
    campaigns = storage.load_marketing()
    users = storage.load_users()
    settings = storage.load_settings()
    tab = request.args.get("tab", "overview")
    active = [p for p in products.values() if p.get("active", True)]
    stats = {"products": len(active), "total_products": len(products), "users": len(users), "campaigns": len(campaigns), "active_campaigns": len([c for c in campaigns if c.get("status") == "active"]), "orders": len(storage.load_orders()), "discount": storage.load_mabuff()}
    titles = {"overview": "Tổng quan", "products": "Sản phẩm", "orders": "Đơn hàng & Sale", "customers": "Khách hàng", "marketing": "Marketing & Sale", "broadcast": "Broadcast nháp", "settings": "Cài đặt shop"}
    return render_template_string(DASHBOARD_HTML, tab=tab, page_title=titles.get(tab, "Tổng quan"), shop_name=settings.get("shop_name", "Tân Minh"), shop_description=settings.get("shop_description", ""), products=list(products.values()), campaigns=campaigns, users=users, chart=[(35, "T2"), (55, "T3"), (48, "T4"), (72, "T5"), (64, "T6"), (88, "T7"), (76, "CN")], stats=stats, csrf_token=_csrf())


@admin_web.get("/api/summary")
@login_required
def summary():
    products = storage.load_products()
    campaigns = storage.load_marketing()
    return jsonify({"products": len(products), "active_products": len([p for p in products.values() if p.get("active", True)]), "customers": len(storage.load_users()), "campaigns": len(campaigns), "orders": len(storage.load_orders())})


COMMUNITY_HTML = r"""<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{{title}} · Tân Minh Admin</title><style>body{margin:0;background:#f6f8fb;color:#172033;font-family:Inter,system-ui}.wrap{max-width:1220px;margin:auto;padding:24px}.top{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}.brand{display:flex;gap:12px;align-items:center}.logo{display:grid;place-items:center;width:42px;height:42px;border-radius:13px;background:linear-gradient(135deg,#1463ff,#7c3aed);color:#fff;font-weight:800}.links a,.btn{display:inline-block;border:0;border-radius:9px;padding:10px 13px;text-decoration:none;font-weight:700;font-size:13px}.links a{color:#175cd3;background:#edf4ff;margin-left:7px}.btn{background:#1463ff;color:#fff;cursor:pointer}.btn.danger{background:#fff1f0;color:#d92d20}.btn.gray{background:#eef2f6;color:#344054}.panel{background:#fff;border:1px solid #e8edf3;border-radius:16px;padding:20px;box-shadow:0 6px 22px #102a4308}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.table{width:100%;border-collapse:collapse;font-size:13px}.table th,.table td{padding:13px 10px;text-align:left;border-bottom:1px solid #f0f2f5;vertical-align:top}.table th{color:#98a2b3;font-size:11px;text-transform:uppercase}.pill{display:inline-flex;padding:4px 8px;border-radius:999px;background:#eef4ff;color:#175cd3;font-size:11px;font-weight:700}.green{background:#ecfdf3;color:#027a48}.red{background:#fff1f0;color:#b42318}.muted{color:#667085;font-size:12px}.input{width:100%;border:1px solid #d8e0ea;border-radius:9px;padding:10px;box-sizing:border-box}.flash{background:#ecfdf3;color:#027a48;border-radius:10px;padding:11px;margin-bottom:16px}@media(max-width:800px){.grid{grid-template-columns:1fr}.top{display:block}.links{margin-top:14px}.table{min-width:720px}.panel{overflow:auto}}</style><div class="wrap"><div class="top"><div class="brand"><div class="logo">TM</div><div><h1 style="margin:0;font-size:22px">{{title}}</h1><div class="muted">Trung tâm hội thoại · {{shop_name}}</div></div></div><div class="links"><a href="{{url_for('admin_web.dashboard')}}">← Dashboard</a><a href="{{url_for('admin_web.groups')}}">Nhóm</a><a href="{{url_for('admin_web.people')}}">Người nhắn</a></div></div>{% for category,message in get_flashed_messages(with_categories=true) %}<div class="flash">{{message}}</div>{% endfor %}{% if page=='groups' %}<div class="panel"><h2 style="margin-top:0">Quản lý nhóm Zalo <span class="pill">{{groups|length}} nhóm</span></h2><p class="muted">Theo dõi nhóm đã nhắn bot và bật/tắt bot trả lời cho từng nhóm.</p><table class="table"><tr><th>Tên nhóm</th><th>Group ID</th><th>Tin nhắn</th><th>Tin gần nhất</th><th>Trạng thái</th><th>Thao tác</th></tr>{% for g in groups %}<tr><td><b>{{g.name}}</b><br><span class="muted">{{g.chat_type}}</span></td><td>{{g.id}}</td><td>{{g.messages or 0}}</td><td>{{g.last_message_at or '—'}}</td><td><span class="pill {{'green' if g.enabled else 'red'}}">{{'Bot đang bật' if g.enabled else 'Bot đã tắt'}}</span></td><td><form method="post"><input type="hidden" name="csrf_token" value="{{csrf_token}}"><input type="hidden" name="group_id" value="{{g.id}}"><input type="hidden" name="enabled" value="{{'0' if g.enabled else '1'}}"><button class="btn {{'danger' if g.enabled else 'gray'}}">{{'Tắt bot' if g.enabled else 'Bật bot'}}</button></form></td></tr>{% else %}<tr><td colspan="6" style="text-align:center;padding:35px;color:#667085">Chưa ghi nhận nhóm nào. Khi có người nhắn trong nhóm, nhóm sẽ xuất hiện tại đây.</td></tr>{% endfor %}</table></div>{% else %}<div class="grid"><div class="panel"><h2 style="margin-top:0">Từng người nhắn <span class="pill">{{contacts|length}} người</span></h2><p class="muted">Chọn một người để xem lịch sử tin nhắn và trạng thái chăm sóc.</p><input class="input" placeholder="Tìm theo tên hoặc ID..." oninput="filterPeople(this.value)"><table class="table" id="people"><tr><th>Người nhắn</th><th>Số tin</th><th>Trạng thái</th></tr>{% for c in contacts %}<tr><td><a href="{{url_for('admin_web.people',contact_id=c.id)}}">{{c.name}}</a><br><span class="muted">{{c.id}}</span></td><td>{{c.messages or 0}}</td><td><span class="pill {{'green' if c.status=='active' else 'red'}}">{{c.status}}</span></td></tr>{% else %}<tr><td colspan="3" style="text-align:center;padding:35px;color:#667085">Chưa có dữ liệu người nhắn.</td></tr>{% endfor %}</table></div><div class="panel"><h2 style="margin-top:0">{{selected.name if selected else 'Chọn người nhắn'}}</h2>{% if selected %}<div class="muted">ID: {{selected.id}} · Tin nhắn: {{selected.messages or 0}}</div><form method="post" style="margin:16px 0"><input type="hidden" name="csrf_token" value="{{csrf_token}}"><input type="hidden" name="contact_id" value="{{selected.id}}"><label>Trạng thái chăm sóc</label><select class="input" name="status"><option value="active" {{'selected' if selected.status=='active'}}>Đang theo dõi</option><option value="vip" {{'selected' if selected.status=='vip'}}>Khách hàng VIP</option><option value="blocked" {{'selected' if selected.status=='blocked'}}>Đã chặn</option></select><button class="btn" style="margin-top:10px">Lưu trạng thái</button></form><h3>Lịch sử nhắn gần đây</h3>{% for m in messages %}<div style="border-top:1px solid #f0f2f5;padding:10px 0"><b>{{m.sender_name or m.user_id}}</b><div>{{m.text or '(không có nội dung văn bản)'}}</div><span class="muted">{{m.created_at}}</span></div>{% else %}<div class="muted">Chưa có lịch sử.</div>{% endfor %}{% else %}<div style="padding:50px 10px;text-align:center;color:#667085">Chọn một người ở danh sách bên trái để xem chi tiết.</div>{% endif %}</div></div>{% endif %}</div><script>function filterPeople(q){q=q.toLowerCase();document.querySelectorAll('#people tr').forEach((r,i)=>{if(i)r.style.display=r.innerText.toLowerCase().includes(q)?'':'none'})}</script></html>"""


@admin_web.route("/groups", methods=["GET", "POST"])
@login_required
def groups():
    if request.method == "POST" and request.form.get("csrf_token") == session.get("admin_csrf"):
        group_id = request.form.get("group_id", "")
        groups_data = storage.load_groups()
        if group_id in groups_data:
            groups_data[group_id]["enabled"] = request.form.get("enabled") == "1"
            storage.save_groups(groups_data)
            flash("Đã cập nhật trạng thái phản hồi của nhóm.", "success")
    settings = storage.load_settings()
    data = list(storage.load_groups().values())
    return render_template_string(COMMUNITY_HTML, page="groups", title="Quản lý nhóm Zalo", shop_name=settings.get("shop_name", "Tân Minh"), groups=data, contacts=[], selected=None, messages=[], csrf_token=_csrf())


@admin_web.route("/people", methods=["GET", "POST"])
@login_required
def people():
    contacts = storage.load_contacts()
    if request.method == "POST" and request.form.get("csrf_token") == session.get("admin_csrf"):
        contact_id = request.form.get("contact_id", "")
        if contact_id in contacts:
            contacts[contact_id]["status"] = request.form.get("status", "active")
            storage.save_contacts(contacts)
            flash("Đã cập nhật trạng thái người nhắn.", "success")
    selected_id = request.args.get("contact_id", "")
    selected = contacts.get(selected_id)
    messages = [m for m in storage.load_message_history() if str(m.get("user_id")) == str(selected_id)][-30:][::-1] if selected else []
    settings = storage.load_settings()
    return render_template_string(COMMUNITY_HTML, page="people", title="Quản lý từng người nhắn", shop_name=settings.get("shop_name", "Tân Minh"), groups=[], contacts=list(contacts.values()), selected=selected, messages=messages, csrf_token=_csrf())
