from __future__ import annotations
from typing import Generator, Optional
from pathlib import Path

def decrypt_secure_log(
    logfile: str | Path,
    key_file: Optional[str | Path] = None,
    key: Optional[str] = None,
) -> Generator[str, None, None]:
    """
    Decrypt a slogsec-encrypted log file and yield clean, readable lines.

    Automatically finds the key if you follow the default naming convention:
        app.log → app.key  or  .slogsec_key

    Args:
        logfile: Path to the encrypted log file
        key_file: Optional explicit path to the key file
        key: Optional raw base64 key string

    Returns:
        Generator yielding decrypted plain-text log lines (str)

    Example:
        for line in slogsec.decrypt_secure_log("app_secure.log"):
            print(line)
    """
    logfile = Path(logfile)

    # Auto-detect key if not provided
    if key is None and key_file is None:
        possible_keys = [
            logfile.with_suffix(".key"),           # app_secure.log → app_secure.key
            logfile.parent / ".slogsec_key",       # hidden global key
            Path.home() / ".slogsec_key",          # user-level key
        ]
        for candidate in possible_keys:
            if candidate.exists():
                key_file = candidate
                break

    if key is None and key_file is not None:
        key = Path(key_file).read_text().strip()

    if key is None:
        raise FileNotFoundError("Encryption key not found. Provide key or key_file.")

    # Use logcrypt's battle-tested decryption + checksum verification
    decrypted_entries = decrypt_log(str(logfile), encryption_key=key)

    for entry in decrypted_entries:
        yield entry["decrypted_line"]