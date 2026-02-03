#!/usr/bin/env python3
"""
🚀 Agro Shop - Performance Testing Suite

This script performs comprehensive performance testing of the Agro Shop application
including load testing, stress testing, and performance benchmarking.
"""

import asyncio
import aiohttp
import time
import statistics
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import List, Dict, Any
import argparse

@dataclass
class TestResult:
    """Performance test result data structure"""
    endpoint: str
    method: str
    response_time: float
    status_code: int
    success: bool
    error: str = None

class PerformanceTester:
    """Comprehensive performance testing class"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.results: List[TestResult] = []
        
    async def make_request(self, session: aiohttp.ClientSession, method: str, endpoint: str, **kwargs) -> TestResult:
        """Make a single HTTP request and measure performance"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            async with session.request(method, url, **kwargs) as response:
                await response.text()  # Read response body
                response_time = time.time() - start_time
                
                return TestResult(
                    endpoint=endpoint,
                    method=method,
                    response_time=response_time,
                    status_code=response.status,
                    success=200 <= response.status < 400
                )
        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                endpoint=endpoint,
                method=method,
                response_time=response_time,
                status_code=0,
                success=False,
                error=str(e)
            )
    
    async def load_test(self, endpoint: str, method: str = "GET", concurrent_users: int = 10, 
                       duration: int = 30, **kwargs) -> List[TestResult]:
        """Perform load testing on a specific endpoint"""
        print(f"🔥 Load testing {method} {endpoint} with {concurrent_users} concurrent users for {duration}s")
        
        results = []
        end_time = time.time() + duration
        
        async with aiohttp.ClientSession() as session:
            while time.time() < end_time:
                tasks = []
                for _ in range(concurrent_users):
                    task = self.make_request(session, method, endpoint, **kwargs)
                    tasks.append(task)
                
                batch_results = await asyncio.gather(*tasks)
                results.extend(batch_results)
                
                # Small delay to prevent overwhelming the server
                await asyncio.sleep(0.1)
        
        return results
    
    async def stress_test(self, endpoint: str, method: str = "GET", max_users: int = 100, 
                         step: int = 10, step_duration: int = 10, **kwargs) -> Dict[int, List[TestResult]]:
        """Perform stress testing with gradually increasing load"""
        print(f"💪 Stress testing {method} {endpoint} up to {max_users} users")
        
        stress_results = {}
        
        for users in range(step, max_users + 1, step):
            print(f"  Testing with {users} concurrent users...")
            results = await self.load_test(endpoint, method, users, step_duration, **kwargs)
            stress_results[users] = results
            
            # Check if we're hitting error threshold
            error_rate = sum(1 for r in results if not r.success) / len(results)
            if error_rate > 0.1:  # 10% error rate threshold
                print(f"  ⚠️ High error rate ({error_rate:.1%}) detected at {users} users")
                break
        
        return stress_results
    
    def analyze_results(self, results: List[TestResult]) -> Dict[str, Any]:
        """Analyze performance test results"""
        if not results:
            return {}
        
        response_times = [r.response_time for r in results]
        successful_requests = [r for r in results if r.success]
        failed_requests = [r for r in results if not r.success]
        
        analysis = {
            "total_requests": len(results),
            "successful_requests": len(successful_requests),
            "failed_requests": len(failed_requests),
            "success_rate": len(successful_requests) / len(results),
            "error_rate": len(failed_requests) / len(results),
            "response_times": {
                "min": min(response_times),
                "max": max(response_times),
                "mean": statistics.mean(response_times),
                "median": statistics.median(response_times),
                "p95": self.percentile(response_times, 95),
                "p99": self.percentile(response_times, 99)
            },
            "requests_per_second": len(results) / sum(response_times) if response_times else 0
        }
        
        return analysis
    
    @staticmethod
    def percentile(data: List[float], percentile: int) -> float:
        """Calculate percentile of a dataset"""
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def print_analysis(self, analysis: Dict[str, Any], title: str = "Performance Analysis"):
        """Print formatted analysis results"""
        print(f"\n📊 {title}")
        print("=" * 50)
        print(f"Total Requests: {analysis['total_requests']}")
        print(f"Successful: {analysis['successful_requests']} ({analysis['success_rate']:.1%})")
        print(f"Failed: {analysis['failed_requests']} ({analysis['error_rate']:.1%})")
        print(f"Requests/sec: {analysis['requests_per_second']:.2f}")
        
        rt = analysis['response_times']
        print(f"\nResponse Times (seconds):")
        print(f"  Min: {rt['min']:.3f}s")
        print(f"  Max: {rt['max']:.3f}s")
        print(f"  Mean: {rt['mean']:.3f}s")
        print(f"  Median: {rt['median']:.3f}s")
        print(f"  95th percentile: {rt['p95']:.3f}s")
        print(f"  99th percentile: {rt['p99']:.3f}s")
    
    async def comprehensive_test_suite(self):
        """Run comprehensive performance test suite"""
        print("🚀 Starting Agro Shop Performance Test Suite")
        print("=" * 60)
        
        # Test endpoints
        endpoints = [
            ("/", "GET"),
            ("/health", "GET"),
            ("/metrics", "GET"),
            ("/api/v1/products", "GET"),
            ("/api/v1/stats", "GET"),
        ]
        
        # 1. Basic response time test
        print("\n1️⃣ Basic Response Time Test")
        async with aiohttp.ClientSession() as session:
            for endpoint, method in endpoints:
                result = await self.make_request(session, method, endpoint)
                status = "✅" if result.success else "❌"
                print(f"  {status} {method} {endpoint}: {result.response_time:.3f}s (HTTP {result.status_code})")
        
        # 2. Load test on main endpoints
        print("\n2️⃣ Load Testing")
        for endpoint, method in [("/", "GET"), ("/api/v1/products", "GET")]:
            results = await self.load_test(endpoint, method, concurrent_users=20, duration=15)
            analysis = self.analyze_results(results)
            self.print_analysis(analysis, f"Load Test: {method} {endpoint}")
        
        # 3. API POST performance test
        print("\n3️⃣ API POST Performance Test")
        product_data = {
            "name": "Performance Test Product",
            "price": 9.99,
            "category": "Test",
            "stock": 100
        }
        
        post_results = await self.load_test(
            "/api/v1/products", 
            "POST", 
            concurrent_users=5, 
            duration=10,
            json=product_data,
            headers={"Content-Type": "application/json"}
        )
        
        post_analysis = self.analyze_results(post_results)
        self.print_analysis(post_analysis, "POST /api/v1/products")
        
        # 4. Stress test
        print("\n4️⃣ Stress Testing")
        stress_results = await self.stress_test("/", max_users=50, step=10, step_duration=5)
        
        print("\nStress Test Results:")
        for users, results in stress_results.items():
            analysis = self.analyze_results(results)
            print(f"  {users} users: {analysis['response_times']['mean']:.3f}s avg, {analysis['success_rate']:.1%} success")
        
        # 5. Generate performance report
        self.generate_performance_report(stress_results)
    
    def generate_performance_report(self, stress_results: Dict[int, List[TestResult]]):
        """Generate a comprehensive performance report"""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_summary": {
                "application": "Agro Shop",
                "base_url": self.base_url,
                "test_type": "Comprehensive Performance Test"
            },
            "stress_test_results": {}
        }
        
        for users, results in stress_results.items():
            analysis = self.analyze_results(results)
            report["stress_test_results"][users] = analysis
        
        # Save report to file
        report_file = f"performance_report_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Performance report saved to: {report_file}")
        
        # Performance recommendations
        print("\n💡 Performance Recommendations:")
        
        # Find breaking point
        breaking_point = None
        for users in sorted(stress_results.keys()):
            results = stress_results[users]
            error_rate = sum(1 for r in results if not r.success) / len(results)
            if error_rate > 0.05:  # 5% error rate
                breaking_point = users
                break
        
        if breaking_point:
            print(f"  • Application starts showing stress at {breaking_point} concurrent users")
            print(f"  • Consider scaling horizontally before reaching {breaking_point} users")
        
        # Response time recommendations
        latest_results = list(stress_results.values())[-1]
        latest_analysis = self.analyze_results(latest_results)
        avg_response = latest_analysis['response_times']['mean']
        
        if avg_response > 2.0:
            print("  • Response times are high (>2s), consider performance optimization")
        elif avg_response > 1.0:
            print("  • Response times are acceptable but could be improved (<1s target)")
        else:
            print("  • Response times are excellent (<1s)")
        
        print("  • Monitor memory and CPU usage during peak loads")
        print("  • Consider implementing caching for frequently accessed data")
        print("  • Use a load balancer for production deployments")

async def main():
    """Main function to run performance tests"""
    parser = argparse.ArgumentParser(description="Agro Shop Performance Testing")
    parser.add_argument("--url", default="http://localhost:5000", help="Base URL to test")
    parser.add_argument("--quick", action="store_true", help="Run quick test suite")
    args = parser.parse_args()
    
    tester = PerformanceTester(args.url)
    
    try:
        if args.quick:
            # Quick test - just basic response times
            print("🏃‍♂️ Running Quick Performance Test")
            async with aiohttp.ClientSession() as session:
                endpoints = [("/", "GET"), ("/health", "GET"), ("/api/v1/products", "GET")]
                for endpoint, method in endpoints:
                    result = await tester.make_request(session, method, endpoint)
                    status = "✅" if result.success else "❌"
                    print(f"{status} {method} {endpoint}: {result.response_time:.3f}s")
        else:
            # Full comprehensive test suite
            await tester.comprehensive_test_suite()
            
    except KeyboardInterrupt:
        print("\n⏹️ Performance testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Performance testing failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())