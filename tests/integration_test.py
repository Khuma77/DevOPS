#!/usr/bin/env python3
"""
Integration tests for Agro Shop
Bu testlar to'liq application workflow'ni tekshiradi
"""

import requests
import json
import time
import pytest
import subprocess
import os

BASE_URL = os.getenv('TEST_URL', 'http://localhost:5000')

class TestIntegration:
    
    @classmethod
    def setup_class(cls):
        """Setup before all tests"""
        # Wait for application to be ready
        max_retries = 30
        for i in range(max_retries):
            try:
                response = requests.get(f"{BASE_URL}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ Application is ready after {i+1} attempts")
                    return
            except requests.exceptions.RequestException as e:
                print(f"⏳ Attempt {i+1}/{max_retries}: {e}")
                if i == max_retries - 1:
                    pytest.skip("❌ Application is not available for integration tests")
                time.sleep(2)
    
    def test_health_check(self):
        """Test application health"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert 'status' in data
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint"""
        response = requests.get(f"{BASE_URL}/metrics")
        assert response.status_code == 200
        assert 'text/plain' in response.headers.get('Content-Type', '')
    
    def test_complete_ecommerce_workflow(self):
        """Test complete e-commerce workflow"""
        
        # 1. Get initial products
        response = requests.get(f"{BASE_URL}/api/v1/products")
        assert response.status_code == 200
        initial_products = response.json()
        
        # 2. Create a new product
        new_product = {
            "name": "Integration Test Product",
            "price": 99.99
        }
        response = requests.post(f"{BASE_URL}/api/v1/products", json=new_product)
        assert response.status_code == 201
        created_product = response.json()
        product_id = created_product['id']
        
        # 3. Verify product was created
        response = requests.get(f"{BASE_URL}/api/v1/products/{product_id}")
        assert response.status_code == 200
        product = response.json()
        assert product['name'] == new_product['name']
        assert product['price'] == new_product['price']
        
        # 4. Create an order with the product
        order_data = {
            "customer_name": "Integration Test Customer",
            "phone": "+998901234567",
            "address": "Test Address, Tashkent",
            "items": [
                {"product_id": product_id, "quantity": 2}
            ]
        }
        response = requests.post(f"{BASE_URL}/api/v1/orders", json=order_data)
        assert response.status_code == 201
        created_order = response.json()
        order_id = created_order['id']
        assert created_order['total'] == 199.98  # 99.99 * 2
        
        # 5. Verify order was created
        response = requests.get(f"{BASE_URL}/api/v1/orders/{order_id}")
        assert response.status_code == 200
        order = response.json()
        assert order['customer_name'] == order_data['customer_name']
        assert len(order['items']) == 1
        assert order['items'][0]['quantity'] == 2
        
        # 6. Check statistics
        response = requests.get(f"{BASE_URL}/api/v1/stats")
        assert response.status_code == 200
        stats = response.json()
        assert stats['products_count'] >= len(initial_products) + 1
        assert stats['orders_count'] >= 1
        assert stats['total_revenue'] >= 199.98
        
        # 7. Update product
        update_data = {"name": "Updated Integration Test Product", "price": 149.99}
        response = requests.put(f"{BASE_URL}/api/v1/products/{product_id}", json=update_data)
        assert response.status_code == 200
        updated_product = response.json()
        assert updated_product['name'] == update_data['name']
        assert updated_product['price'] == update_data['price']
        
        # 8. Clean up - delete product
        response = requests.delete(f"{BASE_URL}/api/v1/products/{product_id}")
        assert response.status_code == 200
        
        # 9. Verify product was deleted
        response = requests.get(f"{BASE_URL}/api/v1/products/{product_id}")
        assert response.status_code == 404
    
    def test_error_handling(self):
        """Test error handling"""
        
        # Test invalid product creation
        invalid_product = {"name": "Test Product"}  # Missing price
        response = requests.post(f"{BASE_URL}/api/v1/products", json=invalid_product)
        assert response.status_code == 400
        
        # Test non-existent product
        response = requests.get(f"{BASE_URL}/api/v1/products/99999")
        assert response.status_code == 404
        
        # Test invalid order creation
        invalid_order = {
            "customer_name": "Test Customer",
            "items": [{"product_id": 99999, "quantity": 1}]  # Non-existent product
        }
        response = requests.post(f"{BASE_URL}/api/v1/orders", json=invalid_order)
        assert response.status_code in [400, 404]
    
    def test_web_interface(self):
        """Test web interface endpoints"""
        
        # Test main page
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        assert 'text/html' in response.headers.get('Content-Type', '')
        
        # Test cart page
        response = requests.get(f"{BASE_URL}/cart")
        assert response.status_code == 200
        
        # Test checkout page
        response = requests.get(f"{BASE_URL}/checkout")
        assert response.status_code == 200
    
    def test_performance(self):
        """Test basic performance"""
        
        # Test response times
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/api/v1/products")
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 2.0, f"Response time too slow: {response_time}s"
        
        # Test concurrent requests
        import concurrent.futures
        
        def make_request():
            return requests.get(f"{BASE_URL}/health")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        for result in results:
            assert result.status_code == 200
    
    def test_metrics_collection(self):
        """Test that metrics are being collected"""
        
        # Make some API calls to generate metrics
        requests.get(f"{BASE_URL}/api/v1/products")
        requests.get(f"{BASE_URL}/api/v1/stats")
        
        # Check metrics endpoint
        response = requests.get(f"{BASE_URL}/metrics")
        assert response.status_code == 200
        metrics_text = response.text
        
        # Verify custom metrics are present
        assert 'api_requests_total' in metrics_text
        assert 'api_request_duration_seconds' in metrics_text
        assert 'products_count_total' in metrics_text
        assert 'active_orders_total' in metrics_text

if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])