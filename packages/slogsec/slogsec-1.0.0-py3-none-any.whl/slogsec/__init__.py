from .log import get_logger
from .secure import enable_secure_logging
from .decrypt import decrypt_secure_log

__all__ = [
    "get_logger",
    "enable_secure_logging",
    "decrypt_secure_log"
]

# Convenience
log = get_logger("slogsec")