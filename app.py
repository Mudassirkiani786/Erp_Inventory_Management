

from flask import (

    Flask, request, redirect, url_for,

    render_template_string, flash, Response

)

from database import get_db, init_db
from datetime import datetime

import sqlite3
import os
import csv
import io

app = Flask(__name__)

# Set FLASK_SECRET_KEY in the environment before deployment.
app.config["SECRET_KEY"] = os.environ.get(
    "FLASK_SECRET_KEY",
    "dev-only-change-this-secret-before-deployment"
)
app.config["DEBUG"] = os.environ.get("FLASK_DEBUG", "0").strip().lower() in {
    "1", "true", "yes", "on"
}

# --------------------------------------------------

# PROFESSIONAL DESIGN / SHARED PAGE

# --------------------------------------------------

PAGE = """

<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport" content="width=device-width, initial-scale=1">

<title>{{ page_title or 'Dashboard' }} | MuDaSiR ERP</title>

<style>

:root {

    --navy: #14243a;

    --navy-light: #203854;

    --blue: #3563e9;

    --blue-hover: #244bc4;

    --bg: #f4f7fb;

    --white: #ffffff;

    --text: #202b3c;

    --muted: #718096;

    --border: #e4eaf2;

    --green: #16845b;

    --red: #c83d4d;

    --orange: #b66b11;

    --shadow: 0 5px 22px rgba(30, 50, 80, .06);

}

* { box-sizing: border-box; }

body {

    margin: 0;

    font-family: Inter, "Segoe UI", Arial, sans-serif;

    background: var(--bg);

    color: var(--text);

    font-size: 14px;

}

.layout { min-height: 100vh; }

.sidebar {

    width: 245px;

    background: var(--navy);

    color: white;

    position: fixed;

    inset: 0 auto 0 0;

    padding: 25px 15px;

    overflow-y: auto;

}

.brand {

    display: flex;

    align-items: center;

    gap: 12px;

    padding: 0 10px 27px;

    border-bottom: 1px solid rgba(255,255,255,.12);

}

.brand-icon {

    width: 42px;

    height: 42px;

    border-radius: 12px;

    display: grid;

    place-items: center;

    background: var(--blue);

    font-size: 22px;

    font-weight: 800;

}

.brand h2 { font-size: 18px; margin: 0; letter-spacing: .4px; }

.brand small { color: #aab8cb; }

.nav-title {

    color: #91a2ba;

    font-size: 10px;

    font-weight: 800;

    letter-spacing: 1.5px;

    padding: 25px 12px 10px;

}

.sidebar nav a {

    display: flex;

    align-items: center;

    gap: 12px;

    color: #c4d0df;

    text-decoration: none;

    padding: 12px 13px;

    margin: 4px 0;

    border-radius: 8px;

    transition: .15s;

}

.sidebar nav a:hover,

.sidebar nav a.active {

    background: var(--navy-light);

    color: white;

}

.sidebar nav a.active { box-shadow: inset 3px 0 var(--blue); }

.nav-icon { width: 20px; text-align: center; font-size: 16px; }

.sidebar-footer {

    margin: 35px 8px 0;

    border-top: 1px solid rgba(255,255,255,.12);

    padding: 18px 5px;

    color: #9eafc4;

    font-size: 12px;

    line-height: 1.7;

}

.main {

    margin-left: 245px;

    min-width: 0;

}

.topbar {

    height: 76px;

    background: white;

    border-bottom: 1px solid var(--border);

    padding: 0 34px;

    display: flex;

    justify-content: space-between;

    align-items: center;

    gap: 15px;

}

.topbar h1 { font-size: 20px; margin: 0; }

.topbar p { margin: 5px 0 0; color: var(--muted); font-size: 12px; }

.user-chip {

    display: flex;

    align-items: center;

    gap: 10px;

    font-weight: 700;

    white-space: nowrap;

}

.avatar {

    width: 36px;

    height: 36px;

    border-radius: 50%;

    background: #e6edff;

    color: var(--blue);

    display: grid;

    place-items: center;

    font-weight: 800;

}

.content { padding: 30px 34px; max-width: 1600px; margin: auto; }

.page-heading {

    display: flex;

    justify-content: space-between;

    align-items: center;

    gap: 15px;

    flex-wrap: wrap;

    margin-bottom: 23px;

}

.page-heading h2 { font-size: 23px; margin: 0; }

.page-heading p { color: var(--muted); margin: 7px 0 0; }

.grid {

    display: grid;

    grid-template-columns: repeat(4, minmax(0, 1fr));

    gap: 17px;

    margin-bottom: 24px;

}

.stat-card, .card {

    background: var(--white);

    border: 1px solid var(--border);

    border-radius: 13px;

    box-shadow: var(--shadow);

}

.stat-card { padding: 22px; min-width: 0; }

.stat-top { display: flex; justify-content: space-between; gap: 8px; }

.stat-label { color: var(--muted); font-weight: 600; }

.stat-icon {

    width: 39px; height: 39px;

    display: grid; place-items: center;

    border-radius: 10px; font-size: 19px;

}

.stat-value { font-size: 27px; font-weight: 800; margin-top: 18px; overflow-wrap: anywhere; }

.stat-note { font-size: 12px; color: var(--muted); margin-top: 8px; }

.blue-bg { background: #e8eeff; }

.green-bg { background: #e2f6ed; }

.orange-bg { background: #fff0dc; }

.purple-bg { background: #f0e9ff; }

.card { padding: 23px; margin-bottom: 22px; min-width: 0; }

.card-head {

    display: flex; align-items: center;

    justify-content: space-between; gap: 12px;

    margin-bottom: 19px; flex-wrap: wrap;

}

.card h3 { font-size: 16px; margin: 0; }

.muted { color: var(--muted); }

.small { font-size: 12px; }

label { display: block; font-weight: 700; margin: 13px 0 7px; }

input, select, textarea {

    width: 100%;

    padding: 11px 12px;

    border: 1px solid #d6deea;

    border-radius: 7px;

    background: white;

    color: var(--text);

    font: inherit;

    outline: none;

}

input:focus, select:focus, textarea:focus {

    border-color: var(--blue);

    box-shadow: 0 0 0 3px rgba(53,99,233,.10);

}

textarea { resize: vertical; min-height: 85px; }

.form-grid {

    display: grid;

    grid-template-columns: repeat(2, minmax(0, 1fr));

    gap: 0 18px;

}

.form-full { grid-column: 1 / -1; }

.btn {

    display: inline-flex; align-items: center;

    justify-content: center; gap: 7px;

    padding: 10px 15px;

    background: var(--blue);

    color: white;

    border: 0;

    border-radius: 7px;

    font: inherit; font-weight: 700;

    text-decoration: none; cursor: pointer;

}

.btn:hover { background: var(--blue-hover); }

.btn-secondary { background: #eaf0fb; color: #29446f; }

.btn-secondary:hover { background: #dce6f8; }

.btn-success { background: var(--green); }

.btn-success:hover { background: #116d4b; }

.btn-danger { background: #fff0f1; color: var(--red); }

.btn-danger:hover { background: #ffe1e4; }

.btn-small { padding: 7px 9px; font-size: 12px; }

.actions { display: flex; flex-wrap: wrap; gap: 7px; align-items: center; }

.inline-form { display: inline-flex; align-items: center; gap: 5px; }

.inline-form input { width: 125px; padding: 8px; }

.inline-form button { white-space: nowrap; }

.table-wrap { width: 100%; overflow-x: auto; }

table { width: 100%; border-collapse: collapse; white-space: nowrap; }

th {

    text-align: left;

    background: #f7f9fc;

    color: #62718a;

    font-size: 11px;

    text-transform: uppercase;

    letter-spacing: .55px;

    font-weight: 800;

}

th, td { padding: 14px 12px; border-bottom: 1px solid #edf0f5; }

tbody tr:hover { background: #fafcff; }

tbody tr:last-child td { border-bottom: 0; }

.item-primary { font-weight: 700; }

.item-secondary { color: var(--muted); font-size: 12px; margin-top: 4px; }

.badge {

    display: inline-block; padding: 5px 9px;

    border-radius: 20px; font-size: 11px; font-weight: 800;

}

.badge-draft { background: #edf1f7; color: #59677a; }

.badge-confirmed { background: #fff1d8; color: #95600d; }

.badge-received { background: #ddf7e9; color: #127448; }

.badge-cancelled { background: #ffe5e8; color: #b42336; }

.badge-in { background: #ddf7e9; color: #127448; }

.badge-out { background: #ffe5e8; color: #b42336; }

.badge-low { background: #fff1d8; color: #95600d; }

.badge-ok { background: #ddf7e9; color: #127448; }

.notice {

    border-radius: 8px;

    padding: 13px 16px;

    margin-bottom: 18px;

    background: #ddf7e9;

    color: #126b46;

    border: 1px solid #bcebd2;

}

.notice.error {

    background: #fff0f1;

    color: #a62939;

    border-color: #ffd1d7;

}

.empty { padding: 30px; text-align: center; color: var(--muted); }

.total-line {

    display: flex; justify-content: flex-end;

    font-weight: 800; font-size: 17px; padding-top: 15px;

}

.product-row {

    border: 1px solid var(--border);

    border-radius: 9px;

    padding: 15px;

    margin: 12px 0;

    background: #fbfcff;

}

.product-row-grid {

    display: grid;

    grid-template-columns: minmax(180px, 2fr) minmax(90px, .8fr)

                           minmax(110px, 1fr) auto;

    gap: 12px; align-items: end;

}

.product-row label { margin-top: 0; }

.product-row .remove-button { margin-bottom: 1px; }

.footer-note {

    color: var(--muted);

    font-size: 12px;

    margin-top: 17px;

    line-height: 1.7;

}

@media(max-width: 1150px) {

    .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }

    .content { padding: 24px 20px; }

    .topbar { padding: 0 20px; }

}

@media(max-width: 760px) {

    .sidebar { position: static; width: 100%; padding: 14px; }

    .brand { padding-bottom: 13px; }

    .sidebar nav { display: grid; grid-template-columns: repeat(2, 1fr); gap: 3px; }

    .nav-title, .sidebar-footer { display: none; }

    .main { margin-left: 0; }

    .topbar { height: auto; min-height: 68px; padding: 14px 18px; }

    .content { padding: 18px 12px; }

    .card { padding: 16px; }

    .grid { gap: 10px; }

    .stat-card { padding: 15px; }

    .stat-value { font-size: 22px; }

    .form-grid { grid-template-columns: 1fr; }

    .form-full { grid-column: auto; }

    .product-row-grid { grid-template-columns: 1fr 1fr; }

    .product-row-grid .product-select { grid-column: 1 / -1; }

    .user-chip span { display: none; }

}

</style>

</head>

<body>

<div class="layout">

    <aside class="sidebar">

        <div class="brand">

            <div class="brand-icon">M</div>

            <div>

                <h2>MuDaSiR ERP</h2>

                <small>Inventory Suite</small>

            </div>

        </div>

        <nav>

            <div class="nav-title">WORKSPACE</div>

            <a href="{{ url_for('dashboard') }}" class="{{ 'active' if active == 'dashboard' else '' }}">

                <span class="nav-icon">▦</span> Dashboard

            </a>
            
<a href="{{ url_for('projects') }}"
   class="{{ 'active' if active == 'projects' else '' }}">
    <span class="nav-icon">▣</span> Projects
</a>


            <a href="{{ url_for('products') }}" class="{{ 'active' if active == 'products' else '' }}">

                <span class="nav-icon">▤</span> Products

            </a>

            <a href="{{ url_for('low_stock_alerts') }}" class="{{ 'active' if active == 'low_stock_alerts' else '' }}">

                <span class="nav-icon">⚠</span> Low Stock Alerts

            </a>

            <a href="{{ url_for('add_product') }}" class="{{ 'active' if active == 'add_product' else '' }}">

                <span class="nav-icon">＋</span> Add Product

            </a>

            <a href="{{ url_for('suppliers') }}" class="{{ 'active' if active == 'suppliers' else '' }}">

                <span class="nav-icon">♙</span> Suppliers

            </a>

            <div class="nav-title">PROCUREMENT</div>

            <a href="{{ url_for('purchase_orders') }}" class="{{ 'active' if active == 'purchase_orders' else '' }}">

                <span class="nav-icon">▣</span> Purchase Orders

            </a>

            <div class="nav-title">INVENTORY</div>

            <a href="{{ url_for('stock') }}" class="{{ 'active' if active == 'stock' else '' }}">

                <span class="nav-icon">⇅</span> Stock IN / OUT

            </a>

            <a href="{{ url_for('material_issuance') }}" class="{{ 'active' if active == 'material_issuance' else '' }}">

                <span class="nav-icon">⇢</span> Material Issuance

            </a>

            <a href="{{ url_for('movements') }}" class="{{ 'active' if active == 'movements' else '' }}">

                <span class="nav-icon">◷</span> Movement History

            </a>

            <a href="{{ url_for('reports') }}" class="{{ 'active' if active == 'reports' else '' }}">

                <span class="nav-icon">▥</span> Reports &amp; Analytics

            </a>

        </nav>

        <div class="sidebar-footer">

            <strong>Local ERP System</strong><br>

            Python · Flask · SQLite<br>

            <span>Development Edition</span>

        </div>

    </aside>

    <div class="main">

        <header class="topbar">

            <div>

                <h1>{{ page_title or 'Dashboard' }}</h1>

                <p>Inventory &amp; procurement management</p>

            </div>

            <div class="user-chip">

                <div class="avatar">AD</div>

                <span>Administrator</span>

            </div>

        </header>

        <main class="content">

            {% for category, message in get_flashed_messages(with_categories=true) %}

            <div class="notice {{ 'error' if category == 'error' else '' }}">

                {{ message }}

            </div>

            {% endfor %}

            {{ content|safe }}

        </main>

    </div>

</div>

</body>

</html>

"""

