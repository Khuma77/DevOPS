from flask import Blueprint, render_template, request, redirect, session
from database import db

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = db()
        admin = conn.execute(
            "SELECT * FROM admin WHERE username=? AND password=?",
            (username, password)
        ).fetchone()

        if admin:
            session["admin"] = True
            return redirect("/admin/dashboard")
        else:
            return "Invalid login"

    return render_template("admin_login.html")


@admin_bp.route("/admin/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect("/admin/login")

    return render_template("admin_dashboard.html")


@admin_bp.route("/admin/orders")
def admin_orders():
    if not session.get("admin"):
        return redirect("/admin/login")

    conn = db()
    orders = conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    return render_template("admin_orders.html", orders=orders)
