import os

from SysGuard.config import REVIEW_WORTHY_EXTENSIONS, SCRIPT_EXTENSIONS, SMALL_EXECUTABLE_SIZE_BYTES


TEXT_SAMPLE_BYTES = 8192
MACHO_HEADERS = [
    b"\xcf\xfa\xed\xfe",
    b"\xfe\xed\xfa\xcf",
    b"\xca\xfe\xba\xbe",
    b"\xbe\xba\xfe\xca",
]


def normalize_lower(path):
    return (path or "").lower()


def is_script_path(path):
    normalized_path = normalize_lower(path)
    return any(normalized_path.endswith(extension) for extension in SCRIPT_EXTENSIONS)


def is_review_worthy_path(path):
    normalized_path = normalize_lower(path)
    return any(normalized_path.endswith(extension) for extension in REVIEW_WORTHY_EXTENSIONS)


def read_file_bytes(path, size=TEXT_SAMPLE_BYTES):
    try:
        with open(path, "rb") as file:
            return file.read(size)
    except (FileNotFoundError, PermissionError, IsADirectoryError, OSError):
        return None


def decode_text(data):
    if not data:
        return ""

    try:
        return data.decode("utf-8", errors="ignore")
    except Exception:
        return ""


def looks_like_binary(data):
    if not data:
        return False

    if any(data.startswith(header) for header in MACHO_HEADERS):
        return True

    return b"\x00" in data


def inspect_file(path):
    if not path:
        return []
    if not os.path.exists(path):
        return []
    if not os.path.isfile(path):
        return []

    findings = []
    file_size = os.path.getsize(path)
    file_bytes = read_file_bytes(path)
    text_sample = decode_text(file_bytes)
    is_binary = looks_like_binary(file_bytes)

    if is_review_worthy_path(path) and file_size <= SMALL_EXECUTABLE_SIZE_BYTES:
        findings.append({
            "type": "small_executable",
            "target": path,
            "details": {
                "reason": "Executable-like file is unusually small.",
                "size_bytes": file_size,
            },
        })

    if is_script_path(path) or text_sample.startswith("#!"):
        lowered = text_sample.lower()

        if "curl " in lowered or "wget " in lowered:
            findings.append({
                "type": "network_enabled_script",
                "target": path,
                "details": {
                    "reason": "Script contains network download commands.",
                    "size_bytes": file_size,
                },
            })

        if "base64" in lowered:
            findings.append({
                "type": "base64_encoded_script",
                "target": path,
                "details": {
                    "reason": "Script references base64, which can indicate obfuscation.",
                    "size_bytes": file_size,
                },
            })

        if text_sample.startswith("#!/bin/bash") or text_sample.startswith("#!/bin/sh"):
            findings.append({
                "type": "shell_script_detected",
                "target": path,
                "details": {
                    "reason": "Shell script shebang detected.",
                    "size_bytes": file_size,
                },
            })

    if is_binary and is_review_worthy_path(path) and file_size <= SMALL_EXECUTABLE_SIZE_BYTES:
        for finding in findings:
            if finding["type"] == "small_executable":
                finding["details"]["binary_header_detected"] = True
                break

    return findings