def page(content, page_title="Dashboard", active="dashboard", **context):

    inner = render_template_string(content, **context)

    return render_template_string(

        PAGE,

        content=inner,

        page_title=page_title,

        active=active

    )

def money(value):

    return "{:,.2f}".format(value or 0)

# --------------------------------------------------

# DASHBOARD

# --------------------------------------------------

@app.route("/")
def dashboard():
    """Read-only dashboard; does not create, update, or delete ERP data."""
    with get_db() as conn:
        product_count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        supplier_count = conn.execute("SELECT COUNT(*) FROM suppliers").fetchone()[0]
        stock_units = conn.execute(
            "SELECT COALESCE(SUM(stock_qty), 0) FROM products"
        ).fetchone()[0]
        low_stock = conn.execute("""
            SELECT COUNT(*) FROM products WHERE stock_qty <= min_stock
        """).fetchone()[0]
        inventory_value = conn.execute("""
            SELECT COALESCE(SUM(stock_qty * cost_price), 0) FROM products
        """).fetchone()[0]
        open_orders = conn.execute("""
            SELECT COUNT(*) FROM purchase_orders
            WHERE status IN ('Draft', 'Confirmed')
        """).fetchone()[0]
        received_orders = conn.execute("""
            SELECT COUNT(*) FROM purchase_orders WHERE status = 'Received'
        """).fetchone()[0]
        project_count = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
        low_stock_items = conn.execute("""
            SELECT item_code, name, stock_qty, min_stock, unit
            FROM products WHERE stock_qty <= min_stock
            ORDER BY (min_stock - stock_qty) DESC, name ASC LIMIT 8
        """).fetchall()
        recent_orders = conn.execute("""
            SELECT po.id, po.po_number, po.order_date, po.status,
                   s.name AS supplier_name,
                   COALESCE(SUM(pol.quantity * pol.unit_price), 0) AS total
            FROM purchase_orders po
            JOIN suppliers s ON s.id = po.supplier_id
            LEFT JOIN purchase_order_lines pol ON pol.purchase_order_id = po.id
            GROUP BY po.id
            ORDER BY po.id DESC LIMIT 8
        """).fetchall()
        recent = conn.execute("""
            SELECT m.*, p.item_code, p.name, p.unit
            FROM stock_movements m
            JOIN products p ON p.id = m.product_id
            ORDER BY m.id DESC LIMIT 8
        """).fetchall()

    return page("""
    <div class="page-heading">
        <div>
            <h2>Overview</h2>
            <p>Inventory, purchasing and project activity at a glance.</p>
        </div>
        <div class="actions">
            <a class="btn btn-secondary" href="{{ url_for('purchase_orders') }}">＋ New Purchase Order</a>
            <a class="btn" href="{{ url_for('add_product') }}">＋ Add Product</a>
        </div>
    </div>

    <div class="grid">
        <div class="stat-card"><div class="stat-top"><span class="stat-label">Products</span><span class="stat-icon blue-bg">▤</span></div><div class="stat-value">{{ product_count }}</div><div class="stat-note">Products in catalogue</div></div>
        <div class="stat-card"><div class="stat-top"><span class="stat-label">Stock Units</span><span class="stat-icon green-bg">▦</span></div><div class="stat-value">{{ "{:,.2f}".format(stock_units) }}</div><div class="stat-note">Combined on-hand quantity</div></div>
        <div class="stat-card"><div class="stat-top"><span class="stat-label">Low Stock</span><span class="stat-icon orange-bg">⚠</span></div><div class="stat-value">{{ low_stock }}</div><div class="stat-note">At or below minimum level</div></div>
        <div class="stat-card"><div class="stat-top"><span class="stat-label">Inventory Value</span><span class="stat-icon purple-bg">¤</span></div><div class="stat-value">{{ "{:,.2f}".format(inventory_value) }}</div><div class="stat-note">Stock quantity × cost price</div></div>
        <div class="stat-card"><div class="stat-top"><span class="stat-label">Suppliers</span><span class="stat-icon blue-bg">♙</span></div><div class="stat-value">{{ supplier_count }}</div><div class="stat-note">Registered suppliers</div></div>
        <div class="stat-card"><div class="stat-top"><span class="stat-label">Open POs</span><span class="stat-icon orange-bg">▣</span></div><div class="stat-value">{{ open_orders }}</div><div class="stat-note">Draft or confirmed orders</div></div>
        <div class="stat-card"><div class="stat-top"><span class="stat-label">Received POs</span><span class="stat-icon green-bg">✓</span></div><div class="stat-value">{{ received_orders }}</div><div class="stat-note">Orders marked received</div></div>
        <div class="stat-card"><div class="stat-top"><span class="stat-label">Projects</span><span class="stat-icon purple-bg">▣</span></div><div class="stat-value">{{ project_count }}</div><div class="stat-note">Projects in the system</div></div>
    </div>

    <section class="card">
        <div class="card-head"><div><h3>Low Stock Alerts</h3><div class="muted small">Items at or below their configured minimum stock level</div></div><a class="btn btn-secondary btn-small" href="{{ url_for('products') }}">View Products</a></div>
        <div class="table-wrap"><table><thead><tr><th>Item Code</th><th>Product</th><th>Current Stock</th><th>Minimum Stock</th><th>Status</th></tr></thead><tbody>
        {% for item in low_stock_items %}
          <tr><td class="item-primary">{{ item['item_code'] }}</td><td>{{ item['name'] }}</td><td>{{ "{:,.2f}".format(item['stock_qty'] or 0) }} {{ item['unit'] or '' }}</td><td>{{ "{:,.2f}".format(item['min_stock'] or 0) }} {{ item['unit'] or '' }}</td><td><span class="badge badge-low">Low stock</span></td></tr>
        {% else %}<tr><td colspan="5" class="empty">No low-stock items. Inventory levels look good.</td></tr>{% endfor %}
        </tbody></table></div>
    </section>

    <section class="card">
        <div class="card-head"><div><h3>Recent Purchase Orders</h3><div class="muted small">Latest orders and their recorded totals</div></div><a class="btn btn-secondary btn-small" href="{{ url_for('purchase_orders') }}">View All POs</a></div>
        <div class="table-wrap"><table><thead><tr><th>PO Number</th><th>Date</th><th>Supplier</th><th>Status</th><th>Total Amount</th><th>Action</th></tr></thead><tbody>
        {% for order in recent_orders %}
          <tr><td class="item-primary">{{ order['po_number'] }}</td><td>{{ order['order_date'] }}</td><td>{{ order['supplier_name'] }}</td><td><span class="badge {% if order['status'] == 'Received' %}badge-received{% elif order['status'] == 'Confirmed' %}badge-confirmed{% elif order['status'] == 'Cancelled' %}badge-cancelled{% else %}badge-draft{% endif %}">{{ order['status'] }}</span></td><td>{{ "{:,.2f}".format(order['total'] or 0) }}</td><td><a class="btn btn-secondary btn-small" href="{{ url_for('po_details', purchase_order_id=order['id']) }}">Open</a></td></tr>
        {% else %}<tr><td colspan="6" class="empty">No purchase orders have been created yet.</td></tr>{% endfor %}
        </tbody></table></div>
    </section>

    <section class="card">
        <div class="card-head"><div><h3>Recent Stock Movements</h3><div class="muted small">Latest stock IN and OUT transactions</div></div><a class="btn btn-secondary btn-small" href="{{ url_for('movements') }}">View All</a></div>
        <div class="table-wrap"><table><thead><tr><th>Date</th><th>Item</th><th>Movement</th><th>Quantity</th><th>Reference</th></tr></thead><tbody>
        {% for movement in recent %}
          <tr><td>{{ movement['movement_date'] if 'movement_date' in movement.keys() else (movement['created_at'] if 'created_at' in movement.keys() else (movement['date'] if 'date' in movement.keys() else '—')) }}</td><td><div class="item-primary">{{ movement['item_code'] }}</div><div class="item-secondary">{{ movement['name'] }}</div></td><td><span class="badge {{ 'badge-in' if movement['movement_type'] == 'IN' else 'badge-out' }}">{{ movement['movement_type'] }}</span></td><td>{{ "{:,.2f}".format(movement['quantity'] or 0) }} {{ movement['unit'] or '' }}</td><td>{{ movement['reference'] or '—' }}</td></tr>
        {% else %}<tr><td colspan="5" class="empty">No stock movements recorded yet.</td></tr>{% endfor %}
        </tbody></table></div>
    </section>
    <p class="footer-note">Dashboard figures are calculated from existing records. This page does not modify inventory, purchase orders, projects or database structure.</p>
    """, page_title="Dashboard", active="dashboard",
        product_count=product_count, supplier_count=supplier_count,
        stock_units=stock_units, low_stock=low_stock,
        inventory_value=inventory_value, open_orders=open_orders,
        received_orders=received_orders, project_count=project_count,
        low_stock_items=low_stock_items, recent_orders=recent_orders,
        recent=recent)

# --------------------------------------------------

# SUPPLIERS

# --------------------------------------------------

@app.route("/suppliers", methods=["GET", "POST"])

