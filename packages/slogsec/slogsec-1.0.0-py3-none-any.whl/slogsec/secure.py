from __future__ import annotations

from typing import Optional
from logcrypt import Logger as cryptlogger
from logcrypt import generate_key
from pathlib import Path

# Global secure logger instance
secure_logger = None

def enable_secure_logging(
    filename: str = "slogsec_secure.log",
    key_file: str = ".slogsec_key",
    correlation_id: Optional[str] = None,
    log_level: str = "DEBUG"
) -> cryptlogger:
    """
    Enable encrypted file logging and return a logger that writes to BOTH:
      • Beautiful colored console
      • Encrypted + checksum-protected file
    """
    global secure_logger

    key_path = Path(key_file)
    if not key_path.exists():
        generate_key(encryption_key=None, key_file=str(key_path))

    secure_logger = cryptlogger(
        file_name=filename,
        encrypt_file=True,
        key_file=str(key_path),
        log_level=log_level,
        correlation_id=correlation_id or "slogsec",
        async_logging=True,
        file_format="text"
    )

    print(f"Slogsec secure logging enabled → {filename}")
    print(f"Key stored at → {key_path.resolve()}")

    # Auto-upgrade global `log` if used
    try:
        import builtins
        if hasattr(builtins, "__slogsec_make_secure__"):
            builtins.__slogsec_make_secure__()
    except Exception:
        pass

    return secure_logger