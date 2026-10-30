"""
PhishGuard - Password Security Analyzer & Cryptographic Generator
Provides deep offline entropy estimation, dictionary checks, complexity scoring,
and sequential/spatial pattern detection with a strict zero-storage privacy policy.
"""
import math
import re
import secrets
import string

# Curated set of the most frequent leaked / compromised passwords
COMMON_PASSWORDS = {
    "123456", "password", "123456789", "12345678", "12345", "111111",
    "1234567", "sunshine", "qwerty", "iloveyou", "princess", "admin",
    "welcome", "football", "monkey", "charlie", "donald", "password1",
    "dragon", "master", "shadow", "superman", "trustno1", "michael",
    "starwars", "jordan", "access", "hunter2", "letmein", "secret",
    "pass1234", "login123", "admin123", "p@ssword", "p@$$w0rd", "root",
    "guest", "system", "testing", "default", "changeme", "qwerty123",
    "asdfgh", "zxcvbn", "password123", "abc12345", "123123", "654321"
}

# Keyboard spatial walk patterns (QWERTY layout)
KEYBOARD_PATTERNS = [
    "qwertyuiop", "asdfghjkl", "zxcvbnm",
    "1234567890", "0987654321",
    "poiuytrewq", "lkjhgfdsa", "mnbvcxz"
]

LEET_REPLACEMENTS = {
    "@": "a", "4": "a", "8": "b", "3": "e", "1": "i", "!": "i",
    "0": "o", "5": "s", "$": "s", "7": "t", "+": "t"
}


def normalize_leetspeak(text: str) -> str:
    """Normalize simple leetspeak substitutions to root text."""
    lowered = text.lower()
    for leet, orig in LEET_REPLACEMENTS.items():
        lowered = lowered.replace(leet, orig)
    return lowered


def check_sequential_runs(text: str) -> bool:
    """Detect sequential runs of 3+ consecutive numbers or alphabet letters."""
    if len(text) < 3:
        return False
    lowered = text.lower()
    for i in range(len(lowered) - 2):
        chunk = lowered[i:i+3]
        if all(c.isdigit() for c in chunk):
            n1, n2, n3 = int(chunk[0]), int(chunk[1]), int(chunk[2])
            if (n2 == n1 + 1 and n3 == n2 + 1) or (n2 == n1 - 1 and n3 == n2 - 1):
                return True
        elif all(c.isalpha() for c in chunk):
            c1, c2, c3 = ord(chunk[0]), ord(chunk[1]), ord(chunk[2])
            if (c2 == c1 + 1 and c3 == c2 + 1) or (c2 == c1 - 1 and c3 == c2 - 1):
                return True
    return False


def check_keyboard_patterns(text: str) -> bool:
    """Detect spatial keyboard sequences (e.g. qwerty, asdf, 12345)."""
    lowered = text.lower()
    if len(lowered) < 3:
        return False
    for pat in KEYBOARD_PATTERNS:
        for i in range(len(pat) - 2):
            sub = pat[i:i+3]
            if sub in lowered:
                return True
    return False


def check_repeated_characters(text: str) -> bool:
    """Detect 3+ consecutive identical characters or low unique ratio."""
    if len(text) < 3:
        return False
    if re.search(r"(.)\1{2,}", text):
        return True
    if len(text) >= 6 and len(set(text)) <= 2:
        return True
    return False


def estimate_crack_time(entropy_bits: float) -> str:
    """
    Estimate time to crack offline using a modern multi-GPU hash cluster
    calculating approximately 10^10 hashes per second (e.g., fast NTLM/MD5).
    """
    if entropy_bits <= 0:
        return "Instant (< 1 millisecond)"

    combinations = 2 ** min(entropy_bits, 128)
    guesses_per_sec = 10_000_000_000

    seconds = combinations / (2 * guesses_per_sec)

    if seconds < 0.001:
        return "Instant (< 1 millisecond)"
    elif seconds < 1:
        return "< 1 second"
    elif seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        return f"{int(seconds / 60)} minutes"
    elif seconds < 86400:
        return f"{int(seconds / 3600)} hours"
    elif seconds < 31536000:
        return f"{int(seconds / 86400)} days"
    elif seconds < 31536000 * 100:
        return f"{int(seconds / 31536000)} years"
    elif seconds < 31536000 * 1000000:
        return f"{int(seconds / (31536000 * 1000))} thousand years"
    else:
        return "Centuries (Computationally Infeasible)"