def suppliers():

    if request.method == "POST":

        name = request.form.get("name", "").strip()

        phone = request.form.get("phone", "").strip()

        email = request.form.get("email", "").strip()

        address = request.form.get("address", "").strip()

        if not name:

            flash("Supplier name is required.", "error")

        else:

            with get_db() as conn:

                conn.execute("""

                    INSERT INTO suppliers (name, phone, email, address)

                    VALUES (?, ?, ?, ?)

                """, (name, phone, email, address))

            flash("Supplier added successfully.")

            return redirect(url_for("suppliers"))

    with get_db() as conn:

        rows = conn.execute("""

            SELECT * FROM suppliers ORDER BY id DESC

        """).fetchall()

    return page("""

    <div class="page-heading">

        <div>

            <h2>Supplier Management</h2>

            <p>Maintain your vendor and supplier directory.</p>

        </div>

    </div>

    <section class="card">

        <div class="card-head"><h3>Add New Supplier</h3></div>

        <form method="post">

            <div class="form-grid">

                <div>

                    <label>Supplier Name *</label>

                    <input name="name" required placeholder="ABC Enterprises">

                </div>

                <div>

                    <label>Phone Number</label>

                    <input name="phone" placeholder="+92 ...">

                </div>

                <div>

                    <label>Email Address</label>

                    <input type="email" name="email" placeholder="supplier@example.com">

                </div>

                <div>

                    <label>Address</label>

                    <input name="address" placeholder="City / address">

                </div>

            </div>

            <p><button class="btn" type="submit">Save Supplier</button></p>

        </form>

    </section>

    <section class="card">

        <div class="card-head">

            <h3>Supplier Directory</h3>

            <span class="badge badge-draft">{{ rows|length }} suppliers</span>

        </div>

        <div class="table-wrap">

        <table>

            <thead><tr><th>Supplier</th><th>Phone</th><th>Email</th><th>Address</th></tr></thead>

            <tbody>

            {% for s in rows %}

            <tr>

                <td class="item-primary">{{ s['name'] }}</td>

                <td>{{ s['phone'] or '-' }}</td>

                <td>{{ s['email'] or '-' }}</td>

                <td>{{ s['address'] or '-' }}</td>

            </tr>

            {% else %}

            <tr><td colspan="4" class="empty">No suppliers added yet.</td></tr>

            {% endfor %}

            </tbody>

        </table>

        </div>

    </section>

    """, page_title="Suppliers", active="suppliers", rows=rows)

# --------------------------------------------------

# PRODUCTS

# --------------------------------------------------

@app.route("/products")

def products():

    search = request.args.get("q", "").strip()

    with get_db() as conn:

        rows = conn.execute("""

            SELECT * FROM products

            WHERE item_code LIKE ? OR name LIKE ? OR category LIKE ?

            ORDER BY id DESC

        """, (f"%{search}%", f"%{search}%", f"%{search}%")).fetchall()

    return page("""

    <div class="page-heading">

        <div>

            <h2>Product Catalogue</h2>

            <p>Manage item codes, descriptions, prices and stock levels.</p>

        </div>

        <a class="btn" href="{{ url_for('add_product') }}">＋ Add Product</a>

    </div>

    <section class="card">

        <form method="get" class="actions" style="margin-bottom:18px">

            <input name="q" value="{{ search }}" placeholder="Search code, description or category"

                   style="max-width:400px">

            <button class="btn" type="submit">Search</button>

            <a class="btn btn-secondary" href="{{ url_for('products') }}">Clear</a>

        </form>

        <div class="table-wrap">

        <table>

            <thead>

            <tr><th>Item</th><th>Category</th><th>Stock</th><th>UOM</th>

            <th>Cost Price</th><th>Sale Price</th><th>Stock Status</th></tr>

            </thead>

            <tbody>

            {% for p in rows %}

            <tr>

                <td>

                    <div class="item-primary">{{ p['item_code'] }}</div>

                    <div class="item-secondary">{{ p['name'] }}</div>

                </td>

                <td>{{ p['category'] or '-' }}</td>

                <td>{{ p['stock_qty'] }}</td>

                <td>{{ p['unit'] }}</td>

                <td>{{ "{:,.2f}".format(p['cost_price']) }}</td>

                <td>{{ "{:,.2f}".format(p['sale_price']) }}</td>

                <td>

                    {% if p['stock_qty'] <= p['min_stock'] %}

                    <span class="badge badge-low">Low Stock</span>

                    {% else %}

                    <span class="badge badge-ok">In Stock</span>

                    {% endif %}

                </td>

            </tr>

            {% else %}

            <tr><td colspan="7" class="empty">No matching products found.</td></tr>

            {% endfor %}

            </tbody>

        </table>

        </div>

    </section>

    """, page_title="Products", active="products", rows=rows, search=search)


# --------------------------------------------------
# LOW STOCK ALERTS (READ-ONLY)
# --------------------------------------------------

@app.route("/low-stock", methods=["GET"])
def low_stock_alerts():
    """Show low-stock and out-of-stock products without modifying records."""
    search = request.args.get("q", "").strip()
    status = request.args.get("status", "low").strip().lower()
    if status not in {"low", "out", "all"}:
        status = "low"

    conditions = []
    params = []

    if status == "out":
        conditions.append("COALESCE(stock_qty, 0) <= 0")
    elif status == "low":
        conditions.append("COALESCE(stock_qty, 0) <= COALESCE(min_stock, 0)")
    # status == "all" intentionally leaves the stock-status condition empty.

    if search:
        conditions.append("(item_code LIKE ? OR name LIKE ? OR COALESCE(category, '') LIKE ?)")
        term = f"%{search}%"
        params.extend([term, term, term])

    where_sql = " AND ".join(conditions) if conditions else "1=1"
    with get_db() as conn:
        rows = conn.execute(f"""
            SELECT item_code, name, category, stock_qty, min_stock, unit, cost_price
            FROM products
            WHERE {where_sql}
            ORDER BY (COALESCE(min_stock, 0) - COALESCE(stock_qty, 0)) DESC, name ASC
        """, params).fetchall()
        low_count = conn.execute("""
            SELECT COUNT(*) FROM products
            WHERE COALESCE(stock_qty, 0) <= COALESCE(min_stock, 0)
        """).fetchone()[0]
        out_count = conn.execute("""
            SELECT COUNT(*) FROM products WHERE COALESCE(stock_qty, 0) <= 0
        """).fetchone()[0]

    return page("""
    <div class="page-heading">
      <div><h2>Low Stock Alerts</h2>
      <p>Find products that need replenishment. This page is read-only.</p></div>
      <a class="btn btn-secondary" href="{{ url_for('purchase_orders') }}">View Purchase Orders</a>
    </div>

    <div class="grid">
      <div class="stat-card"><div class="stat-label">Low / Minimum Stock</div><div class="stat-value">{{ low_count }}</div><div class="stat-note">At or below minimum quantity</div></div>
      <div class="stat-card"><div class="stat-label">Out of Stock</div><div class="stat-value">{{ out_count }}</div><div class="stat-note">Quantity is zero or less</div></div>
    </div>

    <section class="card">
      <form method="get" class="form-grid">
        <div><label>Search Item</label><input name="q" value="{{ search }}" placeholder="Item code, description or category"></div>
        <div><label>Alert Type</label><select name="status">
          <option value="low" {{ 'selected' if status == 'low' else '' }}>Low stock items</option>
          <option value="out" {{ 'selected' if status == 'out' else '' }}>Out of stock only</option>
          <option value="all" {{ 'selected' if status == 'all' else '' }}>All products</option>
        </select></div>
        <div class="form-full actions" style="margin-top:15px">
          <button class="btn" type="submit">Apply Filter</button>
          <a class="btn btn-secondary" href="{{ url_for('low_stock_alerts') }}">Clear</a>
        </div>
      </form>
    </section>

    <section class="card">
      <div class="card-head"><div><h3>Products Requiring Attention</h3><div class="muted small">{{ rows|length }} matching item(s)</div></div></div>
      <div class="table-wrap"><table><thead><tr><th>Item Code</th><th>Description</th><th>Category</th><th>Current Stock</th><th>Minimum Stock</th><th>Shortfall</th><th>Status</th></tr></thead><tbody>
      {% for item in rows %}
        <tr>
          <td class="item-primary">{{ item['item_code'] }}</td>
          <td>{{ item['name'] }}</td>
          <td>{{ item['category'] or '-' }}</td>
          <td>{{ "{:,.2f}".format(item['stock_qty'] or 0) }} {{ item['unit'] or '' }}</td>
          <td>{{ "{:,.2f}".format(item['min_stock'] or 0) }} {{ item['unit'] or '' }}</td>
          <td>{{ "{:,.2f}".format(((item['min_stock'] or 0) - (item['stock_qty'] or 0)) if ((item['min_stock'] or 0) > (item['stock_qty'] or 0)) else 0) }} {{ item['unit'] or '' }}</td>
          <td>{% if (item['stock_qty'] or 0) <= 0 %}<span class="badge badge-out">Out of stock</span>{% else %}<span class="badge badge-low">Low stock</span>{% endif %}</td>
        </tr>
      {% else %}<tr><td colspan="7" class="empty">No products match this alert filter.</td></tr>{% endfor %}
      </tbody></table></div>
      <p class="footer-note">Alerts use each product's existing current stock and minimum stock values. No new database table is created and no stock quantities are changed.</p>
    </section>
    """, page_title="Low Stock Alerts", active="low_stock_alerts",
        rows=rows, search=search, status=status, low_count=low_count, out_count=out_count)
        

@app.route("/products/add", methods=["GET", "POST"])

def add_product():

    if request.method == "POST":

        item_code = request.form.get("item_code", "").strip().upper()

        name = request.form.get("name", "").strip()

        category = request.form.get("category", "").strip()

        unit = request.form.get("unit", "Unit").strip() or "Unit"

        try:

            cost_price = float(request.form.get("cost_price", "0"))

            sale_price = float(request.form.get("sale_price", "0"))

            min_stock = float(request.form.get("min_stock", "0"))

            if not item_code or not name:

                raise ValueError("Item code and product description are required.")

            if min(cost_price, sale_price, min_stock) < 0:

                raise ValueError("Prices and minimum stock cannot be negative.")

            with get_db() as conn:

                conn.execute("""

                    INSERT INTO products

                    (item_code, name, category, unit,

                     cost_price, sale_price, min_stock)

                    VALUES (?, ?, ?, ?, ?, ?, ?)

                """, (item_code, name, category, unit,

                      cost_price, sale_price, min_stock))

            flash("Product created successfully.")

            return redirect(url_for("products"))

        except ValueError as exc:

            flash(str(exc), "error")

        except sqlite3.IntegrityError:

            flash("This item code already exists. Use a unique item code.", "error")

    return page("""

    <div class="page-heading">

        <div>

            <h2>Add New Product</h2>

            <p>Create an inventory item with its code and pricing.</p>

        </div>

        <a class="btn btn-secondary" href="{{ url_for('products') }}">← Back to Products</a>

    </div>

    <section class="card">

        <div class="card-head"><h3>Product Information</h3></div>

        <form method="post">

            <div class="form-grid">

                <div>

                    <label>Item Code *</label>

                    <input name="item_code" required placeholder="e.g. PPE0001">

                </div>

                <div>

                    <label>Product Description *</label>

                    <input name="name" required placeholder="e.g. SAFETY HELMET">

                </div>

                <div>

                    <label>Category</label>

                    <input name="category" placeholder="e.g. PPE">

                </div>

                <div>

                    <label>Unit of Measure</label>

                    <select name="unit">

                        <option>Unit</option><option>Each</option><option>Set</option>

                        <option>Pair</option><option>Box</option><option>Meter</option>

                        <option>Kg</option><option>Liter</option>

                    </select>

                </div>

                <div>

                    <label>Cost Price</label>

                    <input type="number" name="cost_price" min="0" step="0.01" value="0">

                </div>

                <div>

                    <label>Sale Price</label>

                    <input type="number" name="sale_price" min="0" step="0.01" value="0">

                </div>

                <div>

                    <label>Minimum Stock Alert</label>

                    <input type="number" name="min_stock" min="0" step="0.01" value="0">

                </div>

            </div>

            <p class="footer-note">The current stock starts at zero. Record an IN movement or receive a purchase order to increase stock.</p>

            <button class="btn" type="submit">Save Product</button>

        </form>

    </section>

    """, page_title="Add Product", active="add_product")

