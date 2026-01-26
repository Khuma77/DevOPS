from flask import Blueprint, render_template, request, redirect, session
from database import db

admin_products_bp = Blueprint("admin_products", __name__)


def admin_required():
    if not session.get("admin"):
        return False
    return True


# ---------------- PRODUCTS LIST ----------------
@admin_products_bp.route("/admin/products")
def products_list():
    if not admin_required():
        return redirect("/admin/login")

    conn = db()
    products = conn.execute("SELECT * FROM products").fetchall()

    return render_template("admin_products.html", products=products)


# ---------------- ADD PRODUCT ----------------
@admin_products_bp.route("/admin/products/add", methods=["GET", "POST"])
def add_product():
    if not admin_required():
        return redirect("/admin/login")

    if request.method == "POST":
        name = request.form["name"]
        price = float(request.form["price"])

        conn = db()
        conn.execute("INSERT INTO products(name, price) VALUES (?, ?)", (name, price))
        conn.commit()

        return redirect("/admin/products")

    return render_template("admin_add_product.html")


# ---------------- DELETE PRODUCT ----------------
@admin_products_bp.route("/admin/products/delete/<int:id>")
def delete_product(id):
    if not admin_required():
        return redirect("/admin/login")

    conn = db()
    conn.execute("DELETE FROM products WHERE id=?", (id,))
    conn.commit()

    return redirect("/admin/products")


# ---------------- EDIT PRODUCT ----------------
@admin_products_bp.route("/admin/products/edit/<int:id>", methods=["GET", "POST"])
def edit_product(id):
    if not admin_required():
        return redirect("/admin/login")

    conn = db()

    if request.method == "POST":
        name = request.form["name"]
        price = float(request.form["price"])

        conn.execute(
            "UPDATE products SET name=?, price=? WHERE id=?",
            (name, price, id)
        )
        conn.commit()
        return redirect("/admin/products")

    # GET → load product data
    product = conn.execute("SELECT * FROM products WHERE id=?", (id,)).fetchone()

    return render_template("admin_edit_product.html", product=product)
