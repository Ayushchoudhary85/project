"""
Feature Extraction Engine for PhishGuard.
Extracts lexical, structural, and advanced threat indicators from URLs.
"""
import math
import re
import ipaddress
from urllib.parse import urlparse, parse_qs
import tldextract
from config import Config

# Ordered list of feature names used for model training and prediction
FEATURE_NAMES = [
    "url_length",
    "hostname_length",
    "domain_length",
    "path_length",
    "num_dots",
    "num_hyphens",
    "num_digits",
    "num_special_chars",
    "digit_ratio",
    "special_char_ratio",
    "num_subdomains",
    "subdomain_length",
    "has_ip",
    "is_https",
    "has_at_symbol",
    "query_param_count",
    "is_shortened",
    "has_unusual_port",
    "has_encoded_chars",
    "domain_entropy",
    "url_entropy",
    "has_punycode",
    "is_suspicious_tld",
    "suspicious_keyword_count",
    "brand_impersonation_score",
    "suspicious_hostname_pattern"
]

SHORTENER_DOMAINS = {
    "bit.ly", "tinyurl.com", "goo.gl", "t.co", "is.gd", "cli.gs", "yfrog.com",
    "migre.me", "ff.im", "tiny.cc", "url4.eu", "twit.ac", "su.pr", "twurl.nl",
    "snipurl.com", "short.to", "budurl.com", "ping.fm", "post.ly", "just.as",
    "bkite.com", "snipr.com", "fic.kr", "loopt.us", "doiop.com", "short.ie",
    "kl.am", "wp.me", "rubyurl.com", "om.ly", "to.ly", "bit.do", "lnkd.in",
    "db.tt", "qr.ae", "adf.ly", "ity.im", "q.gs", "po.st", "bc.vc", "twitthis.com",
    "u.to", "j.mp", "buzurl.com", "cutt.us", "u.bb", "yourls.org", "prettylinkpro.com",
    "scrnch.me", "filoops.info", "vzturl.com", "qr.net", "1url.com", "tweez.me", "v.gd"
}


def calculate_entropy(text: str) -> float:
    """Calculate the Shannon entropy of a string."""
    if not text:
        return 0.0
    entropy = 0.0
    length = len(text)
    freq = {}
    for char in text:
        freq[char] = freq.get(char, 0) + 1
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)
    return round(entropy, 4)


