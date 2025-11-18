"""General utilities for CTF challenges."""

import math
import itertools
import string
from typing import List, Generator, Union
from ..exceptions import CTFUtilsError


# ============================================================================
# WORDLIST GENERATION FUNCTIONS
# ============================================================================

def generate_wordlist(charset: str, min_length: int, max_length: int) -> Generator[str, None, None]:
    """Generate wordlist with specified charset and length range."""
    for length in range(min_length, max_length + 1):
        for word in itertools.product(charset, repeat=length):
            yield ''.join(word)


def bruteforce_pattern(pattern: str, charset: str = string.ascii_lowercase) -> Generator[str, None, None]:
    """Generate strings matching a pattern. Use '?' for variable characters."""
    variable_positions = [i for i, char in enumerate(pattern) if char == '?']
    
    if not variable_positions:
        yield pattern
        return
    
    for combination in itertools.product(charset, repeat=len(variable_positions)):
        result = list(pattern)
        for pos, char in zip(variable_positions, combination):
            result[pos] = char
        yield ''.join(result)


# ============================================================================
# MATHEMATICAL FUNCTIONS
# ============================================================================

def calculate_entropy(text: str) -> float:
    """Calculate Shannon entropy of text."""
    if not text:
        return 0.0
    
    frequencies = {}
    for char in text:
        frequencies[char] = frequencies.get(char, 0) + 1
    
    entropy = 0.0
    text_length = len(text)
    
    for count in frequencies.values():
        probability = count / text_length
        entropy -= probability * math.log2(probability)
    
    return entropy


def find_common_factors(numbers: List[int]) -> List[int]:
    """Find common factors of a list of numbers."""
    if not numbers:
        return []
    
    first_num = abs(numbers[0])
    factors = set()
    
    for i in range(1, int(math.sqrt(first_num)) + 1):
        if first_num % i == 0:
            factors.add(i)
            factors.add(first_num // i)
    
    common_factors = []
    for factor in factors:
        if all(num % factor == 0 for num in numbers):
            common_factors.append(factor)
    
    return sorted(common_factors)


def gcd(a: int, b: int) -> int:
    """Calculate Greatest Common Divisor."""
    while b:
        a, b = b, a % b
    return abs(a)


def gcd_list(numbers: List[int]) -> int:
    """Calculate GCD of a list of numbers."""
    if not numbers:
        return 0
    
    result = abs(numbers[0])
    for num in numbers[1:]:
        result = gcd(result, abs(num))
    
    return result


def lcm(a: int, b: int) -> int:
    """Calculate Least Common Multiple."""
    return abs(a * b) // gcd(a, b) if a and b else 0


def is_prime(n: int) -> bool:
    """Check if a number is prime."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    
    return True


def prime_factors(n: int) -> List[int]:
    """Find prime factors of a number."""
    factors = []
    d = 2
    
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    
    if n > 1:
        factors.append(n)
    
    return factors


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_input(value: any, expected_type: type, param_name: str = "parameter") -> None:
    """Validate input parameter type."""
    if not isinstance(value, expected_type):
        raise CTFUtilsError(f"{param_name} must be of type {expected_type.__name__}, got {type(value).__name__}")


def safe_divide(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """Safe division that handles division by zero."""
    if b == 0:
        raise CTFUtilsError("Division by zero")
    return a / b


# ============================================================================
# STRING DISTANCE FUNCTIONS
# ============================================================================

def hamming_distance(str1: str, str2: str) -> int:
    """Calculate Hamming distance between two strings."""
    if len(str1) != len(str2):
        raise CTFUtilsError("Strings must have equal length for Hamming distance")
    
    return sum(c1 != c2 for c1, c2 in zip(str1, str2))


def levenshtein_distance(str1: str, str2: str) -> int:
    """Calculate Levenshtein distance between two strings."""
    if len(str1) < len(str2):
        return levenshtein_distance(str2, str1)
    
    if len(str2) == 0:
        return len(str1)
    
    previous_row = range(len(str2) + 1)
    for i, c1 in enumerate(str1):
        current_row = [i + 1]
        for j, c2 in enumerate(str2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]
