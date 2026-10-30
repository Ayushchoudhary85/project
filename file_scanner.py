"""
File Virus Scanner Engine for PhishGuard.
Integrates ClamAV subprocess scanning when available, with
format-aware static heuristic inspection and graceful fallback handling.
"""
import os
import platform
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from config import Config
from file_security import (
    sanitize_filename, compute_file_hashes, inspect_file_signatures
)


def get_candidate_clamav_paths() -> list[str]:
    """Return standard candidate paths for ClamAV binaries across operating systems."""
    system = platform.system()
    candidates = []

    if system == "Windows":
        candidates.extend([
            r"C:\Program Files\ClamAV\clamscan.exe",
            r"C:\Program Files (x86)\ClamAV\clamscan.exe",
            r"C:\ProgramData\chocolatey\bin\clamscan.exe",
            r"C:\tools\clamav\clamscan.exe",
            r"C:\clamav\clamscan.exe",
        ])
    elif system == "Darwin":
        candidates.extend([
            "/opt/homebrew/bin/clamscan",
            "/usr/local/bin/clamscan",
            "/usr/bin/clamscan"
        ])
    else:  # Linux / Unix
        candidates.extend([
            "/usr/bin/clamscan",
            "/usr/local/bin/clamscan",
            "/bin/clamscan"
        ])

    return candidates


