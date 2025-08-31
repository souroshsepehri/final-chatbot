#!/usr/bin/env python3
"""
Performance test script for the chatbot.
"""

import time
import requests
import json
from typing import List, Dict

# Configuration
BASE_URL = "http://localhost:8000"
TEST_MESSAGES = [
    "hello",
    "what is your name?",
    "how can you help me?",
    "what services do you offer?",
    "tell me about your company",
    "what are your contact details?",
    "how do I get support?",
    "what are your business hours?",
    "do you have a FAQ?",
    "can you help me with technical issues?"
]

def test_single_request(message: str) -> Dict:
    """Test a single chat request and measure performance."""
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/",
            json={"message": message},
            timeout=30
        )
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "message": message,
                "response_time_ms": response_time,
                "source": data.get("source", "unknown"),
                "response_length": len(data.get("response", "")),
                "reported_response_time": data.get("response_time_ms")
            }
        else:
            return {
                "success": False,
                "message": message,
                "response_time_ms": response_time,
                "error": f"HTTP {response.status_code}: {response.text}"
            }
            
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "message": message,
            "response_time_ms": 30000,  # 30 second timeout
            "error": "Request timeout"
        }
    except Exception as e:
        return {
            "success": False,
            "message": message,
            "response_time_ms": 0,
            "error": str(e)
        }

def run_performance_test(num_iterations: int = 3) -> Dict:
    """Run a comprehensive performance test."""
    print(f"🚀 Starting performance test with {num_iterations} iterations per message...")
    print(f"📝 Testing {len(TEST_MESSAGES)} different messages")
    print(f"🔄 Total requests: {len(TEST_MESSAGES) * num_iterations}")
    print()
    
    all_results = []
    start_time = time.time()
    
    for i in range(num_iterations):
        print(f"📊 Iteration {i + 1}/{num_iterations}")
        
        for message in TEST_MESSAGES:
            result = test_single_request(message)
            all_results.append(result)
            
            if result["success"]:
                print(f"  ✅ {message[:30]:<30} | {result['response_time_ms']:>6.0f}ms | {result['source']}")
            else:
                print(f"  ❌ {message[:30]:<30} | {result['response_time_ms']:>6.0f}ms | {result['error']}")
    
    total_time = time.time() - start_time
    
    # Analyze results
    successful_results = [r for r in all_results if r["success"]]
    failed_results = [r for r in all_results if not r["success"]]
    
    if successful_results:
        response_times = [r["response_time_ms"] for r in successful_results]
        avg_response_time = sum(response_times) / len(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        
        # Group by source
        source_stats = {}
        for result in successful_results:
            source = result["source"]
            if source not in source_stats:
                source_stats[source] = []
            source_stats[source].append(result["response_time_ms"])
        
        source_averages = {
            source: sum(times) / len(times) 
            for source, times in source_stats.items()
        }
    else:
        avg_response_time = min_response_time = max_response_time = 0
        source_averages = {}
    
    # Print summary
    print()
    print("📈 PERFORMANCE SUMMARY")
    print("=" * 50)
    print(f"Total requests: {len(all_results)}")
    print(f"Successful: {len(successful_results)} ({len(successful_results)/len(all_results)*100:.1f}%)")
    print(f"Failed: {len(failed_results)} ({len(failed_results)/len(all_results)*100:.1f}%)")
    print(f"Total test time: {total_time:.2f}s")
    print(f"Average response time: {avg_response_time:.0f}ms")
    print(f"Min response time: {min_response_time:.0f}ms")
    print(f"Max response time: {max_response_time:.0f}ms")
    print()
    
    print("📊 RESPONSE TIMES BY SOURCE")
    print("-" * 30)
    for source, avg_time in sorted(source_averages.items(), key=lambda x: x[1]):
        count = len(source_stats[source])
        print(f"{source:>15}: {avg_time:>6.0f}ms ({count} requests)")
    
    if failed_results:
        print()
        print("❌ FAILED REQUESTS")
        print("-" * 20)
        for result in failed_results[:5]:  # Show first 5 failures
            print(f"Message: {result['message']}")
            print(f"Error: {result['error']}")
            print()
    
    return {
        "total_requests": len(all_results),
        "successful_requests": len(successful_results),
        "failed_requests": len(failed_results),
        "success_rate": len(successful_results) / len(all_results) if all_results else 0,
        "total_test_time": total_time,
        "avg_response_time_ms": avg_response_time,
        "min_response_time_ms": min_response_time,
        "max_response_time_ms": max_response_time,
        "source_averages": source_averages,
        "failed_requests": failed_results
    }

def test_performance_endpoint() -> Dict:
    """Test the performance endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/chat/performance", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("🤖 Chatbot Performance Test")
    print("=" * 40)
    
    # Test if server is running
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code != 200:
            print(f"❌ Server health check failed: {health_response.status_code}")
            exit(1)
        print("✅ Server is running")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print(f"   Make sure the server is running on {BASE_URL}")
        exit(1)
    
    print()
    
    # Run performance test
    results = run_performance_test(num_iterations=2)
    
    print()
    print("🔍 PERFORMANCE ENDPOINT DATA")
    print("=" * 30)
    perf_data = test_performance_endpoint()
    if "error" not in perf_data:
        print(f"Total requests (last hour): {perf_data.get('total_requests_last_hour', 'N/A')}")
        print(f"Average response time: {perf_data.get('average_response_time_ms', 'N/A'):.0f}ms")
        
        recommendations = perf_data.get('recommendations', [])
        if recommendations:
            print("\n💡 RECOMMENDATIONS:")
            for rec in recommendations:
                print(f"  • {rec}")
    else:
        print(f"❌ Could not fetch performance data: {perf_data['error']}")
    
    print()
    print("🎯 PERFORMANCE TARGETS")
    print("-" * 25)
    print("✅ < 500ms: Excellent")
    print("⚠️  500-1000ms: Good")
    print("❌ > 1000ms: Needs improvement")
    
    # Final assessment
    avg_time = results["avg_response_time_ms"]
    if avg_time < 500:
        print(f"\n🎉 EXCELLENT! Average response time: {avg_time:.0f}ms")
    elif avg_time < 1000:
        print(f"\n👍 GOOD! Average response time: {avg_time:.0f}ms")
    else:
        print(f"\n⚠️  NEEDS IMPROVEMENT! Average response time: {avg_time:.0f}ms")





