# --------------------------------------------------

# PURCHASE ORDERS - MULTIPLE PRODUCTS

# --------------------------------------------------

@app.route("/purchase-orders", methods=["GET", "POST"])

def purchase_orders():

    if request.method == "POST":

        supplier_id = request.form.get("supplier_id", type=int)

        notes = request.form.get("notes", "").strip()

        product_ids = request.form.getlist("product_id")

        quantities = request.form.getlist("quantity")

        prices = request.form.getlist("unit_price")

        try:
            if not supplier_id:
                raise ValueError("Please select a supplier.")

            if not (len(product_ids) == len(quantities) == len(prices)):
                raise ValueError("Product details are incomplete.")

            lines = []

            for pid, qty, price in zip(product_ids, quantities, prices):
                if not pid:
                    continue

                pid = int(pid)
                qty = float(qty)
                price = float(price)

                if qty <= 0:
                    raise ValueError("Each quantity must be greater than zero.")

                if price < 0:
                    raise ValueError("Unit price cannot be negative.")

                lines.append((pid, qty, price))

            if not lines:
                raise ValueError("Add at least one product to the PO.")

            product_ids_only = [line[0] for line in lines]

            if len(product_ids_only) != len(set(product_ids_only)):
                raise ValueError(
                    "A product is repeated. Select each product only once per PO."
                )

            with get_db() as conn:
                supplier = conn.execute(
                    "SELECT id FROM suppliers WHERE id = ?",
                    (supplier_id,)
                ).fetchone()

                if not supplier:
                    raise ValueError("Selected supplier does not exist.")

                for pid, qty, price in lines:
                    product = conn.execute(
                        "SELECT id FROM products WHERE id = ?",
                        (pid,)
                    ).fetchone()

                    if not product:
                        raise ValueError("One of the selected products is invalid.")

                po_number = f"PO-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

                cursor = conn.execute("""
                    INSERT INTO purchase_orders
                        (po_number, supplier_id, order_date, notes)
                    VALUES (?, ?, DATE('now'), ?)
                """, (po_number, supplier_id, notes))

                purchase_order_id = cursor.lastrowid

                for pid, qty, price in lines:
                    conn.execute("""
                        INSERT INTO purchase_order_lines
                            (purchase_order_id, product_id, quantity, unit_price)
                        VALUES (?, ?, ?, ?)
                    """, (purchase_order_id, pid, qty, price))

            flash(
                f"PO-{purchase_order_id:04d} created with {len(lines)} product(s)."
            )
            return redirect(url_for("purchase_orders"))

        except ValueError as exc:
            flash(str(exc), "error")
            return redirect(url_for("purchase_orders"))

        except sqlite3.IntegrityError:
            app.logger.exception("Purchase order integrity error")
            flash(
                "Could not create the purchase order. Please check the supplier, "
                "products and database constraints.",
                "error"
            )
            return redirect(url_for("purchase_orders"))

        except sqlite3.Error:
            app.logger.exception("Database error while creating purchase order")
            flash("A database error occurred while creating the PO.", "error")
            return redirect(url_for("purchase_orders"))

    with get_db() as conn:

        suppliers = conn.execute("""

            SELECT id, name FROM suppliers ORDER BY name

        """).fetchall()

        products = conn.execute("""

            SELECT id, item_code, name, cost_price

            FROM products ORDER BY name

        """).fetchall()

        orders = conn.execute("""

            SELECT po.id, po.order_date, po.status, po.grn_reference,

                   s.name AS supplier_name,

                   COALESCE(SUM(pol.quantity * pol.unit_price), 0) AS total,

                   COUNT(pol.id) AS product_count

            FROM purchase_orders po

            JOIN suppliers s ON s.id = po.supplier_id

            LEFT JOIN purchase_order_lines pol ON pol.purchase_order_id = po.id

            GROUP BY po.id

            ORDER BY po.id DESC

        """).fetchall()

    return page("""

    <div class="page-heading">

        <div>

            <h2>Purchase Orders</h2>

            <p>Create orders, confirm them and receive materials against a GRN.</p>

        </div>

    </div>

    <section class="card">

        <div class="card-head"><h3>Create Purchase Order</h3></div>

        {% if not suppliers %}

            <p class="muted">Please add a supplier before creating a purchase order.</p>

        {% elif not products %}

            <p class="muted">Please add products before creating a purchase order.</p>

        {% else %}

        <form method="post">

            <label>Supplier *</label>

            <select name="supplier_id" required>

                {% for s in suppliers %}

                <option value="{{ s['id'] }}">{{ s['name'] }}</option>

                {% endfor %}

            </select>

            <div class="card-head" style="margin-top:25px">

                <h3>Order Lines</h3>

                <button type="button" class="btn btn-secondary" onclick="addProductRow()">

                    ＋ Add Product

                </button>

            </div>

            <div id="product-rows">

                <div class="product-row">

                    <div class="product-row-grid">

                        <div class="product-select">

                            <label>Product *</label>

                            <select name="product_id" required>

                                {% for p in products %}

                                <option value="{{ p['id'] }}">

                                    {{ p['item_code'] }} — {{ p['name'] }}

                                </option>

                                {% endfor %}

                            </select>

                        </div>

                        <div>

                            <label>Quantity *</label>

                            <input type="number" name="quantity" min="0.01" step="any" required>

                        </div>

                        <div>

                            <label>Unit Price *</label>

                            <input type="number" name="unit_price" min="0" step="any" value="0" required>

                        </div>

                        <div class="remove-button"></div>

                    </div>

                </div>

            </div>

            <template id="product-row-template">

                <div class="product-row">

                    <div class="product-row-grid">

                        <div class="product-select">

                            <label>Product *</label>

                            <select name="product_id" required>

                                {% for p in products %}

                                <option value="{{ p['id'] }}">

                                    {{ p['item_code'] }} — {{ p['name'] }}

                                </option>

                                {% endfor %}

                            </select>

                        </div>

                        <div>

                            <label>Quantity *</label>

                            <input type="number" name="quantity" min="0.01" step="any" required>

                        </div>

                        <div>

                            <label>Unit Price *</label>

                            <input type="number" name="unit_price" min="0" step="any" value="0" required>

                        </div>

                        <div class="remove-button">

                            <button type="button" class="btn btn-danger btn-small"

                                    onclick="this.closest('.product-row').remove()">

                                Remove

                            </button>

                        </div>

                    </div>

                </div>

            </template>

            <label>Notes</label>

            <textarea name="notes" placeholder="Optional delivery details or order notes"></textarea>

            <p class="footer-note">

                Each product can appear only once in this PO. Enter the ordered quantity and agreed unit price.

            </p>

            <button type="submit" class="btn">Create Purchase Order</button>

        </form>

        <script>

        function addProductRow() {

            const template = document.getElementById("product-row-template");

            const clone = template.content.cloneNode(true);

            document.getElementById("product-rows").appendChild(clone);

        }

        </script>

        {% endif %}

    </section>

    <section class="card">

        <div class="card-head">

            <h3>Purchase Order Register</h3>

            <span class="badge badge-draft">{{ orders|length }} orders</span>

        </div>

        <div class="table-wrap">

        <table>

            <thead>

            <tr><th>PO Number</th><th>Date</th><th>Supplier</th><th>Lines</th>

                <th>Status</th><th>Total</th><th>GRN</th><th>Action</th></tr>

            </thead>

            <tbody>

            {% for o in orders %}

            <tr>

                <td class="item-primary">

    <a href="{{ url_for('po_details', purchase_order_id=o['id']) }}">

        PO-{{ "%04d"|format(o['id']) }}

    </a>

</td>

                <td>{{ o['order_date'] }}</td>

                <td>{{ o['supplier_name'] }}</td>

                <td>{{ o['product_count'] }}</td>

                <td>

                    <span class="badge badge-{{ o['status']|lower }}">

                        {{ o['status'] }}

                    </span>

                </td>

                <td>{{ "{:,.2f}".format(o['total']) }}</td>

                <td>

    {% if o['grn_reference'] %}

        <a href="{{ url_for('grn_details', grn_reference=o['grn_reference']) }}">

            {{ o['grn_reference'] }}

        </a>

    {% else %}

        -

    {% endif %}

</td>

                <td>

                    <div class="actions">

                    {% if o['status'] == 'Draft' %}

                        <form method="post" action="{{ url_for('confirm_po', purchase_order_id=o['id']) }}">

                            <button class="btn btn-small" type="submit">Confirm PO</button>

                        </form>

                    {% elif o['status'] == 'Confirmed' %}

                        <form method="post" class="inline-form"

      action="{{ url_for('receive_po', purchase_order_id=o['id']) }}"

      onsubmit="return confirm('Receive this PO and generate a GRN automatically?');">

    <button class="btn btn-success btn-small" type="submit">

        Receive & Generate GRN

    </button>

</form>

                    {% elif o['status'] == 'Received' %}

                        <span class="muted small">Completed</span>

                    {% else %}

                        <span class="muted small">No action</span>

                    {% endif %}

                    </div>

                </td>

            </tr>

            {% else %}

            <tr><td colspan="8" class="empty">No purchase orders created yet.</td></tr>

            {% endfor %}

            </tbody>

        </table>

        </div>

        <p class="footer-note">

            Workflow: Draft → Confirmed → Received. Receiving a PO increases stock for each PO line and records a stock movement.

        </p>

    </section>

    """, page_title="Purchase Orders", active="purchase_orders",

        suppliers=suppliers, products=products, orders=orders)

@app.route("/purchase-orders/<int:purchase_order_id>/confirm", methods=["POST"])

def confirm_po(purchase_order_id):

    with get_db() as conn:

        order = conn.execute("""

            SELECT id, status FROM purchase_orders WHERE id = ?

        """, (purchase_order_id,)).fetchone()

        if order is None:

            flash("Purchase Order not found.", "error")

        elif order["status"] != "Draft":

            flash("Only Draft Purchase Orders can be confirmed.", "error")

        else:

            line_count = conn.execute("""

                SELECT COUNT(*) FROM purchase_order_lines WHERE purchase_order_id = ?

            """, (purchase_order_id,)).fetchone()[0]

            if line_count == 0:

                flash("Cannot confirm a PO without product lines.", "error")

            else:

                conn.execute("""

                    UPDATE purchase_orders SET status = 'Confirmed'

                    WHERE id = ? AND status = 'Draft'

                """, (purchase_order_id,))

                flash(f"PO-{purchase_order_id:04d} confirmed successfully.")

    return redirect(url_for("purchase_orders"))

