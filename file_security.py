"""
File Security & Forensic Inspection Layer for PhishGuard.
Performs cryptographic hashing, magic-byte MIME identification,
format-aware Shannon byte entropy, extension spoofing detection, and static heuristics.
"""
import hashlib
import math
import mimetypes
import os
import re
from pathlib import Path
from werkzeug.utils import secure_filename

# Magic Byte Signatures table for reliable offline identification
MAGIC_SIGNATURES = [
    (b"%PDF-", "application/pdf", [".pdf"]),
    (b"\x89PNG\r\n\x1a\n", "image/png", [".png"]),
    (b"\xff\xd8\xff", "image/jpeg", [".jpg", ".jpeg"]),
    (b"GIF87a", "image/gif", [".gif"]),
    (b"GIF89a", "image/gif", [".gif"]),
    (b"PK\x03\x04", "application/zip", [".zip", ".docx", ".xlsx", ".pptx", ".jar", ".apk"]),
    (b"MZ", "application/x-dosexec", [".exe", ".dll", ".sys", ".scr", ".cpl"]),
    (b"\x7fELF", "application/x-executable", [".elf", ".bin", ""]),
    (b"Rar!\x1a\x07", "application/x-rar-compressed", [".rar"]),
    (b"7z\xbc\xaf\x27\x1c", "application/x-7z-compressed", [".7z"]),
    (b"\x1f\x8b", "application/gzip", [".gz", ".tar.gz"]),
    (b"BM", "image/bmp", [".bmp"]),
    (b"\x49\x49\x2a\x00", "image/tiff", [".tif", ".tiff"]),
    (b"\x4d\x4d\x00\x2a", "image/tiff", [".tif", ".tiff"]),
    (b"\x00\x00\x01\x00", "image/x-icon", [".ico"])
]

DANGEROUS_EXTENSIONS = {
    ".exe", ".dll", ".bat", ".cmd", ".vbs", ".vbe", ".js", ".jse",
    ".wsf", ".wsh", ".ps1", ".psm1", ".scr", ".pif", ".hta", ".cpl",
    ".com", ".jar", ".iso", ".img", ".vhd"
}

COMPRESSED_OR_PACKED_FORMATS = {
    ".zip", ".docx", ".xlsx", ".pptx", ".odt", ".ods", ".odp",
    ".gz", ".tar.gz", ".tgz", ".bz2", ".7z", ".rar", ".xz",
    ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".mp4", ".mp3",
    ".jar", ".apk"
}

SUSPICIOUS_STRINGS = [
    (b"powershell", "References PowerShell scripting engine"),
    (b"cmd.exe", "References Windows Command Shell"),
    (b"WScript.Shell", "References Windows Script Host object"),
    (b"VirtualAlloc", "Contains VirtualAlloc memory allocation API (common shellcode indicator)"),
    (b"WriteProcessMemory", "Contains memory injection API"),
    (b"CreateRemoteThread", "Contains remote thread creation API"),
    (b"URLDownloadToFile", "Contains automated URL file downloader API"),
    (b"eval(", "Contains dynamic JavaScript/script eval execution"),
    (b"base64_decode", "Contains Base64 decoder payload indicator")
]

STRICT_HEADER_EXTS = {
    ".pdf": (b"%PDF-",),
    ".png": (b"\x89PNG\r\n\x1a\n",),
    ".jpg": (b"\xff\xd8\xff",),
    ".jpeg": (b"\xff\xd8\xff",),
    ".gif": (b"GIF87a", b"GIF89a"),
    ".zip": (b"PK\x03\x04",),
    ".exe": (b"MZ",)
}


def sanitize_filename(raw_filename: str) -> str:
    """Sanitize filename to prevent path traversal, null bytes, and shell tricks."""
    if not raw_filename or not raw_filename.strip():
        return "unnamed_file"

    norm = raw_filename.replace("\\", "/")
    base = os.path.basename(norm)
    clean = base.replace("\x00", "")
    safe = secure_filename(clean)
    if not safe or safe.startswith("."):
        safe = "file_" + safe.lstrip(".")
    if not safe or safe == "file_":
        return "unnamed_file"
    return safe


