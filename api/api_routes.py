from flask import Blueprint, jsonify, request
from database import db
import datetime
from prometheus_client import Counter, Histogram, Gauge
import time
import logging

# Prometheus metrics
api_requests_total = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
api_request_duration = Histogram('api_request_duration_seconds', 'API request duration')
active_orders = Gauge('active_orders_total', 'Total active orders')
products_count = Gauge('products_count_total', 'Total products count')

# Custom business metrics
database_operations_total = Counter('database_operations_total', 'Total database operations', ['operation', 'table'])
order_value_histogram = Histogram('order_value_dollars', 'Order value distribution')
user_sessions_active = Gauge('user_sessions_active', 'Active user sessions')
cart_items_total = Counter('cart_items_total', 'Total items added to cart')
checkout_success_total = Counter('checkout_success_total', 'Successful checkouts')
checkout_failure_total = Counter('checkout_failure_total', 'Failed checkouts', ['reason'])

# Setup logging for Loki
logger = logging.getLogger('api')

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


def track_metrics(endpoint):
    def decorator(f):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            method = request.method

            try:
                result = f(*args, **kwargs)
                status = '200'
                api_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
                logger.info(f"API call successful: {method} {endpoint}")
                return result
            except Exception as e:
                status = '500'
                api_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
                logger.error(f"API call failed: {method} {endpoint} - {str(e)}")
                return jsonify({"error": str(e)}), 500
            finally:
                duration = time.time() - start_time
                api_request_duration.observe(duration)

        wrapper.__name__ = f.__name__
        return wrapper
    return decorator


# ==================== PRODUCTS API ====================

@api_bp.route('/products', methods=['GET'])
@track_metrics('/products')
def get_products():
    """Get all products"""
    conn = db()
    products = conn.execute("SELECT * FROM products").fetchall()
    
    # Track database operation
    database_operations_total.labels(operation='SELECT', table='products').inc()

    # Update metrics
    products_count.set(len(products))

    return jsonify([{
        "id": p["id"],
        "name": p["name"],
        "price": float(p["price"])
    } for p in products])


@api_bp.route('/products/<int:product_id>', methods=['GET'])
@track_metrics('/products/<id>')
def get_product(product_id):
    """Get single product"""
    conn = db()
    product = conn.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()

    if not product:
        return jsonify({"error": "Product not found"}), 404

    return jsonify({
        "id": product["id"],
        "name": product["name"],
        "price": float(product["price"])
    })


@api_bp.route('/products', methods=['POST'])
@track_metrics('/products')
def create_product():
    """Create new product"""
    data = request.get_json()

    if not data or 'name' not in data or 'price' not in data:
        return jsonify({"error": "Name and price required"}), 400

    conn = db()
    cursor = conn.execute(
        "INSERT INTO products(name, price) VALUES (?, ?)",
        (data['name'], float(data['price']))
    )
    conn.commit()
    
    # Track database operation
    database_operations_total.labels(operation='INSERT', table='products').inc()

    return jsonify({
        "id": cursor.lastrowid,
        "name": data['name'],
        "price": float(data['price'])
    }), 201


@api_bp.route('/products/<int:product_id>', methods=['PUT'])
@track_metrics('/products/<id>')
def update_product(product_id):
    """Update product"""
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON data required"}), 400

    conn = db()

    # Check if product exists
    product = conn.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
    if not product:
        return jsonify({"error": "Product not found"}), 404

    # Update fields
    name = data.get('name', product['name'])
    price = data.get('price', product['price'])

    conn.execute(
        "UPDATE products SET name=?, price=? WHERE id=?",
        (name, float(price), product_id)
    )
    conn.commit()

    return jsonify({
        "id": product_id,
        "name": name,
        "price": float(price)
    })


@api_bp.route('/products/<int:product_id>', methods=['DELETE'])
@track_metrics('/products/<id>')
def delete_product(product_id):
    """Delete product"""
    conn = db()

    # Check if product exists
    product = conn.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
    if not product:
        return jsonify({"error": "Product not found"}), 404

    conn.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()

    return jsonify({"message": "Product deleted successfully"})


# ==================== ORDERS API ====================

