#!/usr/bin/env python3
"""
Simple test script to verify CPU stress testing functionality
"""

import time
from stress_tests import CPUStressTester
from cpu_monitor import StressTestMonitor

def test_cpu_stress():
    """Test CPU stress testing functionality"""
    print("🚀 Testing CPU Stress Testing Functionality")
    print("=" * 50)
    
    # Initialize components
    stress_tester = CPUStressTester()
    monitor = StressTestMonitor()
    
    print(f"💻 Detected {stress_tester.cpu_count} CPU cores")
    print()
    
    # Test 1: Prime number generation (smaller dataset for quick test)
    print("🔢 Testing Prime Number Generation...")
    monitor.start_stress_test_monitoring("prime_test")
    
    start_time = time.time()
    result = stress_tester.test_prime_generation(max_number=100000)  # Smaller for quick test
    end_time = time.time()
    
    monitoring_results = monitor.stop_stress_test_monitoring()
    
    print(f"✅ Prime Generation Results:")
    print(f"   - Found {result['primes_found']} primes in {result['execution_time']:.2f} seconds")
    print(f"   - Performance: {result['primes_per_second']:.0f} primes/second")
    print(f"   - Peak CPU usage: {monitoring_results.get('peak_cpu_percent', 'N/A')}%")
    print(f"   - Average CPU usage: {monitoring_results.get('avg_cpu_percent', 'N/A')}%")
    print()
    
    # Test 2: Matrix multiplication (smaller matrix for quick test)
    print("🔢 Testing Matrix Multiplication...")
    monitor.start_stress_test_monitoring("matrix_test")
    
    result = stress_tester.test_matrix_multiplication(size=500)  # Smaller for quick test
    monitoring_results = monitor.stop_stress_test_monitoring()
    
    print(f"✅ Matrix Multiplication Results:")
    print(f"   - Matrix size: {result['matrix_size']}")
    print(f"   - Operations: {result['operations']:,}")
    print(f"   - Execution time: {result['execution_time']:.2f} seconds")
    print(f"   - Performance: {result['operations_per_second']:.0f} ops/second")
    print(f"   - Peak CPU usage: {monitoring_results.get('peak_cpu_percent', 'N/A')}%")
    print()
    
    # Test 3: Fibonacci sequence (smaller range for quick test)
    print("🔢 Testing Fibonacci Sequence...")
    monitor.start_stress_test_monitoring("fibonacci_test")
    
    result = stress_tester.test_fibonacci_sequence(max_n=10000)  # Smaller for quick test
    monitoring_results = monitor.stop_stress_test_monitoring()
    
    print(f"✅ Fibonacci Sequence Results:")
    print(f"   - Calculations: {result['calculations']}")
    print(f"   - Execution time: {result['execution_time']:.2f} seconds")
    print(f"   - Performance: {result['calculations_per_second']:.0f} calcs/second")
    print(f"   - Peak CPU usage: {monitoring_results.get('peak_cpu_percent', 'N/A')}%")
    print()
    
    # Test 4: Monte Carlo π calculation (smaller iterations for quick test)
    print("🔢 Testing Monte Carlo π Calculation...")
    monitor.start_stress_test_monitoring("monte_carlo_test")
    
    result = stress_tester.test_monte_carlo_pi(total_iterations=1000000)  # Smaller for quick test
    monitoring_results = monitor.stop_stress_test_monitoring()
    
    print(f"✅ Monte Carlo π Results:")
    print(f"   - Iterations: {result['total_iterations']:,}")
    print(f"   - π estimate: {result['pi_estimate']:.6f}")
    print(f"   - π error: {result['pi_error']:.6f}")
    print(f"   - Execution time: {result['execution_time']:.2f} seconds")
    print(f"   - Performance: {result['iterations_per_second']:.0f} iterations/second")
    print(f"   - Peak CPU usage: {monitoring_results.get('peak_cpu_percent', 'N/A')}%")
    print()
    
    print("🎉 All tests completed successfully!")
    print("=" * 50)
    print("🌐 To run the full web application, use:")
    print("   python main.py")
    print()
    print("📊 Then visit: http://localhost:8000")
    print("📚 API docs: http://localhost:8000/docs")

if __name__ == "__main__":
    test_cpu_stress()