import sqlite3

def db():
    conn = sqlite3.connect("agro.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = db()

    # PRODUCTS
    conn.execute("""
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL
    );
    """)

    # ORDERS
    conn.execute("""
    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT,
        phone TEXT,
        address TEXT,
        total REAL,
        created_at TEXT
    );
    """)

    # ORDER ITEMS
    conn.execute("""
    CREATE TABLE IF NOT EXISTS order_items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        product_name TEXT,
        quantity INTEGER,
        price REAL,
        subtotal REAL
    );
    """)

    # ADMIN USER
    conn.execute("""
    CREATE TABLE IF NOT EXISTS admin(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    );
    """)

    # insert default admin (only once)
    count_admin = conn.execute("SELECT COUNT(*) FROM admin").fetchone()[0]
    if count_admin == 0:
        conn.execute("INSERT INTO admin(username, password) VALUES ('admin', '1234')")
        conn.commit()

    # insert demo products
    count_products = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    if count_products == 0:
        conn.execute("INSERT INTO products(name, price) VALUES ('Sabzi', 12000)")
        conn.execute("INSERT INTO products(name, price) VALUES ('Kartoshka', 10000)")
        conn.execute("INSERT INTO products(name, price) VALUES ('Qovun', 10050)")
        conn.execute("INSERT INTO products(name, price) VALUES ('Kalbasa', 10022)")
        conn.execute("INSERT INTO products(name, price) VALUES ('Tarvuz', 10031)")

        conn.commit()