@app.route("/purchase-orders/<int:purchase_order_id>/receive", methods=["POST"])
def receive_po(purchase_order_id):
    """Receive a confirmed PO and automatically create a unique GRN reference."""
    try:
        with get_db() as conn:
            order = conn.execute(
                "SELECT id, status FROM purchase_orders WHERE id = ?", (purchase_order_id,)
            ).fetchone()
            if order is None:
                raise ValueError("Purchase Order not found.")
            if order["status"] != "Confirmed":
                raise ValueError("Only Confirmed POs can be received.")

            lines = conn.execute("""
                SELECT pol.product_id, pol.quantity, p.item_code, p.name
                FROM purchase_order_lines pol
                JOIN products p ON p.id = pol.product_id
                WHERE pol.purchase_order_id = ?
            """, (purchase_order_id,)).fetchall()
            if not lines:
                raise ValueError("This PO has no product lines.")

            # Use a date-based sequence; check the database to avoid duplicates.
            from datetime import datetime
            date_prefix = datetime.now().strftime("%Y%m%d")
            existing = conn.execute("""
                SELECT grn_reference FROM purchase_orders
                WHERE grn_reference LIKE ?
                ORDER BY grn_reference DESC
            """, (f"GRN-{date_prefix}-%",)).fetchall()
            used_numbers = []
            for row in existing:
                try:
                    used_numbers.append(int(row["grn_reference"].rsplit("-", 1)[1]))
                except (ValueError, IndexError, TypeError):
                    pass
            next_number = max(used_numbers, default=0) + 1
            grn_reference = f"GRN-{date_prefix}-{next_number:04d}"

            # Validate every line before making any stock changes.
            for line in lines:
                if line["quantity"] <= 0:
                    raise ValueError(f"Invalid quantity for {line['item_code']}.")

            for line in lines:
                conn.execute("""
                    UPDATE products SET stock_qty = stock_qty + ? WHERE id = ?
                """, (line["quantity"], line["product_id"]))
                conn.execute("""
                    INSERT INTO stock_movements
                        (product_id, movement_type, quantity, reference, notes)
                    VALUES (?, 'IN', ?, ?, ?)
                """, (
                    line["product_id"], line["quantity"], grn_reference,
                    f"Material received against PO-{purchase_order_id:04d}"
                ))

            conn.execute("""
                UPDATE purchase_orders
                SET status = 'Received', grn_reference = ?
                WHERE id = ? AND status = 'Confirmed'
            """, (grn_reference, purchase_order_id))

        flash(f"PO-{purchase_order_id:04d} received. Stock updated and GRN {grn_reference} generated.")
    except ValueError as exc:
        flash(str(exc), "error")
    except sqlite3.Error as exc:
        app.logger.exception("Database error while receiving PO %s", purchase_order_id)
        flash("Could not receive this PO because of a database error. No changes were saved.", "error")
    return redirect(url_for("purchase_orders"))


@app.route("/purchase-orders/<int:purchase_order_id>")
def po_details(purchase_order_id):
    with get_db() as conn:
        order = conn.execute("""
            SELECT po.*, s.name AS supplier_name, s.phone AS supplier_phone,
                   s.email AS supplier_email, s.address AS supplier_address,
                   COALESCE(SUM(pol.quantity * pol.unit_price), 0) AS total
            FROM purchase_orders po
            JOIN suppliers s ON s.id = po.supplier_id
            LEFT JOIN purchase_order_lines pol ON pol.purchase_order_id = po.id
            WHERE po.id = ?
            GROUP BY po.id
        """, (purchase_order_id,)).fetchone()
        if order is None:
            flash("Purchase Order not found.", "error")
            return redirect(url_for("purchase_orders"))
        lines = conn.execute("""
            SELECT p.item_code, p.name, p.unit, pol.quantity, pol.unit_price,
                   (pol.quantity * pol.unit_price) AS line_total
            FROM purchase_order_lines pol
            JOIN products p ON p.id = pol.product_id
            WHERE pol.purchase_order_id = ? ORDER BY pol.id
        """, (purchase_order_id,)).fetchall()
    return page("""
    <div class="page-heading">
      <div><h2>Purchase Order PO-{{ "%04d"|format(order['id']) }}</h2>
      <p>Order details, supplier information and item lines.</p></div>
      <a class="btn btn-secondary" href="{{ url_for('purchase_orders') }}">← Back to Purchase Orders</a>
    </div>
    <section class="card">
      <div class="form-grid">
        <div><strong>Supplier</strong><p>{{ order['supplier_name'] }}</p></div>
        <div><strong>Order Date</strong><p>{{ order['order_date'] }}</p></div>
        <div><strong>Status</strong><p><span class="badge badge-{{ order['status']|lower }}">{{ order['status'] }}</span></p></div>
        <div><strong>GRN Reference</strong><p>{% if order['grn_reference'] %}<a href="{{ url_for('grn_details', grn_reference=order['grn_reference']) }}">{{ order['grn_reference'] }}</a>{% else %}-{% endif %}</p></div>
        <div><strong>Phone</strong><p>{{ order['supplier_phone'] or '-' }}</p></div>
        <div><strong>Email</strong><p>{{ order['supplier_email'] or '-' }}</p></div>
        <div class="form-full"><strong>Notes</strong><p>{{ order['notes'] or '-' }}</p></div>
      </div>
    </section>
    <section class="card">
      <div class="card-head"><h3>Order Lines</h3></div>
      <div class="table-wrap"><table><thead><tr><th>Item Code</th><th>Description</th><th>Quantity</th><th>UOM</th><th>Unit Price</th><th>Line Total</th></tr></thead><tbody>
      {% for line in lines %}<tr><td>{{ line['item_code'] }}</td><td>{{ line['name'] }}</td><td>{{ line['quantity'] }}</td><td>{{ line['unit'] }}</td><td>{{ "{:,.2f}".format(line['unit_price']) }}</td><td>{{ "{:,.2f}".format(line['line_total']) }}</td></tr>
      {% else %}<tr><td colspan="6" class="empty">No order lines found.</td></tr>{% endfor %}
      </tbody></table></div>
      <div class="total-line">Total: {{ "{:,.2f}".format(order['total']) }}</div>
    </section>
    """, page_title=f"PO-{purchase_order_id:04d}", active="purchase_orders", order=order, lines=lines)


@app.route("/grn/<path:grn_reference>")
def grn_details(grn_reference):
    with get_db() as conn:
        order = conn.execute("""
            SELECT po.*, s.name AS supplier_name,
                   COALESCE(SUM(pol.quantity * pol.unit_price), 0) AS total
            FROM purchase_orders po
            JOIN suppliers s ON s.id = po.supplier_id
            LEFT JOIN purchase_order_lines pol ON pol.purchase_order_id = po.id
            WHERE po.grn_reference = ? AND po.status = 'Received'
            GROUP BY po.id
        """, (grn_reference,)).fetchone()
        if order is None:
            flash("GRN not found.", "error")
            return redirect(url_for("purchase_orders"))
        lines = conn.execute("""
            SELECT p.item_code, p.name, p.unit, pol.quantity, pol.unit_price,
                   (pol.quantity * pol.unit_price) AS line_total
            FROM purchase_order_lines pol
            JOIN products p ON p.id = pol.product_id
            WHERE pol.purchase_order_id = ? ORDER BY pol.id
        """, (order["id"],)).fetchall()
    return page("""
    <div class="page-heading"><div><h2>Goods Received Note</h2><p>Automatically generated receipt record.</p></div>
      <a class="btn btn-secondary" href="{{ url_for('purchase_orders') }}">← Purchase Orders</a></div>
    <section class="card"><div class="form-grid">
      <div><strong>GRN Number</strong><p>{{ order['grn_reference'] }}</p></div>
      <div><strong>Purchase Order</strong><p><a href="{{ url_for('po_details', purchase_order_id=order['id']) }}">PO-{{ "%04d"|format(order['id']) }}</a></p></div>
      <div><strong>Supplier</strong><p>{{ order['supplier_name'] }}</p></div>
      <div><strong>Receipt Date</strong><p>{{ order['updated_at'] if 'updated_at' in order.keys() else order['order_date'] }}</p></div>
      <div><strong>Status</strong><p><span class="badge badge-received">Received</span></p></div>
    </div></section>
    <section class="card"><div class="card-head"><h3>Received Materials</h3></div>
      <div class="table-wrap"><table><thead><tr><th>Item Code</th><th>Description</th><th>Quantity Received</th><th>UOM</th><th>Unit Price</th><th>Total</th></tr></thead><tbody>
      {% for line in lines %}<tr><td>{{ line['item_code'] }}</td><td>{{ line['name'] }}</td><td>{{ line['quantity'] }}</td><td>{{ line['unit'] }}</td><td>{{ "{:,.2f}".format(line['unit_price']) }}</td><td>{{ "{:,.2f}".format(line['line_total']) }}</td></tr>
      {% else %}<tr><td colspan="6" class="empty">No receipt lines found.</td></tr>{% endfor %}
      </tbody></table></div><div class="total-line">Total: {{ "{:,.2f}".format(order['total']) }}</div>
      <p class="footer-note">This GRN was generated by the local ERP when the PO was received. Stock movement history records the same GRN reference.</p>
    </section>
    """, page_title="GRN Details", active="purchase_orders", order=order, lines=lines)

# --------------------------------------------------

# MANUAL STOCK IN / OUT

# --------------------------------------------------

@app.route("/stock", methods=["GET", "POST"])

def stock():

    if request.method == "POST":

        try:

            product_id = request.form.get("product_id", type=int)

            movement_type = request.form.get("movement_type", "")

            quantity = float(request.form.get("quantity", "0"))

            reference = request.form.get("reference", "").strip()

            notes = request.form.get("notes", "").strip()

            if not product_id:

                raise ValueError("Please select a product.")

            if movement_type not in ("IN", "OUT"):

                raise ValueError("Invalid stock movement type.")

            if quantity <= 0:

                raise ValueError("Quantity must be greater than zero.")

            with get_db() as conn:

                product = conn.execute("""

                    SELECT id, stock_qty FROM products WHERE id = ?

                """, (product_id,)).fetchone()

                if product is None:

                    raise ValueError("Product not found.")

                if movement_type == "OUT" and quantity > product["stock_qty"]:

                    raise ValueError(

                        f"Insufficient stock. Available: {product['stock_qty']}."

                    )

                if movement_type == "IN":

                    conn.execute("""

                        UPDATE products SET stock_qty = stock_qty + ?

                        WHERE id = ?

                    """, (quantity, product_id))

                else:

                    conn.execute("""

                        UPDATE products SET stock_qty = stock_qty - ?

                        WHERE id = ?

                    """, (quantity, product_id))

                conn.execute("""

                    INSERT INTO stock_movements

                        (product_id, movement_type, quantity, reference, notes)

                    VALUES (?, ?, ?, ?, ?)

                """, (product_id, movement_type, quantity, reference, notes))

            flash("Stock movement recorded successfully.")

            return redirect(url_for("stock"))

        except ValueError as exc:

            flash(str(exc), "error")

    with get_db() as conn:

        product_rows = conn.execute("""

            SELECT id, item_code, name, stock_qty, unit

            FROM products ORDER BY name

        """).fetchall()

    return page("""

    <div class="page-heading">

        <div>

            <h2>Stock IN / OUT</h2>

            <p>Record manual receipts and material issuance.</p>

        </div>

    </div>

    <section class="card">

        <div class="card-head"><h3>Record Stock Movement</h3></div>

        {% if not product_rows %}

            <p class="muted">Add a product before recording stock movements.</p>

        {% else %}

        <form method="post">

            <div class="form-grid">

                <div class="form-full">

                    <label>Product *</label>

                    <select name="product_id" required>

                        {% for p in product_rows %}

                        <option value="{{ p['id'] }}">

                            {{ p['item_code'] }} — {{ p['name'] }}

                            (Available: {{ p['stock_qty'] }} {{ p['unit'] }})

                        </option>

                        {% endfor %}

                    </select>

                </div>

                <div>

                    <label>Movement Type *</label>

                    <select name="movement_type" required>

                        <option value="IN">Stock IN / Receipt</option>

                        <option value="OUT">Stock OUT / Issuance</option>

                    </select>

                </div>

                <div>

                    <label>Quantity *</label>

                    <input type="number" name="quantity" min="0.01" step="any" required>

                </div>

                <div>

                    <label>Reference</label>

                    <input name="reference" placeholder="Issue number / receipt reference">

                </div>

                <div>

                    <label>Notes</label>

                    <input name="notes" placeholder="Reason or department">

                </div>

            </div>

            <p class="footer-note">Stock OUT is blocked when the requested quantity exceeds available stock.</p>

            <button class="btn" type="submit">Record Movement</button>

        </form>

        {% endif %}

    </section>

    """, page_title="Stock IN / OUT", active="stock",

        product_rows=product_rows)


