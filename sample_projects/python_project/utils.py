"""
Utility functions for mathematical operations
"""

def factorial(n):
    """Calculate factorial of n"""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def fibonacci(n):
    """Calculate nth Fibonacci number"""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

def print_list(items):
    """Print all items in a list"""
    for item in items:
        print(item, end=' ')
    print()

def is_prime(n):
    """Check if a number is prime"""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def get_primes_up_to(n):
    """Get all prime numbers up to n"""
    primes = []
    for i in range(2, n + 1):
        if is_prime(i):
            primes.append(i)
    return primes 