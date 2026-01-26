from flask import Flask, render_template, redirect, request, session
from flask_cors import CORS
from database import create_tables, db
import datetime
import os
import logging

# Import logging configuration
from logging_config import setup_logging, get_logger

# Import API routes and monitoring
from api.api_routes import api_bp
from monitoring.metrics import metrics_bp

# Admin Panels
from admin.admin_controller import admin_bp
from admin.admin_products import admin_products_bp

# Setup logging
setup_logging()
logger = get_logger('main')

# Create logs directory
os.makedirs('logs', exist_ok=True)

app = Flask(__name__)
app.secret_key = "secret123"

# Enable CORS for API endpoints
CORS(app, resources={
    r"/api/*": {"origins": "*"},
    r"/metrics": {"origins": "*"},
    r"/health": {"origins": "*"}
})

# Create DB tables
create_tables()
logger.info("Database tables created successfully")

# Register blueprints
app.register_blueprint(api_bp)
app.register_blueprint(metrics_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(admin_products_bp)

logger.info("All blueprints registered successfully")


# --------------------------- PRODUCTS PAGE ---------------------------

@app.route("/")
def products():
    logger.info("Products page accessed")
    conn = db()
    products = conn.execute("SELECT * FROM products").fetchall()
    return render_template("products.html", products=products)


# --------------------------- CART SYSTEM ---------------------------

@app.route("/add/<int:product_id>")
def add_to_cart(product_id):
    logger.info(f"Product {product_id} added to cart")
    cart = session.get("cart", {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    session["cart"] = cart
    return redirect("/cart")


@app.route("/cart")
def cart():
    logger.info("Cart page accessed")
    cart = session.get("cart", {})
    conn = db()
    items = []
    total = 0

    for pid, qty in cart.items():
        product = conn.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
        subtotal = product["price"] * qty
        total += subtotal
        items.append({"product": product, "qty": qty, "subtotal": subtotal})

    return render_template("cart.html", items=items, total=total)


@app.route("/update/<int:pid>", methods=["POST"])
def update_qty(pid):
    logger.info(f"Cart quantity updated for product {pid}")
    qty = int(request.form["qty"])
    cart = session.get("cart", {})

    if qty <= 0:
        cart.pop(str(pid), None)
    else:
        cart[str(pid)] = qty

    session["cart"] = cart
    return redirect("/cart")


# --------------------------- CHECKOUT + SAVE ORDER ---------------------------

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    cart = session.get("cart", {})
    conn = db()

    if request.method == "POST":
        logger.info("New order being processed")
        
        name = request.form["name"]
        phone = request.form["phone"]
        address = request.form["address"]

        items = []
        total = 0

        for pid, qty in cart.items():
            product = conn.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
            subtotal = product["price"] * qty
            total += subtotal
            items.append((product["name"], qty, product["price"], subtotal))

        # Save order
        conn.execute("""
            INSERT INTO orders(customer_name, phone, address, total, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (name, phone, address, total, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()

        order_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        # Save order items
        for product_name, qty, price, subtotal in items:
            conn.execute("""
                INSERT INTO order_items(order_id, product_name, quantity, price, subtotal)
                VALUES (?, ?, ?, ?, ?)
            """, (order_id, product_name, qty, price, subtotal))
        conn.commit()

        # Clear cart
        session["cart"] = {}
        
        logger.info(f"Order {order_id} created successfully for customer {name}")
        return "Order placed successfully!"

    # GET (render checkout page)
    logger.info("Checkout page accessed")
    items = []
    total = 0

    for pid, qty in cart.items():
        product = conn.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
        subtotal = product["price"] * qty
        total += subtotal
        items.append({"product": product, "qty": qty, "subtotal": subtotal})

    return render_template("checkout.html", items=items, total=total)


# --------------------------- REGISTER ADMIN PANEL (2 blueprints) ---------------------------

app.register_blueprint(admin_bp)
app.register_blueprint(admin_products_bp)


# --------------------------- RUN APP ---------------------------

if __name__ == '__main__':
    logger.info("Starting Agro Shop application")
    app.run(host='0.0.0.0', port=5000, debug=True)

@app.route("/health")
def health():
    logger.info("Health check accessed")
    return {"status": "ok"}, 200