def analyze_password(password: str) -> dict:
    """
    Analyze password strength, entropy, complexity, and common weaknesses.
    NEVER logs or stores the input password string.
    """
    if not password:
        return {
            "length": 0,
            "score": 0,
            "score_100": 0,
            "category": "Very Weak",
            "strength_category": "Very Weak",
            "entropy_bits": 0.0,
            "pool_size": 0,
            "charset_pool_size": 0,
            "crack_time": "Instant",
            "crack_time_display": "Instant",
            "is_common": False,
            "has_repeated": False,
            "has_sequential": False,
            "has_keyboard_walk": False,
            "has_keyboard_pattern": False,
            "meets_length": False,
            "has_lowercase": False,
            "has_uppercase": False,
            "has_digit": False,
            "has_symbol": False,
            "checks": {
                "has_lowercase": False,
                "has_uppercase": False,
                "has_digit": False,
                "has_symbol": False,
                "min_length_12": False
            },
            "recommendations": ["Enter a password to inspect."],
            "disclaimer": "Entropy alone does not guarantee security against credential leaks or targeted attacks."
        }

    length = len(password)
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    symbols = set(string.punctuation)
    has_symbol = any(c in symbols for c in password)

    # 1. Determine Character Pool Size (R)
    pool_size = 0
    if has_lower:
        pool_size += 26
    if has_upper:
        pool_size += 26
    if has_digit:
        pool_size += 10
    if has_symbol:
        pool_size += 33
    if any(ord(c) > 127 for c in password):
        pool_size += 50

    pool_size = max(pool_size, 1)

    # 2. Theoretical Shannon Entropy: E = L * log2(R)
    theoretical_entropy = length * math.log2(pool_size)

    # 3. Detect Patterns & Common Passwords
    normalized_pass = normalize_leetspeak(password)
    is_common = (
        password.lower() in COMMON_PASSWORDS
        or normalized_pass in COMMON_PASSWORDS
        or any(w in normalized_pass for w in ("admin", "password", "root", "guest", "qwerty") if len(w) >= 5)
    )

    has_repeated = check_repeated_characters(password)
    has_sequential = check_sequential_runs(password)
    has_keyboard_walk = check_keyboard_patterns(password)

    # 4. Penalty Deductions for Weaknesses
    penalties = 0.0
    if is_common:
        penalties += 40.0
    if len(set(password)) <= 2:
        penalties += 45.0
    elif has_repeated:
        penalties += 16.0
    if has_sequential:
        penalties += 16.0
    if has_keyboard_walk:
        penalties += 18.0
    if length < 8:
        penalties += 25.0
    elif length < 12:
        penalties += 8.0

    effective_entropy = max(0.0, round(theoretical_entropy - penalties, 1))

    # 5. Strength Category & Scores (0-4 and 0-100)
    if is_common or length < 6 or effective_entropy < 28 or len(set(password)) <= 2:
        strength_category = "Very Weak"
        score = 0
        score_100 = min(20, int(effective_entropy * 0.7))
    elif effective_entropy < 45 or length < 8 or has_sequential:
        strength_category = "Weak"
        score = 1
        score_100 = min(40, max(25, int(effective_entropy * 0.85)))
    elif effective_entropy < 62:
        strength_category = "Medium"
        score = 2
        score_100 = min(65, max(45, int(effective_entropy * 0.95)))
    elif effective_entropy < 78 or not (has_lower and has_upper and has_digit and has_symbol):
        strength_category = "Strong"
        score = 3
        score_100 = min(85, max(70, int(effective_entropy * 1.02)))
    else:
        strength_category = "Very Strong"
        score = 4
        score_100 = min(100, max(90, int(effective_entropy * 1.05)))

    # 6. Recommendations
    recommendations = []
    if length < 12:
        recommendations.append(f"Increase password length to at least 14-16 characters (current: {length}).")
    if is_common:
        recommendations.append("This is a known common or compromised password pattern. Change it immediately.")
    if not has_upper:
        recommendations.append("Include uppercase letters (A-Z) to expand character pool diversity.")
    if not has_lower:
        recommendations.append("Include lowercase letters (a-z).")
    if not has_digit:
        recommendations.append("Include numeric digits (0-9).")
    if not has_symbol:
        recommendations.append("Include special symbols (e.g. !@#$%^&*).")
    if has_repeated:
        recommendations.append("Avoid consecutive or excessive repeated characters.")
    if has_sequential:
        recommendations.append("Avoid sequential numbers or alphabet runs (e.g., '1234', 'abcd').")
    if has_keyboard_walk:
        recommendations.append("Avoid spatial keyboard patterns (e.g., 'qwerty', 'asdf').")

    if not recommendations:
        recommendations.append("Excellent password complexity! Suitable for high-security accounts.")
        recommendations.append("Consider using a password manager and enabling multi-factor authentication (2FA).")

    crack_time = estimate_crack_time(effective_entropy)

    return {
        "length": length,
        "score": score,
        "score_100": score_100,
        "category": strength_category,
        "strength_category": strength_category,
        "entropy_bits": effective_entropy,
        "theoretical_entropy": round(theoretical_entropy, 1),
        "pool_size": pool_size,
        "charset_pool_size": pool_size,
        "crack_time": crack_time,
        "crack_time_display": crack_time,
        "is_common": is_common,
        "has_repeated": has_repeated,
        "has_sequential": has_sequential,
        "has_keyboard_walk": has_keyboard_walk,
        "has_keyboard_pattern": has_keyboard_walk,
        "meets_length": length >= 12,
        "has_lowercase": has_lower,
        "has_uppercase": has_upper,
        "has_digit": has_digit,
        "has_symbol": has_symbol,
        "checks": {
            "has_lowercase": has_lower,
            "has_uppercase": has_upper,
            "has_digit": has_digit,
            "has_symbol": has_symbol,
            "min_length_12": length >= 12
        },
        "recommendations": recommendations,
        "formula": "E = L * log2(R) where L is length and R is character pool size, adjusted for pattern penalties.",
        "disclaimer": "Entropy alone does not guarantee security against credential stuffing, phishing, or active malware."
    }


