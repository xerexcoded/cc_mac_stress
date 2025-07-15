import time
import multiprocessing
import numpy as np
import random
import math
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Dict, List, Tuple


def prime_sieve_chunk(start: int, end: int) -> List[int]:
    """Generate prime numbers in a range using Sieve of Eratosthenes"""
    if start < 2:
        start = 2
    
    # Create boolean array and initialize all entries as True
    sieve = [True] * (end - start + 1)
    
    # Start with smallest prime 2
    for p in range(2, int(math.sqrt(end)) + 1):
        # Find minimum number in range [start, end] that is multiple of p
        start_multiple = max(p * p, (start + p - 1) // p * p)
        
        # Mark multiples of p in range [start, end]
        for i in range(start_multiple, end + 1, p):
            sieve[i - start] = False
    
    # Collect all prime numbers
    primes = []
    for i in range(len(sieve)):
        if sieve[i]:
            primes.append(start + i)
    
    return primes


def matrix_multiply_chunk(args: Tuple[np.ndarray, np.ndarray, int, int]) -> np.ndarray:
    """Multiply matrix chunks for parallel processing"""
    a, b, start_row, end_row = args
    return np.dot(a[start_row:end_row], b)


def fibonacci_worker(n: int) -> int:
    """Calculate Fibonacci number using iterative method"""
    if n <= 1:
        return n
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def merge_sort_parallel(arr: List[int], depth: int = 0) -> List[int]:
    """Parallel merge sort implementation"""
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    
    # Use parallel processing for larger arrays at shallow depths
    if len(arr) > 1000 and depth < 3:
        with ProcessPoolExecutor(max_workers=2) as executor:
            left_future = executor.submit(merge_sort_parallel, arr[:mid], depth + 1)
            right_future = executor.submit(merge_sort_parallel, arr[mid:], depth + 1)
            
            left = left_future.result()
            right = right_future.result()
    else:
        left = merge_sort_parallel(arr[:mid], depth + 1)
        right = merge_sort_parallel(arr[mid:], depth + 1)
    
    return merge(left, right)


def merge(left: List[int], right: List[int]) -> List[int]:
    """Merge two sorted arrays"""
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def monte_carlo_pi_chunk(iterations: int) -> int:
    """Calculate π using Monte Carlo method - returns count of points inside circle"""
    count = 0
    for _ in range(iterations):
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        if x * x + y * y <= 1:
            count += 1
    return count


class CPUStressTester:
    def __init__(self):
        self.cpu_count = multiprocessing.cpu_count()
    
    def test_prime_generation(self, max_number: int = 1000000) -> Dict:
        """Stress test with prime number generation"""
        start_time = time.time()
        
        # Divide work among CPU cores
        chunk_size = max_number // self.cpu_count
        chunks = []
        
        for i in range(self.cpu_count):
            start = i * chunk_size + 1
            end = (i + 1) * chunk_size if i < self.cpu_count - 1 else max_number
            chunks.append((start, end))
        
        # Process chunks in parallel
        with ProcessPoolExecutor(max_workers=self.cpu_count) as executor:
            futures = [executor.submit(prime_sieve_chunk, start, end) for start, end in chunks]
            results = []
            
            for future in as_completed(futures):
                results.extend(future.result())
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        return {
            'test_type': 'Prime Generation',
            'max_number': max_number,
            'primes_found': len(results),
            'execution_time': execution_time,
            'primes_per_second': len(results) / execution_time,
            'cpu_cores_used': self.cpu_count
        }
    
    def test_matrix_multiplication(self, size: int = 1000) -> Dict:
        """Stress test with matrix multiplication"""
        start_time = time.time()
        
        # Generate random matrices
        matrix_a = np.random.rand(size, size)
        matrix_b = np.random.rand(size, size)
        
        # Divide matrix A into chunks for parallel processing
        chunk_size = size // self.cpu_count
        chunks = []
        
        for i in range(self.cpu_count):
            start_row = i * chunk_size
            end_row = (i + 1) * chunk_size if i < self.cpu_count - 1 else size
            chunks.append((matrix_a, matrix_b, start_row, end_row))
        
        # Process chunks in parallel
        with ProcessPoolExecutor(max_workers=self.cpu_count) as executor:
            futures = [executor.submit(matrix_multiply_chunk, chunk) for chunk in chunks]
            results = []
            
            for future in as_completed(futures):
                results.append(future.result())
        
        # Combine results
        result_matrix = np.vstack(results)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        return {
            'test_type': 'Matrix Multiplication',
            'matrix_size': f'{size}x{size}',
            'operations': size * size * size,
            'execution_time': execution_time,
            'operations_per_second': (size * size * size) / execution_time,
            'cpu_cores_used': self.cpu_count
        }
    
    def test_fibonacci_sequence(self, max_n: int = 50000) -> Dict:
        """Stress test with Fibonacci sequence calculation"""
        start_time = time.time()
        
        # Generate list of Fibonacci numbers to calculate
        fib_numbers = list(range(1, max_n + 1, max_n // (self.cpu_count * 10)))
        
        # Calculate Fibonacci numbers in parallel
        with ProcessPoolExecutor(max_workers=self.cpu_count) as executor:
            futures = [executor.submit(fibonacci_worker, n) for n in fib_numbers]
            results = []
            
            for future in as_completed(futures):
                results.append(future.result())
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        return {
            'test_type': 'Fibonacci Sequence',
            'max_number': max_n,
            'calculations': len(fib_numbers),
            'execution_time': execution_time,
            'calculations_per_second': len(fib_numbers) / execution_time,
            'cpu_cores_used': self.cpu_count
        }
    
    def test_sorting_algorithms(self, array_size: int = 100000) -> Dict:
        """Stress test with parallel sorting"""
        start_time = time.time()
        
        # Generate random array
        test_array = [random.randint(1, 1000000) for _ in range(array_size)]
        
        # Sort using parallel merge sort
        sorted_array = merge_sort_parallel(test_array.copy())
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        return {
            'test_type': 'Parallel Merge Sort',
            'array_size': array_size,
            'execution_time': execution_time,
            'elements_per_second': array_size / execution_time,
            'cpu_cores_used': self.cpu_count,
            'is_sorted': sorted_array == sorted(test_array)
        }
    
    def test_monte_carlo_pi(self, total_iterations: int = 10000000) -> Dict:
        """Stress test with Monte Carlo π calculation"""
        start_time = time.time()
        
        # Divide iterations among CPU cores
        iterations_per_core = total_iterations // self.cpu_count
        
        # Calculate π using Monte Carlo method in parallel
        with ProcessPoolExecutor(max_workers=self.cpu_count) as executor:
            futures = [executor.submit(monte_carlo_pi_chunk, iterations_per_core) for _ in range(self.cpu_count)]
            total_inside = sum(future.result() for future in as_completed(futures))
        
        # Calculate π
        pi_estimate = 4 * total_inside / total_iterations
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        return {
            'test_type': 'Monte Carlo π Calculation',
            'total_iterations': total_iterations,
            'pi_estimate': pi_estimate,
            'pi_error': abs(pi_estimate - math.pi),
            'execution_time': execution_time,
            'iterations_per_second': total_iterations / execution_time,
            'cpu_cores_used': self.cpu_count
        }