# --------------------------------------------------
# MATERIAL ISSUANCE
# --------------------------------------------------

def init_material_issuance_db():
    """Create the issuance register without replacing existing tables or data."""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS material_issuances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                quantity REAL NOT NULL CHECK (quantity > 0),
                issued_to TEXT NOT NULL,
                department TEXT DEFAULT '',
                reference TEXT NOT NULL UNIQUE,
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)


@app.route("/material-issuance", methods=["GET", "POST"])
def material_issuance():
    if request.method == "POST":
        product_id = request.form.get("product_id", type=int)
        issued_to = request.form.get("issued_to", "").strip()
        department = request.form.get("department", "").strip()
        notes = request.form.get("notes", "").strip()

        try:
            quantity = float(request.form.get("quantity", "0"))
            if not product_id:
                raise ValueError("Please select a product.")
            if not issued_to:
                raise ValueError("Issued To is required.")
            if quantity <= 0:
                raise ValueError("Quantity must be greater than zero.")

            from datetime import datetime
            date_prefix = datetime.now().strftime("%Y%m%d")

            with get_db() as conn:
                product = conn.execute("""
                    SELECT id, item_code, name, stock_qty
                    FROM products WHERE id = ?
                """, (product_id,)).fetchone()
                if product is None:
                    raise ValueError("Selected product was not found.")
                if quantity > product["stock_qty"]:
                    raise ValueError(
                        f"Insufficient stock for {product['item_code']}. "
                        f"Available: {product['stock_qty']}."
                    )

                existing = conn.execute("""
                    SELECT reference FROM material_issuances
                    WHERE reference LIKE ? ORDER BY reference DESC
                """, (f"ISS-{date_prefix}-%",)).fetchall()
                used_numbers = []
                for row in existing:
                    try:
                        used_numbers.append(int(row["reference"].rsplit("-", 1)[1]))
                    except (ValueError, IndexError, TypeError):
                        pass
                reference = f"ISS-{date_prefix}-{max(used_numbers, default=0) + 1:04d}"

                # The conditional update prevents stock from going below zero.
                updated = conn.execute("""
                    UPDATE products SET stock_qty = stock_qty - ?
                    WHERE id = ? AND stock_qty >= ?
                """, (quantity, product_id, quantity))
                if updated.rowcount != 1:
                    raise ValueError("Stock is insufficient or changed. Refresh and try again.")

                conn.execute("""
                    INSERT INTO material_issuances
                        (product_id, quantity, issued_to, department, reference, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (product_id, quantity, issued_to, department, reference, notes))

                movement_notes = f"Issued to {issued_to}"
                if department:
                    movement_notes += f" | Department: {department}"
                if notes:
                    movement_notes += f" | {notes}"
                conn.execute("""
                    INSERT INTO stock_movements
                        (product_id, movement_type, quantity, reference, notes)
                    VALUES (?, 'OUT', ?, ?, ?)
                """, (product_id, quantity, reference, movement_notes))

            flash(f"Material issued successfully. Reference: {reference}")
            return redirect(url_for("material_issuance"))

        except ValueError as exc:
            flash(str(exc), "error")
        except sqlite3.IntegrityError:
            flash("Could not save issuance due to a database constraint. No changes were saved.", "error")
        except sqlite3.Error:
            app.logger.exception("Database error during material issuance")
            flash("Database error. No changes were saved.", "error")

    with get_db() as conn:
        # Safe migration: create only the new table if it does not exist.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS material_issuances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                quantity REAL NOT NULL CHECK (quantity > 0),
                issued_to TEXT NOT NULL,
                department TEXT DEFAULT '',
                reference TEXT NOT NULL UNIQUE,
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        products = conn.execute("""
            SELECT id, item_code, name, unit, stock_qty
            FROM products ORDER BY name
        """).fetchall()
        rows = conn.execute("""
            SELECT mi.*, p.item_code, p.name, p.unit
            FROM material_issuances mi
            JOIN products p ON p.id = mi.product_id
            ORDER BY mi.id DESC LIMIT 200
        """).fetchall()

    return page("""
    <div class="page-heading">
      <div><h2>Material Issuance</h2>
      <p>Issue available stock to an employee, department or project.</p></div>
    </div>
    <section class="card">
      <div class="card-head"><h3>Issue Material</h3></div>
      {% if not products %}
        <p class="muted">Add a product before issuing material.</p>
      {% else %}
      <form method="post">
        <div class="form-grid">
          <div class="form-full">
            <label>Product / Item Code *</label>
            <select name="product_id" required>
              {% for p in products %}
              <option value="{{ p['id'] }}">{{ p['item_code'] }} — {{ p['name'] }} | Available: {{ p['stock_qty'] }} {{ p['unit'] }}</option>
              {% endfor %}
            </select>
          </div>
          <div><label>Quantity to Issue *</label>
            <input type="number" name="quantity" min="0.01" step="any" required></div>
          <div><label>Issued To (Employee / Person) *</label>
            <input name="issued_to" required placeholder="e.g. Ahmed Ali"></div>
          <div><label>Department / Project</label>
            <input name="department" placeholder="e.g. HSE / Maintenance"></div>
          <div><label>Notes</label>
            <input name="notes" placeholder="Optional reason or details"></div>
        </div>
        <p class="footer-note">Stock decreases only when sufficient quantity is available. Each issue creates an ISS reference and an OUT movement.</p>
        <button class="btn btn-success" type="submit">Confirm Material Issue</button>
      </form>
      {% endif %}
    </section>
    <section class="card">
      <div class="card-head"><h3>Issuance History</h3>
        <span class="badge badge-draft">{{ rows|length }} recent records</span></div>
      <div class="table-wrap"><table>
        <thead><tr><th>Date</th><th>Issue Ref</th><th>Item</th><th>Quantity</th><th>Issued To</th><th>Department / Project</th><th>Notes</th></tr></thead>
        <tbody>
        {% for r in rows %}
        <tr><td>{{ r['created_at'] }}</td><td class="item-primary">{{ r['reference'] }}</td>
          <td><div class="item-primary">{{ r['item_code'] }}</div><div class="item-secondary">{{ r['name'] }}</div></td>
          <td>{{ r['quantity'] }} {{ r['unit'] }}</td><td>{{ r['issued_to'] }}</td>
          <td>{{ r['department'] or '-' }}</td><td>{{ r['notes'] or '-' }}</td></tr>
        {% else %}<tr><td colspan="7" class="empty">No material issues recorded yet.</td></tr>{% endfor %}
        </tbody>
      </table></div>
    </section>
    """, page_title="Material Issuance", active="material_issuance",
        products=products, rows=rows)


# --------------------------------------------------

# STOCK MOVEMENT HISTORY

# --------------------------------------------------

@app.route("/movements")

def movements():

    movement_type = request.args.get("type", "").strip().upper()

    search = request.args.get("q", "").strip()

    if movement_type not in ("", "IN", "OUT"):

        movement_type = ""

    with get_db() as conn:

        rows = conn.execute("""

            SELECT m.*, p.item_code, p.name, p.unit

            FROM stock_movements m

            JOIN products p ON p.id = m.product_id

            WHERE (? = '' OR m.movement_type = ?)

              AND (

                m.reference LIKE ? OR m.notes LIKE ?

                OR p.item_code LIKE ? OR p.name LIKE ?

              )

            ORDER BY m.id DESC

        """, (

            movement_type, movement_type,

            f"%{search}%", f"%{search}%",

            f"%{search}%", f"%{search}%"

        )).fetchall()

    return page("""

    <div class="page-heading">

        <div>

            <h2>Stock Movement History</h2>

            <p>Review recorded receipts, issues and GRN transactions.</p>

        </div>

    </div>

    <section class="card">

        <form method="get" class="actions" style="margin-bottom:18px">

            <input name="q" value="{{ search }}"

                   placeholder="Search item, reference or notes"

                   style="max-width:330px">

            <select name="type" style="max-width:170px">

                <option value="" {{ 'selected' if movement_type == '' else '' }}>All movements</option>

                <option value="IN" {{ 'selected' if movement_type == 'IN' else '' }}>Stock IN</option>

                <option value="OUT" {{ 'selected' if movement_type == 'OUT' else '' }}>Stock OUT</option>

            </select>

            <button class="btn" type="submit">Filter</button>

            <a class="btn btn-secondary" href="{{ url_for('movements') }}">Clear</a>

        </form>

        <div class="table-wrap">

        <table>

            <thead>

            <tr><th>Date</th><th>Item</th><th>Type</th><th>Quantity</th>

                <th>Reference</th><th>Notes</th></tr>

            </thead>

            <tbody>

            {% for m in rows %}

            <tr>

                <td>{{ m['created_at'] }}</td>

                <td>

                    <div class="item-primary">{{ m['item_code'] }}</div>

                    <div class="item-secondary">{{ m['name'] }}</div>

                </td>

                <td>

                    <span class="badge {{ 'badge-in' if m['movement_type'] == 'IN' else 'badge-out' }}">

                        {{ m['movement_type'] }}

                    </span>

                </td>

                <td>{{ m['quantity'] }} {{ m['unit'] }}</td>

                <td>{{ m['reference'] or '-' }}</td>

                <td>{{ m['notes'] or '-' }}</td>

            </tr>

            {% else %}

            <tr><td colspan="6" class="empty">No matching stock movements found.</td></tr>

            {% endfor %}

            </tbody>

        </table>

        </div>

    </section>

    """, page_title="Movement History", active="movements",

        rows=rows, search=search, movement_type=movement_type)
        
# --------------------------------------------------
# PROJECT MANAGEMENT
# --------------------------------------------------

PROJECT_STATUSES = [
    "Planned",
    "In Progress",
    "On Hold",
    "Completed",
    "Cancelled",
]


@app.route("/projects", methods=["GET"])
def projects():
    search = request.args.get("q", "").strip()

    with get_db() as conn:
        rows = conn.execute("""
            SELECT *
            FROM projects
            WHERE project_code LIKE ?
               OR name LIKE ?
               OR customer LIKE ?
            ORDER BY id DESC
        """, (
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        )).fetchall()

        total = conn.execute(
            "SELECT COUNT(*) FROM projects"
        ).fetchone()[0]

        active_count = conn.execute("""
            SELECT COUNT(*) FROM projects
            WHERE status = 'In Progress'
        """).fetchone()[0]

        completed_count = conn.execute("""
            SELECT COUNT(*) FROM projects
            WHERE status = 'Completed'
        """).fetchone()[0]

    return page("""
    <div class="page-heading">
        <div>
            <h2>Project Management</h2>
            <p>Create projects and monitor their status and progress.</p>
        </div>
        <a class="btn" href="{{ url_for('add_project') }}">
            + Create Project
        </a>
    </div>

    <div class="grid">
        <div class="stat-card">
            <div class="stat-label">Total Projects</div>
            <div class="stat-value">{{ total }}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">In Progress</div>
            <div class="stat-value">{{ active_count }}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Completed</div>
            <div class="stat-value">{{ completed_count }}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Search Results</div>
            <div class="stat-value">{{ rows|length }}</div>
        </div>
    </div>

    <section class="card">
        <form method="get" class="actions"
              style="margin-bottom:18px">
            <input name="q" value="{{ search }}"
                   placeholder="Search code, project or customer"
                   style="max-width:350px">
            <button class="btn" type="submit">Search</button>
            <a class="btn btn-secondary"
               href="{{ url_for('projects') }}">Clear</a>
        </form>

        <div class="table-wrap">
        <table>
            <thead>
                <tr>
                    <th>Project Code</th>
                    <th>Project Name</th>
                    <th>Customer</th>
                    <th>Start Date</th>
                    <th>End Date</th>
                    <th>Budget</th>
                    <th>Status / Progress</th>
                    <th>Update</th>
                </tr>
            </thead>
            <tbody>
            {% for p in rows %}
                <tr>
                    <td class="item-primary">
                        {{ p['project_code'] }}
                    </td>
                    <td>
                        <div class="item-primary">{{ p['name'] }}</div>
                        <div class="item-secondary">
                            {{ p['location'] or '-' }}
                        </div>
                    </td>
                    <td>{{ p['customer'] or '-' }}</td>
                    <td>{{ p['start_date'] or '-' }}</td>
                    <td>{{ p['end_date'] or '-' }}</td>
                    <td>{{ "{:,.2f}".format(p['budget']) }}</td>
                    <td>
                        <span class="badge badge-draft">
                            {{ p['status'] }}
                        </span>
                        <div style="margin-top:7px">
                            {{ p['progress'] }}% complete
                        </div>
                    </td>
                    <td>
                        <form method="post"
                              action="{{ url_for(
                                  'update_project',
                                  project_id=p['id']
                              ) }}">
                            <select name="status" required>
                                {% for s in statuses %}
                                <option value="{{ s }}"
                                    {{ 'selected' if s == p['status'] else '' }}>
                                    {{ s }}
                                </option>
                                {% endfor %}
                            </select>
                            <label>Progress (%)</label>
                            <input type="number" name="progress"
                                   min="0" max="100"
                                   value="{{ p['progress'] }}" required>
                            <button class="btn btn-small"
                                    style="margin-top:8px"
                                    type="submit">
                                Save
                            </button>
                        </form>
                    </td>
                </tr>
            {% else %}
                <tr>
                    <td colspan="8" class="empty">
                        No projects found. Create your first project.
                    </td>
                </tr>
            {% endfor %}
            </tbody>
        </table>
        </div>
    </section>
    """,
    page_title="Projects",
    active="projects",
    rows=rows,
    search=search,
    total=total,
    active_count=active_count,
    completed_count=completed_count,
    statuses=PROJECT_STATUSES)


@app.route("/projects/add", methods=["GET", "POST"])
def add_project():
    if request.method == "POST":
        project_code = request.form.get(
            "project_code", ""
        ).strip().upper()
        name = request.form.get("name", "").strip()
        customer = request.form.get("customer", "").strip()
        location = request.form.get("location", "").strip()
        start_date = request.form.get("start_date", "").strip()
        end_date = request.form.get("end_date", "").strip()
        description = request.form.get(
            "description", ""
        ).strip()

        try:
            budget = float(request.form.get("budget", "0"))

            if not project_code or not name:
                raise ValueError(
                    "Project code and project name are required."
                )

            if budget < 0:
                raise ValueError("Budget cannot be negative.")

            if start_date and end_date and end_date < start_date:
                raise ValueError(
                    "End date cannot be earlier than start date."
                )

            with get_db() as conn:
                conn.execute("""
                    INSERT INTO projects (
                        project_code, name, customer, location,
                        start_date, end_date, budget, description
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    project_code, name, customer, location,
                    start_date, end_date, budget, description
                ))

            flash("Project created successfully.")
            return redirect(url_for("projects"))

        except ValueError as exc:
            flash(str(exc), "error")
        except sqlite3.IntegrityError:
            flash(
                "This project code already exists. "
                "Please use a unique code.",
                "error"
            )

    return page("""
    <div class="page-heading">
        <div>
            <h2>Create New Project</h2>
            <p>Enter the project details below.</p>
        </div>
        <a class="btn btn-secondary"
           href="{{ url_for('projects') }}">
            Back to Projects
        </a>
    </div>

    <section class="card">
        <div class="card-head">
            <h3>Project Information</h3>
        </div>

        <form method="post">
            <div class="form-grid">
                <div>
                    <label>Project Code *</label>
                    <input name="project_code" required
                           placeholder="e.g. PRJ-0001"
                           value="{{ request.form.get(
                               'project_code', ''
                           ) }}">
                </div>

                <div>
                    <label>Project Name *</label>
                    <input name="name" required
                           placeholder="Enter project name"
                           value="{{ request.form.get('name', '') }}">
                </div>

                <div>
                    <label>Customer / Client</label>
                    <input name="customer"
                           value="{{ request.form.get('customer', '') }}">
                </div>

                <div>
                    <label>Project Location</label>
                    <input name="location"
                           value="{{ request.form.get('location', '') }}">
                </div>

                <div>
                    <label>Start Date</label>
                    <input type="date" name="start_date"
                           value="{{ request.form.get('start_date', '') }}">
                </div>

                <div>
                    <label>End Date</label>
                    <input type="date" name="end_date"
                           value="{{ request.form.get('end_date', '') }}">
                </div>

                <div>
                    <label>Budget</label>
                    <input type="number" name="budget"
                           min="0" step="0.01" value="0">
                </div>

                <div class="form-full">
                    <label>Description / Notes</label>
                    <textarea name="description"
                              placeholder="Project scope and details">{{ request.form.get('description', '') }}</textarea>
                </div>
            </div>

            <p class="footer-note">
                New projects start with Planned status and 0% progress.
            </p>
            <button class="btn" type="submit">
                Save Project
            </button>
        </form>
    </section>
    """,
    page_title="Create Project",
    active="projects")


