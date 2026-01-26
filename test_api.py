#!/usr/bin/env python3
"""
Unit tests for Agro Shop API
"""

import pytest
import json
import tempfile
import os
from app import app
from database import create_tables, db

@pytest.fixture
def client():
    """Create test client"""
    # Create temporary database
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        with app.app_context():
            create_tables()
        yield client
    
    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

def test_health_endpoint(client):
    """Test health endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'

def test_metrics_endpoint(client):
    """Test metrics endpoint"""
    response = client.get('/metrics')
    assert response.status_code == 200
    assert 'text/plain' in response.content_type

def test_get_products_empty(client):
    """Test getting products when database is empty"""
    response = client.get('/api/v1/products')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 0

def test_create_product(client):
    """Test creating a new product"""
    product_data = {
        'name': 'Test Apple',
        'price': 2.50
    }
    response = client.post('/api/v1/products', 
                          data=json.dumps(product_data),
                          content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == 'Test Apple'
    assert data['price'] == 2.50
    assert 'id' in data

def test_create_product_invalid_data(client):
    """Test creating product with invalid data"""
    response = client.post('/api/v1/products', 
                          data=json.dumps({'name': 'Test'}),
                          content_type='application/json')
    assert response.status_code == 400

def test_get_product_not_found(client):
    """Test getting non-existent product"""
    response = client.get('/api/v1/products/999')
    assert response.status_code == 404

def test_product_crud_operations(client):
    """Test complete CRUD operations for products"""
    # Create
    product_data = {'name': 'Test Orange', 'price': 3.00}
    response = client.post('/api/v1/products', 
                          data=json.dumps(product_data),
                          content_type='application/json')
    assert response.status_code == 201
    product = json.loads(response.data)
    product_id = product['id']
    
    # Read
    response = client.get(f'/api/v1/products/{product_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'Test Orange'
    
    # Update
    update_data = {'name': 'Updated Orange', 'price': 3.50}
    response = client.put(f'/api/v1/products/{product_id}',
                         data=json.dumps(update_data),
                         content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'Updated Orange'
    assert data['price'] == 3.50
    
    # Delete
    response = client.delete(f'/api/v1/products/{product_id}')
    assert response.status_code == 200
    
    # Verify deletion
    response = client.get(f'/api/v1/products/{product_id}')
    assert response.status_code == 404

def test_create_order(client):
    """Test creating an order"""
    # First create a product
    product_data = {'name': 'Test Banana', 'price': 1.50}
    response = client.post('/api/v1/products', 
                          data=json.dumps(product_data),
                          content_type='application/json')
    product = json.loads(response.data)
    product_id = product['id']
    
    # Create order
    order_data = {
        'customer_name': 'John Doe',
        'phone': '+998901234567',
        'address': 'Test Address',
        'items': [{'product_id': product_id, 'quantity': 2}]
    }
    response = client.post('/api/v1/orders',
                          data=json.dumps(order_data),
                          content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['customer_name'] == 'John Doe'
    assert data['total'] == 3.00  # 1.50 * 2

def test_create_order_invalid_product(client):
    """Test creating order with non-existent product"""
    order_data = {
        'customer_name': 'John Doe',
        'phone': '+998901234567',
        'address': 'Test Address',
        'items': [{'product_id': 999, 'quantity': 2}]
    }
    response = client.post('/api/v1/orders',
                          data=json.dumps(order_data),
                          content_type='application/json')
    assert response.status_code == 404

def test_get_stats(client):
    """Test statistics endpoint"""
    response = client.get('/api/v1/stats')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'products_count' in data
    assert 'orders_count' in data
    assert 'total_revenue' in data
    assert 'recent_orders' in data

def test_web_routes(client):
    """Test web interface routes"""
    # Test main page
    response = client.get('/')
    assert response.status_code == 200
    
    # Test cart page
    response = client.get('/cart')
    assert response.status_code == 200
    
    # Test checkout page
    response = client.get('/checkout')
    assert response.status_code == 200

if __name__ == '__main__':
    pytest.main([__file__, '-v'])