def levenshtein_distance(s1: str, s2: str) -> int:
    """Compute Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def normalize_url(url: str) -> str:
    """Clean and normalize URL for parsing."""
    if not url:
        return ""
    url = url.strip()
    # Add scheme if missing
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
        url = "http://" + url
    return url


def is_ip_address(hostname: str) -> int:
    """Check if the hostname is an IPv4 or IPv6 address."""
    if not hostname:
        return 0
    # Strip port or brackets if any
    clean_host = hostname.split(":")[0].strip("[]")
    try:
        ipaddress.ip_address(clean_host)
        return 1
    except ValueError:
        return 0


def detect_brand_impersonation(domain: str, subdomain: str) -> tuple[float, str | None]:
    """
    Detect if target brands are being spoofed in domain or subdomains.
    Returns (score 0.0 to 1.0, matched_brand or None).
    """
    domain_lower = domain.lower()
    subdomain_lower = subdomain.lower()
    full_host = f"{subdomain_lower}.{domain_lower}".strip(".")

    for brand in Config.TARGET_BRANDS:
        # If the domain itself is the brand (e.g., paypal.com, paypal.co.uk), it's not impersonation
        if domain_lower.startswith(f"{brand}.") or domain_lower == brand:
            continue

        # Check if brand appears as a whole word or substring in subdomains or registered domain
        if brand in subdomain_lower:
            return 1.0, brand
        if brand in domain_lower:
            return 1.0, brand

        # Check typosquatting via Levenshtein distance on domain name
        domain_name = domain_lower.split(".")[0]
        if abs(len(domain_name) - len(brand)) <= 2:
            dist = levenshtein_distance(domain_name, brand)
            if dist == 1 and len(brand) >= 4:
                return 0.9, brand
            if dist == 2 and len(brand) >= 6:
                return 0.7, brand

    return 0.0, None


class FeatureExtractor:
    """Extracts features and threat indicators from normalized URLs."""

    def __init__(self):
        # Configure tldextract to use its offline bundled snapshot without network calls
        cache_dir = str(Config.INSTANCE_DIR / ".tld_cache")
        self.extractor = tldextract.TLDExtract(cache_dir=cache_dir, suffix_list_urls=None)

    def extract(self, raw_url: str) -> dict:
        """
        Extract numerical features, metadata components, and threat indicators.
        Returns a dictionary with 'features', 'vector', 'components', and 'indicators'.
        """
        url = normalize_url(raw_url)
        parsed = urlparse(url)

        # Parse domain parts with tldextract
        ext = self.extractor(parsed.netloc or parsed.path)
        subdomain = ext.subdomain
        domain_name = ext.domain
        suffix = ext.suffix
        registered_domain = f"{domain_name}.{suffix}" if suffix else domain_name
        hostname = parsed.netloc.split(":")[0] if ":" in parsed.netloc else parsed.netloc

        indicators = []

        # 1. Lexical Lengths
        url_len = len(url)
        host_len = len(hostname)
        dom_len = len(registered_domain)
        path_len = len(parsed.path)

        if url_len > 100:
            indicators.append(f"Abnormally long URL ({url_len} characters)")
        if host_len > 40:
            indicators.append(f"Suspiciously long hostname ({host_len} characters)")

        # 2. Character Counts & Ratios
        num_dots = url.count(".")
        num_hyphens = url.count("-")
        num_digits = sum(c.isdigit() for c in url)
        special_chars = set("?=&%_~+#$!*()[],;")
        num_special_chars = sum(c in special_chars for c in url)

        digit_ratio = round(num_digits / max(url_len, 1), 4)
        special_char_ratio = round(num_special_chars / max(url_len, 1), 4)

        if num_dots >= 4:
            indicators.append(f"Excessive number of dots ({num_dots} dots)")
        if num_hyphens >= 3:
            indicators.append(f"High number of hyphens ({num_hyphens} hyphens)")
        if digit_ratio > 0.25:
            indicators.append(f"High numeric character ratio ({digit_ratio * 100:.1f}%)")

        # 3. Subdomains
        subdomains_list = [s for s in subdomain.split(".") if s]
        num_subdomains = len(subdomains_list)
        subdomain_length = len(subdomain)

        if num_subdomains >= 3:
            indicators.append(f"Excessive subdomain depth ({num_subdomains} levels)")

        # 4. IP Hostname Check
        has_ip = is_ip_address(hostname)
        if has_ip:
            indicators.append("Host is a direct raw IP address instead of a registered domain")

        # 5. HTTPS Scheme
        is_https = 1 if parsed.scheme.lower() == "https" else 0
        if not is_https:
            indicators.append("Insecure plain HTTP protocol (lacks SSL/TLS)")

        # 6. '@' Symbol
        has_at = 1 if "@" in url else 0
        if has_at:
            indicators.append("URL contains '@' credential delimiter symbol")

        # 7. Query Parameters
        query_dict = parse_qs(parsed.query)
        query_param_count = len(query_dict)

        # 8. Shortener Detection
        is_shortened = 1 if hostname.lower() in SHORTENER_DOMAINS else 0
        if is_shortened:
            indicators.append("URL uses a known URL shortening / redirection service")

        # 9. Unusual Port
        has_unusual_port = 0
        if parsed.port and parsed.port not in (80, 443, 8080):
            has_unusual_port = 1
            indicators.append(f"Unusual non-standard network port ({parsed.port})")

        # 10. Encoded Characters
        has_encoded_chars = 1 if "%" in url else 0
        if has_encoded_chars:
            encoded_count = len(re.findall(r"%[0-9a-fA-F]{2}", url))
            if encoded_count >= 3:
                indicators.append(f"High volume of hex-encoded characters ({encoded_count} encoded tokens)")

        # 11. Shannon Entropy
        domain_entropy = calculate_entropy(f"{subdomain}.{domain_name}")
        url_entropy = calculate_entropy(url)

        if domain_entropy > 3.8:
            indicators.append(f"High domain entropy ({domain_entropy}) indicating algorithmic randomness / DGA")

        # 12. Punycode / IDN Homographs
        has_punycode = 1 if "xn--" in hostname.lower() or any(ord(c) > 127 for c in hostname) else 0
        if has_punycode:
            indicators.append("Punycode / IDN homograph representation detected in domain name")

        # 13. Suspicious TLD
        is_suspicious_tld = 1 if suffix.lower() in Config.SUSPICIOUS_TLDS else 0
        if is_suspicious_tld:
            indicators.append(f"Domain registered under high-abuse TLD (.{suffix})")

        # 14. Suspicious Phishing Keywords
        found_keywords = [
            kw for kw in Config.SUSPICIOUS_KEYWORDS
            if kw in parsed.path.lower() or kw in parsed.query.lower() or kw in subdomain.lower()
        ]
        suspicious_keyword_count = len(found_keywords)
        if suspicious_keyword_count > 0:
            indicators.append(f"Suspicious security/credential keywords: {', '.join(found_keywords[:4])}")

        # 15. Brand Impersonation & Typosquatting
        brand_score, impersonated_brand = detect_brand_impersonation(registered_domain, subdomain)
        if impersonated_brand:
            indicators.append(f"Suspected brand impersonation targeting '{impersonated_brand}'")

        # 16. Hostname Pattern Anomalies
        suspicious_hostname_pattern = 0
        if "--" in hostname or re.search(r"[0-9]{3,}", hostname):
            suspicious_hostname_pattern = 1
            indicators.append("Anomalous hostname pattern (multi-hyphens or continuous digit sequences)")

        # Fast-Path Whitelist check
        is_whitelisted = registered_domain.lower() in Config.TRUSTED_APEX_DOMAINS

        # Assemble feature dictionary
        features = {
            "url_length": url_len,
            "hostname_length": host_len,
            "domain_length": dom_len,
            "path_length": path_len,
            "num_dots": num_dots,
            "num_hyphens": num_hyphens,
            "num_digits": num_digits,
            "num_special_chars": num_special_chars,
            "digit_ratio": digit_ratio,
            "special_char_ratio": special_char_ratio,
            "num_subdomains": num_subdomains,
            "subdomain_length": subdomain_length,
            "has_ip": has_ip,
            "is_https": is_https,
            "has_at_symbol": has_at,
            "query_param_count": query_param_count,
            "is_shortened": is_shortened,
            "has_unusual_port": has_unusual_port,
            "has_encoded_chars": has_encoded_chars,
            "domain_entropy": domain_entropy,
            "url_entropy": url_entropy,
            "has_punycode": has_punycode,
            "is_suspicious_tld": is_suspicious_tld,
            "suspicious_keyword_count": suspicious_keyword_count,
            "brand_impersonation_score": brand_score,
            "suspicious_hostname_pattern": suspicious_hostname_pattern
        }

        # Vector ordered according to FEATURE_NAMES
        vector = [features[name] for name in FEATURE_NAMES]

        components = {
            "url": url,
            "hostname": hostname,
            "domain": registered_domain,
            "subdomain": subdomain,
            "suffix": suffix,
            "path": parsed.path,
            "query": parsed.query,
            "is_whitelisted": is_whitelisted
        }

        return {
            "features": features,
            "vector": vector,
            "components": components,
            "indicators": indicators
        }
