#!/usr/bin/env python3
"""
🔍 Agro Shop - Deployment Verification Script

This script performs comprehensive verification of the deployed Agro Shop application
including health checks, API validation, monitoring stack verification, and performance checks.
"""

import requests
import time
import json
import sys
import subprocess
import argparse
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import concurrent.futures

@dataclass
class VerificationResult:
    """Verification test result"""
    test_name: str
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None
    response_time: Optional[float] = None

class DeploymentVerifier:
    """Comprehensive deployment verification"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.results: List[VerificationResult] = []
        
    def add_result(self, result: VerificationResult):
        """Add verification result"""
        self.results.append(result)
        status = "✅" if result.success else "❌"
        time_info = f" ({result.response_time:.3f}s)" if result.response_time else ""
        print(f"{status} {result.test_name}{time_info}: {result.message}")
    
    def verify_health_endpoint(self) -> VerificationResult:
        """Verify application health endpoint"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=self.timeout)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                health_data = response.json()
                return VerificationResult(
                    test_name="Health Check",
                    success=True,
                    message="Application is healthy",
                    details=health_data,
                    response_time=response_time
                )
            else:
                return VerificationResult(
                    test_name="Health Check",
                    success=False,
                    message=f"Health check failed with status {response.status_code}",
                    response_time=response_time
                )
        except Exception as e:
            return VerificationResult(
                test_name="Health Check",
                success=False,
                message=f"Health check failed: {str(e)}"
            )
    
    def verify_api_endpoints(self) -> List[VerificationResult]:
        """Verify all API endpoints"""
        results = []
        
        # Test GET endpoints
        get_endpoints = [
            ("/api/v1/products", "Products API"),
            ("/api/v1/stats", "Statistics API"),
            ("/metrics", "Metrics endpoint")
        ]
        
        for endpoint, name in get_endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=self.timeout)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    results.append(VerificationResult(
                        test_name=name,
                        success=True,
                        message="Endpoint responding correctly",
                        response_time=response_time
                    ))
                else:
                    results.append(VerificationResult(
                        test_name=name,
                        success=False,
                        message=f"Endpoint returned status {response.status_code}",
                        response_time=response_time
                    ))
            except Exception as e:
                results.append(VerificationResult(
                    test_name=name,
                    success=False,
                    message=f"Endpoint failed: {str(e)}"
                ))
        
        return results
    
    def verify_database_connectivity(self) -> VerificationResult:
        """Verify database connectivity through API"""
        try:
            # Try to fetch products (requires database)
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/v1/products", timeout=self.timeout)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                products = response.json()
                return VerificationResult(
                    test_name="Database Connectivity",
                    success=True,
                    message=f"Database accessible, {len(products)} products found",
                    details={"product_count": len(products)},
                    response_time=response_time
                )
            else:
                return VerificationResult(
                    test_name="Database Connectivity",
                    success=False,
                    message=f"Database check failed with status {response.status_code}",
                    response_time=response_time
                )
        except Exception as e:
            return VerificationResult(
                test_name="Database Connectivity",
                success=False,
                message=f"Database check failed: {str(e)}"
            )
    
    def verify_api_functionality(self) -> List[VerificationResult]:
        """Verify API CRUD functionality"""
        results = []
        
        # Test product creation
        test_product = {
            "name": "Verification Test Product",
            "price": 99.99,
            "category": "Test",
            "stock": 1
        }
        
        try:
            # Create product
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/api/v1/products",
                json=test_product,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            response_time = time.time() - start_time
            
            if response.status_code == 201:
                created_product = response.json()
                product_id = created_product.get('id')
                
                results.append(VerificationResult(
                    test_name="API Create Product",
                    success=True,
                    message="Product creation successful",
                    details={"product_id": product_id},
                    response_time=response_time
                ))
                
                # Test product retrieval
                if product_id:
                    try:
                        start_time = time.time()
                        get_response = requests.get(
                            f"{self.base_url}/api/v1/products/{product_id}",
                            timeout=self.timeout
                        )
                        response_time = time.time() - start_time
                        
                        if get_response.status_code == 200:
                            results.append(VerificationResult(
                                test_name="API Get Product",
                                success=True,
                                message="Product retrieval successful",
                                response_time=response_time
                            ))
                        else:
                            results.append(VerificationResult(
                                test_name="API Get Product",
                                success=False,
                                message=f"Product retrieval failed with status {get_response.status_code}",
                                response_time=response_time
                            ))
                    except Exception as e:
                        results.append(VerificationResult(
                            test_name="API Get Product",
                            success=False,
                            message=f"Product retrieval failed: {str(e)}"
                        ))
                
                # Clean up - delete test product
                try:
                    requests.delete(f"{self.base_url}/api/v1/products/{product_id}", timeout=self.timeout)
                except:
                    pass  # Cleanup failure is not critical
                    
            else:
                results.append(VerificationResult(
                    test_name="API Create Product",
                    success=False,
                    message=f"Product creation failed with status {response.status_code}",
                    response_time=response_time
                ))
        except Exception as e:
            results.append(VerificationResult(
                test_name="API Create Product",
                success=False,
                message=f"Product creation failed: {str(e)}"
            ))
        
        return results
    
    def verify_performance(self) -> VerificationResult:
        """Verify basic performance requirements"""
        try:
            # Test response time for main page
            start_time = time.time()
            response = requests.get(f"{self.base_url}/", timeout=self.timeout)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                if response_time < 2.0:  # 2 second threshold
                    return VerificationResult(
                        test_name="Performance Check",
                        success=True,
                        message=f"Response time acceptable",
                        response_time=response_time
                    )
                else:
                    return VerificationResult(
                        test_name="Performance Check",
                        success=False,
                        message=f"Response time too slow (>{response_time:.3f}s)",
                        response_time=response_time
                    )
            else:
                return VerificationResult(
                    test_name="Performance Check",
                    success=False,
                    message=f"Performance check failed with status {response.status_code}",
                    response_time=response_time
                )
        except Exception as e:
            return VerificationResult(
                test_name="Performance Check",
                success=False,
                message=f"Performance check failed: {str(e)}"
            )
    
    def verify_monitoring_endpoints(self) -> List[VerificationResult]:
        """Verify monitoring and observability endpoints"""
        results = []
        
        # Check Prometheus metrics
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/metrics", timeout=self.timeout)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                metrics_text = response.text
                # Check for key metrics
                required_metrics = [
                    "api_requests_total",
                    "api_request_duration_seconds",
                    "python_info"
                ]
                
                missing_metrics = [m for m in required_metrics if m not in metrics_text]
                
                if not missing_metrics:
                    results.append(VerificationResult(
                        test_name="Prometheus Metrics",
                        success=True,
                        message="All required metrics available",
                        response_time=response_time
                    ))
                else:
                    results.append(VerificationResult(
                        test_name="Prometheus Metrics",
                        success=False,
                        message=f"Missing metrics: {', '.join(missing_metrics)}",
                        response_time=response_time
                    ))
            else:
                results.append(VerificationResult(
                    test_name="Prometheus Metrics",
                    success=False,
                    message=f"Metrics endpoint failed with status {response.status_code}",
                    response_time=response_time
                ))
        except Exception as e:
            results.append(VerificationResult(
                test_name="Prometheus Metrics",
                success=False,
                message=f"Metrics check failed: {str(e)}"
            ))
        
        return results
    
    def verify_kubernetes_deployment(self, namespace: str = "agro-shop") -> List[VerificationResult]:
        """Verify Kubernetes deployment status"""
        results = []
        
        try:
            # Check pod status
            cmd = ["kubectl", "get", "pods", "-n", namespace, "-o", "json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                pods_data = json.loads(result.stdout)
                pods = pods_data.get("items", [])
                
                if pods:
                    running_pods = [p for p in pods if p.get("status", {}).get("phase") == "Running"]
                    ready_pods = []
                    
                    for pod in running_pods:
                        conditions = pod.get("status", {}).get("conditions", [])
                        ready_condition = next((c for c in conditions if c.get("type") == "Ready"), None)
                        if ready_condition and ready_condition.get("status") == "True":
                            ready_pods.append(pod)
                    
                    results.append(VerificationResult(
                        test_name="Kubernetes Pods",
                        success=len(ready_pods) > 0,
                        message=f"{len(ready_pods)}/{len(pods)} pods ready",
                        details={
                            "total_pods": len(pods),
                            "running_pods": len(running_pods),
                            "ready_pods": len(ready_pods)
                        }
                    ))
                else:
                    results.append(VerificationResult(
                        test_name="Kubernetes Pods",
                        success=False,
                        message="No pods found in namespace"
                    ))
            else:
                results.append(VerificationResult(
                    test_name="Kubernetes Pods",
                    success=False,
                    message=f"kubectl command failed: {result.stderr}"
                ))
        except subprocess.TimeoutExpired:
            results.append(VerificationResult(
                test_name="Kubernetes Pods",
                success=False,
                message="kubectl command timed out"
            ))
        except Exception as e:
            results.append(VerificationResult(
                test_name="Kubernetes Pods",
                success=False,
                message=f"Kubernetes check failed: {str(e)}"
            ))
        
        return results
    
    def run_comprehensive_verification(self, include_k8s: bool = False, namespace: str = "agro-shop") -> Dict[str, Any]:
        """Run comprehensive deployment verification"""
        print("🔍 Starting Agro Shop Deployment Verification")
        print("=" * 60)
        
        # Basic health and connectivity
        print("\n1️⃣ Basic Health Checks")
        self.add_result(self.verify_health_endpoint())
        
        # API endpoints
        print("\n2️⃣ API Endpoint Verification")
        for result in self.verify_api_endpoints():
            self.add_result(result)
        
        # Database connectivity
        print("\n3️⃣ Database Connectivity")
        self.add_result(self.verify_database_connectivity())
        
        # API functionality
        print("\n4️⃣ API Functionality Tests")
        for result in self.verify_api_functionality():
            self.add_result(result)
        
        # Performance check
        print("\n5️⃣ Performance Verification")
        self.add_result(self.verify_performance())
        
        # Monitoring endpoints
        print("\n6️⃣ Monitoring & Observability")
        for result in self.verify_monitoring_endpoints():
            self.add_result(result)
        
        # Kubernetes deployment (if requested)
        if include_k8s:
            print("\n7️⃣ Kubernetes Deployment Status")
            for result in self.verify_kubernetes_deployment(namespace):
                self.add_result(result)
        
        # Generate summary
        return self.generate_summary()
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate verification summary"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests
        
        summary = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "overall_status": "PASS" if failed_tests == 0 else "FAIL",
            "test_results": [
                {
                    "test_name": r.test_name,
                    "success": r.success,
                    "message": r.message,
                    "response_time": r.response_time,
                    "details": r.details
                }
                for r in self.results
            ]
        }
        
        print("\n" + "=" * 60)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {summary['success_rate']:.1%}")
        print(f"Overall Status: {summary['overall_status']}")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.results:
                if not result.success:
                    print(f"  • {result.test_name}: {result.message}")
        
        # Save detailed report
        report_file = f"verification_report_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return summary

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Agro Shop Deployment Verification")
    parser.add_argument("--url", default="http://localhost:5000", help="Base URL to verify")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")
    parser.add_argument("--k8s", action="store_true", help="Include Kubernetes verification")
    parser.add_argument("--namespace", default="agro-shop", help="Kubernetes namespace")
    args = parser.parse_args()
    
    verifier = DeploymentVerifier(args.url, args.timeout)
    
    try:
        summary = verifier.run_comprehensive_verification(args.k8s, args.namespace)
        
        # Exit with appropriate code
        if summary["overall_status"] == "PASS":
            print("\n🎉 All verification tests passed!")
            sys.exit(0)
        else:
            print(f"\n💥 {summary['failed_tests']} verification tests failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Verification failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()