def generate_secure_password(length: int = 16, include_symbols: bool = True,
                             include_numbers: bool = True, include_uppercase: bool = True,
                             include_digits: bool = None) -> str:
    """
    Generate a cryptographically secure random password using secrets module.
    Guarantees at least one character from each enabled set.
    """
    if include_digits is not None:
        include_numbers = include_digits

    length = max(8, min(64, length))

    lower_pool = string.ascii_lowercase
    upper_pool = string.ascii_uppercase if include_uppercase else ""
    digits_pool = string.digits if include_numbers else ""
    symbols_pool = "!@#$%^&*()_+-=[]{}|;:,.<>?" if include_symbols else ""

    combined_pool = lower_pool + upper_pool + digits_pool + symbols_pool
    if not combined_pool:
        combined_pool = lower_pool

    guaranteed = [secrets.choice(lower_pool)]
    if include_uppercase and upper_pool:
        guaranteed.append(secrets.choice(upper_pool))
    if include_numbers and digits_pool:
        guaranteed.append(secrets.choice(digits_pool))
    if include_symbols and symbols_pool:
        guaranteed.append(secrets.choice(symbols_pool))

    remaining_length = max(0, length - len(guaranteed))
    random_chars = [secrets.choice(combined_pool) for _ in range(remaining_length)]

    all_chars = guaranteed + random_chars
    # Cryptographic shuffle
    for i in range(len(all_chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        all_chars[i], all_chars[j] = all_chars[j], all_chars[i]

    return "".join(all_chars)