@app.route("/projects/<int:project_id>/update",
           methods=["POST"])
def update_project(project_id):
    status = request.form.get("status", "").strip()

    try:
        if status not in PROJECT_STATUSES:
            raise ValueError("Please select a valid project status.")

        progress_value = request.form.get("progress", "").strip()
        if not progress_value:
            raise ValueError("Progress is required.")

        try:
            progress = int(progress_value)
        except ValueError:
            raise ValueError("Progress must be a whole number between 0 and 100.")

        if not 0 <= progress <= 100:
            raise ValueError("Progress must be between 0 and 100.")

        if status == "Completed":
            progress = 100

        with get_db() as conn:
            result = conn.execute("""
                UPDATE projects
                SET status = ?, progress = ?
                WHERE id = ?
            """, (status, progress, project_id))

            if result.rowcount == 0:
                flash("Project not found.", "error")
            else:
                flash("Project status and progress updated.")

    except ValueError as exc:
        flash(str(exc), "error")

    return redirect(url_for("projects"))


@app.route("/projects/<int:project_id>", methods=["GET"])
def project_details(project_id):
    with get_db() as conn:
        project = conn.execute(
            "SELECT * FROM projects WHERE id = ?",
            (project_id,)
        ).fetchone()

    if project is None:
        return "Project not found", 404

    content = """
    <div class="card">
        <h2>Project Details</h2>

        <p><strong>Project Code:</strong>
        {{ project['project_code'] }}</p>

        <p><strong>Project Name:</strong>
        {{ project['name'] }}</p>

        <p><strong>Customer:</strong>
        {{ project['customer'] }}</p>

        <p><strong>Location:</strong>
        {{ project['location'] }}</p>

        <p><strong>Start Date:</strong>
        {{ project['start_date'] }}</p>

        <p><strong>End Date:</strong>
        {{ project['end_date'] }}</p>

        <p><strong>Budget:</strong>
        {{ money(project['budget']) }}</p>

        <p><strong>Status:</strong>
        {{ project['status'] }}</p>

        <p><strong>Progress:</strong>
        {{ project['progress'] }}%</p>

        <p><strong>Description:</strong>
        {{ project['description'] }}</p>

        <a href="{{ url_for('projects') }}">Back to Projects</a>
    </div>
    """

    return page(
        content,
        page_title="Project Details",
        active="projects",
        project=project,
        money=money
    )


# --------------------------------------------------
# REPORTS & ANALYTICS
# --------------------------------------------------