@api_bp.route('/orders', methods=['GET'])
@track_metrics('/orders')
def get_orders():
    """Get all orders"""
    conn = db()
    orders = conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()

    # Update metrics
    active_orders.set(len(orders))

    result = []
    for order in orders:
        # Get order items
        items = conn.execute(
            "SELECT * FROM order_items WHERE order_id=?",
            (order["id"],)
        ).fetchall()

        result.append({
            "id": order["id"],
            "customer_name": order["customer_name"],
            "phone": order["phone"],
            "address": order["address"],
            "total": float(order["total"]),
            "created_at": order["created_at"],
            "items": [{
                "product_name": item["product_name"],
                "quantity": item["quantity"],
                "price": float(item["price"]),
                "subtotal": float(item["subtotal"])
            } for item in items]
        })

    return jsonify(result)


@api_bp.route('/orders/<int:order_id>', methods=['GET'])
@track_metrics('/orders/<id>')
def get_order(order_id):
    """Get single order"""
    conn = db()
    order = conn.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()

    if not order:
        return jsonify({"error": "Order not found"}), 404

    # Get order items
    items = conn.execute(
        "SELECT * FROM order_items WHERE order_id=?",
        (order_id,)
    ).fetchall()

    return jsonify({
        "id": order["id"],
        "customer_name": order["customer_name"],
        "phone": order["phone"],
        "address": order["address"],
        "total": float(order["total"]),
        "created_at": order["created_at"],
        "items": [{
            "product_name": item["product_name"],
            "quantity": item["quantity"],
            "price": float(item["price"]),
            "subtotal": float(item["subtotal"])
        } for item in items]
    })


@api_bp.route('/orders', methods=['POST'])
@track_metrics('/orders')
def create_order():
    """Create new order"""
    data = request.get_json()

    required_fields = ['customer_name', 'phone', 'address', 'items']
    if not data or not all(field in data for field in required_fields):
        checkout_failure_total.labels(reason='missing_fields').inc()
        return jsonify({"error": "Required fields: customer_name, phone, address, items"}), 400

    if not data['items']:
        checkout_failure_total.labels(reason='empty_cart').inc()
        return jsonify({"error": "Order must have at least one item"}), 400

    conn = db()
    total = 0

    # Calculate total and validate products
    for item in data['items']:
        if 'product_id' not in item or 'quantity' not in item:
            checkout_failure_total.labels(reason='invalid_item_format').inc()
            return jsonify({"error": "Each item must have product_id and quantity"}), 400

        product = conn.execute("SELECT * FROM products WHERE id=?", (item['product_id'],)).fetchone()
        if not product:
            checkout_failure_total.labels(reason='product_not_found').inc()
            return jsonify({"error": f"Product {item['product_id']} not found"}), 404

        subtotal = product['price'] * item['quantity']
        total += subtotal

    # Track order value
    order_value_histogram.observe(total)

    # Create order
    cursor = conn.execute("""
        INSERT INTO orders(customer_name, phone, address, total, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (data['customer_name'], data['phone'], data['address'], total,
          datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    order_id = cursor.lastrowid
    
    # Track database operations
    database_operations_total.labels(operation='INSERT', table='orders').inc()

    # Create order items
    for item in data['items']:
        product = conn.execute("SELECT * FROM products WHERE id=?", (item['product_id'],)).fetchone()
        subtotal = product['price'] * item['quantity']

        conn.execute("""
            INSERT INTO order_items(order_id, product_name, quantity, price, subtotal)
            VALUES (?, ?, ?, ?, ?)
        """, (order_id, product['name'], item['quantity'], product['price'], subtotal))
        
        database_operations_total.labels(operation='INSERT', table='order_items').inc()

    conn.commit()
    
    # Track successful checkout
    checkout_success_total.inc()

    return jsonify({
        "id": order_id,
        "customer_name": data['customer_name'],
        "phone": data['phone'],
        "address": data['address'],
        "total": total,
        "message": "Order created successfully"
    }), 201


# ==================== STATISTICS API ====================

@api_bp.route('/stats', methods=['GET'])
@track_metrics('/stats')
def get_stats():
    """Get application statistics"""
    conn = db()

    # Get counts
    products_count_db = conn.execute("SELECT COUNT(*) as count FROM products").fetchone()['count']
    orders_count = conn.execute("SELECT COUNT(*) as count FROM orders").fetchone()['count']
    total_revenue = conn.execute("SELECT SUM(total) as revenue FROM orders").fetchone()['revenue'] or 0

    # Get recent orders (last 7 days)
    recent_orders = conn.execute("""
        SELECT COUNT(*) as count FROM orders
        WHERE created_at >= datetime('now', '-7 days')
    """).fetchone()['count']

    return jsonify({
        "products_count": products_count_db,
        "orders_count": orders_count,
        "total_revenue": float(total_revenue),
        "recent_orders": recent_orders,
        "timestamp": datetime.datetime.now().isoformat()
    })