def compute_file_hashes(file_path: str) -> dict:
    """Compute SHA-256, SHA-1, and MD5 cryptographic hashes via streaming buffers."""
    sha256 = hashlib.sha256()
    sha1 = hashlib.sha1()
    md5 = hashlib.md5()

    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
            sha1.update(chunk)
            md5.update(chunk)

    return {
        "sha256": sha256.hexdigest(),
        "sha1": sha1.hexdigest(),
        "md5": md5.hexdigest()
    }


def calculate_file_entropy(file_path: str) -> float:
    """
    Calculate Shannon byte entropy: H = -sum(p(x) * log2(p(x)))
    Returns a float between 0.0 (homogeneous) and 8.0 (maximal disorder / packed / encrypted).
    """
    freq = {}
    total = 0

    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            for byte in chunk:
                freq[byte] = freq.get(byte, 0) + 1
            total += len(chunk)

    if total == 0:
        return 0.0

    entropy = 0.0
    for count in freq.values():
        p = count / total
        entropy -= p * math.log2(p)

    return round(entropy, 3)


def inspect_file_signatures(file_path: str, filename: str) -> dict:
    """
    Inspect magic byte signatures, format-aware byte entropy, extension spoofing,
    double extensions, and static heuristic indicators without executing the file.
    """
    file_size = os.path.getsize(file_path)
    file_ext = Path(filename).suffix.lower()

    header = b""
    with open(file_path, "rb") as f:
        header = f.read(2048)

    # 1. Match Magic Bytes
    detected_mime = "application/octet-stream"
    expected_exts = []
    matched_signature = False

    for magic, mime, exts in MAGIC_SIGNATURES:
        if header.startswith(magic):
            detected_mime = mime
            expected_exts = exts
            matched_signature = True
            break

    if not matched_signature:
        try:
            header.decode("utf-8")
            detected_mime = "text/plain"
        except UnicodeDecodeError:
            guessed, _ = mimetypes.guess_type(filename)
            detected_mime = guessed or "application/octet-stream"

    # 2. Check for Double Extension (e.g. invoice.pdf.exe)
    parts = filename.lower().split(".")
    has_double_ext = False
    if len(parts) > 2:
        penultimate = f".{parts[-2]}"
        last = f".{parts[-1]}"
        if penultimate in (".pdf", ".docx", ".xlsx", ".png", ".jpg", ".txt") and last in DANGEROUS_EXTENSIONS:
            has_double_ext = True

    # 3. Check for Extension Spoofing
    is_spoofed = False
    if matched_signature and expected_exts:
        if file_ext and file_ext not in expected_exts:
            is_spoofed = True

    if not is_spoofed and file_ext in STRICT_HEADER_EXTS:
        valid_sigs = STRICT_HEADER_EXTS[file_ext]
        if not any(header.startswith(s) for s in valid_sigs):
            is_spoofed = True

    # 4. Check for Executable Binary Type
    is_executable = (
        file_ext in DANGEROUS_EXTENSIONS
        or detected_mime in ("application/x-dosexec", "application/x-executable")
    )

    # 5. Format-Aware Shannon Byte Entropy Analysis
    entropy = calculate_file_entropy(file_path)
    is_naturally_compressed = (
        file_ext in COMPRESSED_OR_PACKED_FORMATS
        or detected_mime in (
            "application/pdf", "application/zip", "image/png",
            "image/jpeg", "application/x-gzip", "application/x-7z-compressed"
        )
    )

    is_suspicious_entropy = False
    entropy_explanation = ""

    if is_naturally_compressed:
        # High entropy (7.2 - 8.0) is normal for Deflate, LZMA, and media compression
        is_suspicious_entropy = False
        entropy_explanation = (
            f"Shannon byte entropy is {entropy}/8.0 bits. This is expected and normal for "
            f"compressed or stream formats ({detected_mime}); stream compression naturally "
            f"maximizes byte dispersion without indicating malicious obfuscation."
        )
    elif is_executable:
        if entropy >= 7.5:
            is_suspicious_entropy = True
            entropy_explanation = (
                f"Elevated byte entropy ({entropy}/8.0 bits) in an executable binary. "
                "Often observed in packed (e.g. UPX), encrypted, or obfuscated payloads."
            )
        else:
            entropy_explanation = (
                f"Byte entropy is {entropy}/8.0 bits, within standard distribution for compiled binaries."
            )
    else:
        # Plain text, scripts, or uncompressed formats
        if entropy >= 7.0:
            is_suspicious_entropy = True
            entropy_explanation = (
                f"High byte entropy ({entropy}/8.0 bits) in a text or script format. "
                "May indicate embedded base64 payloads, encrypted shellcode, or hidden binary blobs."
            )
        else:
            entropy_explanation = (
                f"Byte entropy is {entropy}/8.0 bits, within expected parameters for uncompressed text/data."
            )

    # 6. Static String Indicators
    found_suspicious_strings = []
    for pattern, desc in SUSPICIOUS_STRINGS:
        if pattern.lower() in header.lower():
            found_suspicious_strings.append(desc)

    # 7. Build Structured Forensic Findings & Legacy String Indicators
    structured_findings = []
    threat_indicators = []

    # Finding: Format Signature
    if is_spoofed:
        f_spoof = {
            "category": "Header Verification",
            "title": "Extension Masquerading / Spoofing",
            "severity": "threat",
            "evidence": f"Declared: '{file_ext}' vs. Header Signature: '{detected_mime}'",
            "explanation": "File header magic bytes do not match the declared extension. This evasion tactic is commonly used to bypass user suspicion."
        }
        structured_findings.append(f_spoof)
        threat_indicators.append(f"File Extension Spoofing Detected: Claimed '{file_ext}' but header is {detected_mime}")
    else:
        structured_findings.append({
            "category": "Header Verification",
            "title": "Signature Format Integrity",
            "severity": "clean",
            "evidence": f"Header conforms to {detected_mime} specifications",
            "explanation": "Binary header magic bytes are consistent with the declared file type."
        })

    # Finding: Double Extension
    if has_double_ext:
        f_dext = {
            "category": "Filename Analysis",
            "title": "Deceptive Double Extension",
            "severity": "threat",
            "evidence": f"Filename: '{filename}'",
            "explanation": "Multiple extensions detected attempting to disguise an executable as a document."
        }
        structured_findings.append(f_dext)
        threat_indicators.append(f"Deceptive double extension detected ({filename})")

    # Finding: Entropy
    structured_findings.append({
        "category": "Byte Distribution",
        "title": "High Entropy (Compressed Stream)" if is_naturally_compressed else ("Suspicious Byte Entropy" if is_suspicious_entropy else "Standard Byte Entropy"),
        "severity": "warning" if is_suspicious_entropy else "info",
        "evidence": f"{entropy} / 8.0 bits (Scale: 0.0 - 8.0)",
        "explanation": entropy_explanation
    })
    if is_suspicious_entropy:
        threat_indicators.append(f"Elevated byte entropy ({entropy}/8.0) indicating potential packing or obfuscation")

    # Finding: Embedded Strings
    for s in found_suspicious_strings:
        structured_findings.append({
            "category": "Static Heuristics",
            "title": "Suspicious Code Pattern",
            "severity": "warning",
            "evidence": s,
            "explanation": "Found embedded references to system scripting or low-level memory allocation functions."
        })
        threat_indicators.append(f"Suspicious embedded signature: {s}")

    return {
        "filename": filename,
        "file_size": file_size,
        "extension": file_ext,
        "detected_mime": detected_mime,
        "entropy": entropy,
        "is_executable": is_executable,
        "is_spoofed": is_spoofed,
        "has_double_ext": has_double_ext,
        "is_naturally_compressed": is_naturally_compressed,
        "is_suspicious_entropy": is_suspicious_entropy,
        "entropy_explanation": entropy_explanation,
        "threat_indicators": threat_indicators,
        "structured_findings": structured_findings
    }
