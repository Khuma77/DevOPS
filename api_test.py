#!/usr/bin/env python3
"""
API Test Script for Agro Shop
Bu script API endpointlarini test qilish uchun
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health():
    """Health check test"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_metrics():
    """Metrics endpoint test"""
    print("📊 Testing metrics endpoint...")
    response = requests.get(f"{BASE_URL}/metrics")
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print("Metrics data available ✓")
    print()

def test_products_api():
    """Products API test"""
    print("🛍️ Testing Products API...")
    
    # Get all products
    response = requests.get(f"{BASE_URL}/api/v1/products")
    print(f"GET /products - Status: {response.status_code}")
    products = response.json()
    print(f"Products count: {len(products)}")
    
    # Create new product
    new_product = {
        "name": "Test Mahsulot",
        "price": 25.99
    }
    response = requests.post(f"{BASE_URL}/api/v1/products", json=new_product)
    print(f"POST /products - Status: {response.status_code}")
    if response.status_code == 201:
        created_product = response.json()
        product_id = created_product['id']
        print(f"Created product ID: {product_id}")
        
        # Get single product
        response = requests.get(f"{BASE_URL}/api/v1/products/{product_id}")
        print(f"GET /products/{product_id} - Status: {response.status_code}")
        
        # Update product
        updated_data = {"name": "Updated Test Mahsulot", "price": 30.99}
        response = requests.put(f"{BASE_URL}/api/v1/products/{product_id}", json=updated_data)
        print(f"PUT /products/{product_id} - Status: {response.status_code}")
        
        # Delete product
        response = requests.delete(f"{BASE_URL}/api/v1/products/{product_id}")
        print(f"DELETE /products/{product_id} - Status: {response.status_code}")
    
    print()

def test_orders_api():
    """Orders API test"""
    print("📦 Testing Orders API...")
    
    # Get all orders
    response = requests.get(f"{BASE_URL}/api/v1/orders")
    print(f"GET /orders - Status: {response.status_code}")
    orders = response.json()
    print(f"Orders count: {len(orders)}")
    
    # Create test order (assuming product ID 1 exists)
    new_order = {
        "customer_name": "Test Customer",
        "phone": "+998901234567",
        "address": "Test Address, Tashkent",
        "items": [
            {"product_id": 1, "quantity": 2}
        ]
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/orders", json=new_order)
    print(f"POST /orders - Status: {response.status_code}")
    if response.status_code == 201:
        created_order = response.json()
        order_id = created_order['id']
        print(f"Created order ID: {order_id}")
        
        # Get single order
        response = requests.get(f"{BASE_URL}/api/v1/orders/{order_id}")
        print(f"GET /orders/{order_id} - Status: {response.status_code}")
    
    print()

def test_stats_api():
    """Statistics API test"""
    print("📈 Testing Statistics API...")
    response = requests.get(f"{BASE_URL}/api/v1/stats")
    print(f"GET /stats - Status: {response.status_code}")
    if response.status_code == 200:
        stats = response.json()
        print(f"Statistics: {json.dumps(stats, indent=2)}")
    print()

def load_test():
    """Simple load test"""
    print("⚡ Running load test (10 requests)...")
    start_time = time.time()
    
    for i in range(10):
        response = requests.get(f"{BASE_URL}/api/v1/products")
        print(f"Request {i+1}: {response.status_code}")
        time.sleep(0.1)
    
    end_time = time.time()
    print(f"Load test completed in {end_time - start_time:.2f} seconds")
    print()

if __name__ == "__main__":
    print("🚀 Starting API Tests for Agro Shop")
    print("=" * 50)
    
    try:
        test_health()
        test_metrics()
        test_products_api()
        test_orders_api()
        test_stats_api()
        load_test()
        
        print("✅ All tests completed!")
        print("\n📊 Now check Grafana dashboard at: http://localhost:3000")
        print("👤 Login: admin / admin123")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection error! Make sure the Flask app is running on port 5000")
    except Exception as e:
        print(f"❌ Error: {e}")