@app.route("/reports", methods=["GET"])
def reports():
    """Read-only reports with optional date filters."""
    from_date = request.args.get("from_date", "").strip()
    to_date = request.args.get("to_date", "").strip()

    # Validate date strings before they are used in SQL filters.
    try:
        if from_date:
            datetime.strptime(from_date, "%Y-%m-%d")
        if to_date:
            datetime.strptime(to_date, "%Y-%m-%d")
        if from_date and to_date and from_date > to_date:
            raise ValueError("Start date cannot be after end date.")
    except ValueError:
        flash("Please select valid dates and make sure the start date is not after the end date.", "error")
        return redirect(url_for("reports"))

    with get_db() as conn:
        # Current stock snapshot (not date-dependent).
        stock_rows = conn.execute("""
            SELECT item_code, name, category, stock_qty, unit, cost_price,
                   (COALESCE(stock_qty, 0) * COALESCE(cost_price, 0)) AS stock_value,
                   min_stock
            FROM products
            ORDER BY name
        """).fetchall()

        stock_summary = conn.execute("""
            SELECT COUNT(*) AS product_count,
                   COALESCE(SUM(stock_qty), 0) AS stock_units,
                   COALESCE(SUM(COALESCE(stock_qty, 0) * COALESCE(cost_price, 0)), 0) AS inventory_value,
                   COALESCE(SUM(CASE WHEN stock_qty <= min_stock THEN 1 ELSE 0 END), 0) AS low_stock_count
            FROM products
        """).fetchone()

        movement_rows = conn.execute("""
            SELECT m.created_at, m.movement_type, m.quantity, m.reference, m.notes,
                   p.item_code, p.name, p.unit
            FROM stock_movements m
            JOIN products p ON p.id = m.product_id
            WHERE (? = '' OR date(m.created_at) >= date(?))
              AND (? = '' OR date(m.created_at) <= date(?))
            ORDER BY m.id DESC LIMIT 100
        """, (from_date, from_date, to_date, to_date)).fetchall()

        issuance_rows = conn.execute("""
            SELECT mi.created_at, mi.reference, p.item_code, p.name, p.unit,
                   mi.quantity, mi.issued_to, mi.department, mi.notes
            FROM material_issuances mi
            JOIN products p ON p.id = mi.product_id
            WHERE (? = '' OR date(mi.created_at) >= date(?))
              AND (? = '' OR date(mi.created_at) <= date(?))
            ORDER BY mi.id DESC LIMIT 100
        """, (from_date, from_date, to_date, to_date)).fetchall()

        purchase_rows = conn.execute("""
            SELECT po.id, po.order_date, po.status, po.grn_reference,
                   s.name AS supplier_name,
                   COALESCE(SUM(pol.quantity * pol.unit_price), 0) AS total,
                   COUNT(pol.id) AS line_count
            FROM purchase_orders po
            JOIN suppliers s ON s.id = po.supplier_id
            LEFT JOIN purchase_order_lines pol ON pol.purchase_order_id = po.id
            WHERE (? = '' OR date(po.order_date) >= date(?))
              AND (? = '' OR date(po.order_date) <= date(?))
            GROUP BY po.id
            ORDER BY po.id DESC LIMIT 100
        """, (from_date, from_date, to_date, to_date)).fetchall()

    return page("""
    <div class="page-heading">
      <div><h2>Reports &amp; Analytics</h2>
      <p>Review inventory valuation, stock transactions, material issues and purchasing.</p></div>
    </div>

    <section class="card">
      <div class="card-head"><h3>Report Date Range</h3></div>
      <form method="get" class="form-grid">
        <div><label>From Date</label><input type="date" name="from_date" value="{{ from_date }}"></div>
        <div><label>To Date</label><input type="date" name="to_date" value="{{ to_date }}"></div>
        <div class="form-full actions" style="margin-top:15px">
          <button class="btn" type="submit">Apply Date Filter</button>
          <a class="btn btn-secondary" href="{{ url_for('reports') }}">Clear Dates</a>
        </div>
      </form>
      <p class="footer-note">The date range applies to stock movements, material issuance and purchase orders. Current stock and valuation are live snapshots.</p>
    </section>

    <div class="grid">
      <div class="stat-card"><div class="stat-label">Products</div><div class="stat-value">{{ stock_summary['product_count'] }}</div></div>
      <div class="stat-card"><div class="stat-label">Total Stock Units</div><div class="stat-value">{{ "{:,.2f}".format(stock_summary['stock_units'] or 0) }}</div></div>
      <div class="stat-card"><div class="stat-label">Inventory Value</div><div class="stat-value">{{ "{:,.2f}".format(stock_summary['inventory_value'] or 0) }}</div></div>
      <div class="stat-card"><div class="stat-label">Low Stock Items</div><div class="stat-value">{{ stock_summary['low_stock_count'] }}</div></div>
    </div>

    <section class="card">
      <div class="card-head"><div><h3>Stock Valuation Report</h3><div class="muted small">Current quantity multiplied by cost price</div></div>
        <a class="btn btn-secondary btn-small" href="{{ url_for('export_report', report_type='stock') }}">Export to Excel (CSV)</a></div>
      <div class="table-wrap"><table><thead><tr><th>Item Code</th><th>Description</th><th>Category</th><th>Quantity</th><th>UOM</th><th>Cost Price</th><th>Stock Value</th><th>Minimum</th></tr></thead><tbody>
      {% for r in stock_rows %}<tr><td class="item-primary">{{ r['item_code'] }}</td><td>{{ r['name'] }}</td><td>{{ r['category'] or '-' }}</td><td>{{ "{:,.2f}".format(r['stock_qty'] or 0) }}</td><td>{{ r['unit'] or '' }}</td><td>{{ "{:,.2f}".format(r['cost_price'] or 0) }}</td><td>{{ "{:,.2f}".format(r['stock_value'] or 0) }}</td><td>{{ "{:,.2f}".format(r['min_stock'] or 0) }}</td></tr>
      {% else %}<tr><td colspan="8" class="empty">No products found.</td></tr>{% endfor %}
      </tbody></table></div>
    </section>

    <section class="card">
      <div class="card-head"><div><h3>Stock Movement Report</h3><div class="muted small">Latest 100 matching IN / OUT transactions</div></div>
        <a class="btn btn-secondary btn-small" href="{{ url_for('export_report', report_type='movements', from_date=from_date, to_date=to_date) }}">Export to Excel (CSV)</a></div>
      <div class="table-wrap"><table><thead><tr><th>Date</th><th>Item Code</th><th>Description</th><th>Type</th><th>Quantity</th><th>Reference</th><th>Notes</th></tr></thead><tbody>
      {% for r in movement_rows %}<tr><td>{{ r['created_at'] }}</td><td>{{ r['item_code'] }}</td><td>{{ r['name'] }}</td><td><span class="badge {{ 'badge-in' if r['movement_type'] == 'IN' else 'badge-out' }}">{{ r['movement_type'] }}</span></td><td>{{ r['quantity'] }} {{ r['unit'] or '' }}</td><td>{{ r['reference'] or '-' }}</td><td>{{ r['notes'] or '-' }}</td></tr>
      {% else %}<tr><td colspan="7" class="empty">No matching stock movements.</td></tr>{% endfor %}
      </tbody></table></div>
    </section>

    <section class="card">
      <div class="card-head"><div><h3>Material Issuance Report</h3><div class="muted small">Latest 100 matching material issue records</div></div>
        <a class="btn btn-secondary btn-small" href="{{ url_for('export_report', report_type='issuance', from_date=from_date, to_date=to_date) }}">Export to Excel (CSV)</a></div>
      <div class="table-wrap"><table><thead><tr><th>Date</th><th>Issue Reference</th><th>Item Code</th><th>Description</th><th>Quantity</th><th>Issued To</th><th>Department / Project</th></tr></thead><tbody>
      {% for r in issuance_rows %}<tr><td>{{ r['created_at'] }}</td><td>{{ r['reference'] }}</td><td>{{ r['item_code'] }}</td><td>{{ r['name'] }}</td><td>{{ r['quantity'] }} {{ r['unit'] or '' }}</td><td>{{ r['issued_to'] }}</td><td>{{ r['department'] or '-' }}</td></tr>
      {% else %}<tr><td colspan="7" class="empty">No matching material issuance records.</td></tr>{% endfor %}
      </tbody></table></div>
    </section>

    <section class="card">
      <div class="card-head"><div><h3>Purchase Report</h3><div class="muted small">Latest 100 matching purchase orders</div></div>
        <a class="btn btn-secondary btn-small" href="{{ url_for('export_report', report_type='purchase_orders', from_date=from_date, to_date=to_date) }}">Export to Excel (CSV)</a></div>
      <div class="table-wrap"><table><thead><tr><th>PO Number</th><th>Order Date</th><th>Supplier</th><th>Lines</th><th>Status</th><th>Total Amount</th><th>GRN</th></tr></thead><tbody>
      {% for r in purchase_rows %}<tr><td>PO-{{ "%04d"|format(r['id']) }}</td><td>{{ r['order_date'] }}</td><td>{{ r['supplier_name'] }}</td><td>{{ r['line_count'] }}</td><td>{{ r['status'] }}</td><td>{{ "{:,.2f}".format(r['total'] or 0) }}</td><td>{{ r['grn_reference'] or '-' }}</td></tr>
      {% else %}<tr><td colspan="7" class="empty">No matching purchase orders.</td></tr>{% endfor %}
      </tbody></table></div>
    </section>
    <p class="footer-note">Exports are CSV files that open in Microsoft Excel and other spreadsheet applications. Reports do not change stock or purchase records.</p>
    """, page_title="Reports & Analytics", active="reports",
        from_date=from_date, to_date=to_date, stock_rows=stock_rows,
        stock_summary=stock_summary, movement_rows=movement_rows,
        issuance_rows=issuance_rows, purchase_rows=purchase_rows)


@app.route("/reports/export/<report_type>", methods=["GET"])
def export_report(report_type):
    """Export report rows as UTF-8 CSV, which Excel can open directly."""
    from_date = request.args.get("from_date", "").strip()
    to_date = request.args.get("to_date", "").strip()
    try:
        if from_date:
            datetime.strptime(from_date, "%Y-%m-%d")
        if to_date:
            datetime.strptime(to_date, "%Y-%m-%d")
        if from_date and to_date and from_date > to_date:
            raise ValueError
    except ValueError:
        flash("Please select a valid date range before exporting.", "error")
        return redirect(url_for("reports"))

    with get_db() as conn:
        if report_type == "stock":
            headers = ["Item Code", "Description", "Category", "Quantity", "UOM", "Cost Price", "Stock Value", "Minimum Stock"]
            rows = conn.execute("""
                SELECT item_code, name, category, stock_qty, unit, cost_price,
                       COALESCE(stock_qty, 0) * COALESCE(cost_price, 0) AS stock_value,
                       min_stock FROM products ORDER BY name
            """).fetchall()
            filename = "stock_valuation_report.csv"
        elif report_type == "movements":
            headers = ["Date", "Item Code", "Description", "Movement Type", "Quantity", "UOM", "Reference", "Notes"]
            rows = conn.execute("""
                SELECT m.created_at, p.item_code, p.name, m.movement_type,
                       m.quantity, p.unit, m.reference, m.notes
                FROM stock_movements m JOIN products p ON p.id = m.product_id
                WHERE (? = '' OR date(m.created_at) >= date(?))
                  AND (? = '' OR date(m.created_at) <= date(?))
                ORDER BY m.id DESC
            """, (from_date, from_date, to_date, to_date)).fetchall()
            filename = "stock_movement_report.csv"
        elif report_type == "issuance":
            headers = ["Date", "Issue Reference", "Item Code", "Description", "Quantity", "UOM", "Issued To", "Department / Project", "Notes"]
            rows = conn.execute("""
                SELECT mi.created_at, mi.reference, p.item_code, p.name,
                       mi.quantity, p.unit, mi.issued_to, mi.department, mi.notes
                FROM material_issuances mi JOIN products p ON p.id = mi.product_id
                WHERE (? = '' OR date(mi.created_at) >= date(?))
                  AND (? = '' OR date(mi.created_at) <= date(?))
                ORDER BY mi.id DESC
            """, (from_date, from_date, to_date, to_date)).fetchall()
            filename = "material_issuance_report.csv"
        elif report_type == "purchase_orders":
            headers = ["PO Number", "Order Date", "Supplier", "Line Count", "Status", "Total Amount", "GRN Reference"]
            rows = conn.execute("""
                SELECT po.id, po.order_date, s.name,
                       COUNT(pol.id), po.status,
                       COALESCE(SUM(pol.quantity * pol.unit_price), 0),
                       po.grn_reference
                FROM purchase_orders po JOIN suppliers s ON s.id = po.supplier_id
                LEFT JOIN purchase_order_lines pol ON pol.purchase_order_id = po.id
                WHERE (? = '' OR date(po.order_date) >= date(?))
                  AND (? = '' OR date(po.order_date) <= date(?))
                GROUP BY po.id ORDER BY po.id DESC
            """, (from_date, from_date, to_date, to_date)).fetchall()
            filename = "purchase_order_report.csv"
        else:
            flash("Unknown report type.", "error")
            return redirect(url_for("reports"))

    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(headers)
    for row in rows:
        values = list(row)
        if report_type == "purchase_orders":
            values[0] = f"PO-{int(values[0]):04d}"
        writer.writerow(values)

    # UTF-8 BOM helps Excel correctly recognize non-ASCII text.
    csv_data = "\ufeff" + output.getvalue()
    return Response(
        csv_data,
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# --------------------------------------------------

# START APPLICATION

# --------------------------------------------------

if __name__ == "__main__":

    init_db()

    init_material_issuance_db()

    app.run(debug=app.config["DEBUG"])
