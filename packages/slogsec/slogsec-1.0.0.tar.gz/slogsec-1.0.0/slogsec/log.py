import logging
import colorlog

def _create_colored_handler():
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s %(name)s %(levelname)8s │ %(message)s",
        datefmt="%H:%M:%S",
        log_colors={
            "DEBUG":    "cyan",
            "INFO":     "green",
            "WARNING":  "yellow",
            "ERROR":    "red",
            "CRITICAL": "bold_red",
            "SUCCESS":  "bold_green",
            "FAIL":     "bold_red",
        }
    ))
    return handler

class ClogAdapter(logging.LoggerAdapter):
    def __init__(self, name: str):
        logger = logging.getLogger(name)
        if not logger.handlers:
            logger.addHandler(_create_colored_handler())
        logger.setLevel(logging.DEBUG)
        super().__init__(logger, {})

    def success(self, msg, *args, **kwargs):
        self.log(25, msg, *args, **kwargs)

    def fail(self, msg, *args, **kwargs):
        self.log(45, msg, *args, **kwargs)

def get_logger(name: str = "slogsec") -> ClogAdapter:
    return ClogAdapter(name)