def check_clamav_availability(clamav_cmd: str = None) -> dict:
    """
    Check whether ClamAV scanner binary is installed, accessible, and functional.
    Returns diagnostic details and OS-specific setup guidance if missing.
    """
    system = platform.system()
    cmd = clamav_cmd or Config.CLAMAV_PATH
    binary_path = shutil.which(cmd)

    # If not in PATH, probe standard operating system installation locations
    if not binary_path:
        for candidate in get_candidate_clamav_paths():
            if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                binary_path = candidate
                break

    if not binary_path:
        if system == "Windows":
            cmd_guide = "winget install ClamAV.ClamAV"
            steps = [
                "1. Open PowerShell as Administrator and run: winget install ClamAV.ClamAV",
                "2. Open the ClamAV directory and run 'freshclam.exe' to download virus definitions",
                "3. In PhishGuard Settings, ensure the executable path points to clamscan.exe"
            ]
        elif system == "Darwin":
            cmd_guide = "brew install clamav && freshclam"
            steps = [
                "1. Install via Homebrew: brew install clamav",
                "2. Initialize signatures by executing: freshclam",
                "3. Verify binary with: which clamscan"
            ]
        else:
            cmd_guide = "sudo apt update && sudo apt install -y clamav clamav-daemon && sudo freshclam"
            steps = [
                "1. Install packages: sudo apt install -y clamav clamav-daemon",
                "2. Update database signatures: sudo freshclam",
                "3. Verify installation: clamscan --version"
            ]

        return {
            "available": False,
            "status": "not_installed",
            "version": None,
            "path": None,
            "os": system,
            "install_guide": {
                "os": system,
                "command": cmd_guide,
                "steps": steps
            },
            "message": f"ClamAV is not installed or not found in system PATH on this {system} host."
        }

    # Verify execution via version flag
    try:
        proc = subprocess.run(
            [binary_path, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False
        )
        if proc.returncode == 0:
            version_str = proc.stdout.strip().split("\n")[0]
            return {
                "available": True,
                "status": "ready",
                "version": version_str,
                "path": binary_path,
                "os": system,
                "install_guide": None,
                "message": f"ClamAV engine active ({version_str})"
            }
        else:
            return {
                "available": False,
                "status": "error",
                "version": None,
                "path": binary_path,
                "os": system,
                "install_guide": None,
                "message": f"ClamAV version check failed (Exit code {proc.returncode})"
            }
    except subprocess.TimeoutExpired:
        return {
            "available": False,
            "status": "timeout",
            "version": None,
            "path": binary_path,
            "os": system,
            "install_guide": None,
            "message": "ClamAV binary probe timed out."
        }
    except Exception as e:
        return {
            "available": False,
            "status": "error",
            "version": None,
            "path": binary_path,
            "os": system,
            "install_guide": None,
            "message": f"ClamAV execution failure: {str(e)}"
        }


def run_clamav_scan(file_path: str, binary_path: str) -> dict:
    """
    Execute ClamAV scan on an isolated file via safe subprocess with a strict timeout.
    Exit codes:
      0 = No virus found
      1 = Virus(es) found
      2 = Error occurred
    """
    try:
        proc = subprocess.run(
            [binary_path, "--no-summary", file_path],
            capture_output=True,
            text=True,
            timeout=30,
            check=False
        )

        output = proc.stdout.strip() or proc.stderr.strip()

        if proc.returncode == 0:
            return {
                "status": "Clean",
                "infected": False,
                "threat_name": None,
                "raw_output": output
            }
        elif proc.returncode == 1:
            threat_name = "Malicious Payload"
            if "FOUND" in output:
                match = output.split("FOUND")[0].split(":")[-1].strip()
                if match:
                    threat_name = match
            return {
                "status": "Malicious",
                "infected": True,
                "threat_name": threat_name,
                "raw_output": output
            }
        else:
            return {
                "status": "Scan Error",
                "infected": False,
                "threat_name": None,
                "raw_output": f"ClamAV scanner exit code {proc.returncode}: {output}"
            }
    except subprocess.TimeoutExpired:
        return {
            "status": "Scan Error",
            "infected": False,
            "threat_name": None,
            "raw_output": "Antivirus signature scan timed out (exceeded 30-second limit)."
        }
    except Exception as e:
        return {
            "status": "Scan Error",
            "infected": False,
            "threat_name": None,
            "raw_output": f"Subprocess execution failure: {str(e)}"
        }


def scan_file_buffer(file_storage, custom_clamav_path: str = None) -> dict:
    """
    Full pipeline to inspect an uploaded file:
    1. Sanitize filename.
    2. Stream to isolated temporary directory.
    3. Compute cryptographic hashes (SHA-256, SHA-1, MD5).
    4. Run format-aware static heuristics & magic-byte signature check.
    5. Run ClamAV if available, or fallback gracefully with explicit limited analysis status.
    6. Generate evidence-based findings and recommendations.
    7. Securely delete temporary file immediately.
    """
    original_name = getattr(file_storage, "filename", "unnamed_file")
    safe_name = sanitize_filename(original_name)

    temp_dir = tempfile.mkdtemp(prefix="phishguard_scan_")
    temp_path = os.path.join(temp_dir, safe_name)

    try:
        # Save securely to temporary path
        file_storage.save(temp_path)
        file_size = os.path.getsize(temp_path)

        # Enforce size limit
        if file_size > Config.MAX_CONTENT_LENGTH:
            raise ValueError(f"File exceeds maximum permissible upload size ({Config.MAX_CONTENT_LENGTH // (1024 * 1024)} MB).")

        # 1. Cryptographic Hashes
        hashes = compute_file_hashes(temp_path)

        # 2. Format-Aware Heuristic and Signature Inspection
        heuristics = inspect_file_signatures(temp_path, safe_name)

        # 3. Antivirus Engine Check
        clam_info = check_clamav_availability(custom_clamav_path)
        indicators = list(heuristics["threat_indicators"])
        structured_findings = list(heuristics["structured_findings"])
        recommendations = []

        if clam_info["available"]:
            # Run ClamAV Signature Scan
            clam_res = run_clamav_scan(temp_path, clam_info["path"])
            engine_used = clam_info["version"] or "ClamAV Active"

            if clam_res["status"] == "Malicious":
                status = "Malicious"
                risk_score = 95
                threat_name = clam_res["threat_name"]
                antivirus_status = f"Threat Detected: {threat_name}"
                indicators.insert(0, f"ClamAV Signature Detection: {threat_name}")
                structured_findings.insert(0, {
                    "category": "Antivirus Engine",
                    "title": "Malware Signature Match",
                    "severity": "threat",
                    "evidence": f"Detection: {threat_name}",
                    "explanation": "File matched a known malware signature in the ClamAV signature database."
                })
                recommendations.append("DO NOT open, execute, or distribute this file.")
                recommendations.append("Quarantine or permanently delete the file immediately.")
                recommendations.append("Isolate any host endpoint that may have received or opened this file.")
            elif clam_res["status"] == "Scan Error":
                status = "Scan Error"
                risk_score = 50
                threat_name = None
                antivirus_status = "Scan Error"
                indicators.append(clam_res["raw_output"])
                structured_findings.append({
                    "category": "Antivirus Engine",
                    "title": "Antivirus Engine Error",
                    "severity": "warning",
                    "evidence": clam_res["raw_output"],
                    "explanation": "The signature engine encountered an internal execution error."
                })
                recommendations.append("Antivirus scan did not complete cleanly; re-scan or inspect manually.")
            else:
                # ClamAV reported Clean, check if heuristic anomalies were found
                antivirus_status = "Clean (No Known Signatures Found)"
                structured_findings.insert(0, {
                    "category": "Antivirus Engine",
                    "title": "Signature Scan Completed",
                    "severity": "clean",
                    "evidence": "ClamAV database lookup: Negative",
                    "explanation": "No known virus or trojan signatures matched."
                })

                if heuristics["is_spoofed"] or heuristics["has_double_ext"]:
                    status = "Suspicious"
                    risk_score = 70
                    threat_name = "Deceptive Extension / Masqueraded File"
                    recommendations.append("File passed virus signature scanning, but exhibits extension masquerading.")
                    recommendations.append("Verify the original source before trusting or opening this file.")
                else:
                    status = "Clean"
                    risk_score = 5
                    threat_name = None
                    recommendations.append("No known virus signatures or structural format anomalies detected.")
                    recommendations.append("Maintain standard endpoint security and verify origin before execution.")
        else:
            # ClamAV is UNAVAILABLE - NEVER report Clean falsely!
            engine_used = "Static Heuristic Inspector (ClamAV Offline)"
            antivirus_status = "Offline (ClamAV Not Installed)"

            structured_findings.insert(0, {
                "category": "Antivirus Engine",
                "title": "Signature Scanning Offline",
                "severity": "warning",
                "evidence": clam_info["message"],
                "explanation": "ClamAV is not installed on this host. Signature-based virus detection was skipped; analysis is limited to static byte heuristics."
            })

            if heuristics["is_spoofed"] or heuristics["has_double_ext"]:
                status = "Suspicious"
                risk_score = 75
                threat_name = "Extension Spoofing / Structural Masquerading"
                recommendations.append("Structural deception detected (e.g. extension spoofing or double extensions).")
                recommendations.append("Do not open or execute this file; it disguises its true binary payload.")
            elif heuristics["is_suspicious_entropy"]:
                status = "Suspicious"
                risk_score = 55
                threat_name = "Anomalous Byte Entropy"
                recommendations.append("File exhibits elevated entropy in an uncompressed format (potential packed payload).")
                recommendations.append("Inspect file in an isolated virtualized sandbox before running.")
            else:
                status = "Limited Analysis"
                risk_score = 15
                threat_name = None
                indicators.append("Antivirus engine unavailable: File underwent static heuristic analysis only.")
                recommendations.append("ClamAV signature database scanning was offline; file cannot be guaranteed clean.")
                recommendations.append("Install ClamAV to enable automated malware signature verification.")

        return {
            "filename": safe_name,
            "original_filename": original_name,
            "file_size": file_size,
            "mime_type": heuristics["detected_mime"],
            "sha256": hashes["sha256"],
            "sha1": hashes["sha1"],
            "md5": hashes["md5"],
            "status": status,
            "risk_score": risk_score,
            "threat_name": threat_name,
            "engine_used": engine_used,
            "antivirus_status": antivirus_status,
            "clam_info": clam_info,
            "entropy": heuristics["entropy"],
            "is_executable": heuristics["is_executable"],
            "is_spoofed": heuristics["is_spoofed"],
            "has_double_ext": heuristics["has_double_ext"],
            "is_naturally_compressed": heuristics["is_naturally_compressed"],
            "is_suspicious_entropy": heuristics["is_suspicious_entropy"],
            "entropy_explanation": heuristics["entropy_explanation"],
            "threat_indicators": indicators,
            "structured_findings": structured_findings,
            "recommendations": recommendations,
            "clamav_available": clam_info["available"],
            "scan_timestamp": datetime.now(timezone.utc).isoformat()
        }

    finally:
        # Secure cleanup: remove file and temp directory
        try:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass
