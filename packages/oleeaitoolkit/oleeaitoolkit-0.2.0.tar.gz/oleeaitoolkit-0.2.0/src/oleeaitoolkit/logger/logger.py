
import logging
import sys

# Create a custom logger
logger = logging.getLogger("oleeaitoolkit")
logger.setLevel(logging.DEBUG)  # Capture all levels DEBUG and above

# Create handlers
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)  # Log all levels to console

# Create formatters and add them to handlers
formatter = logging.Formatter(
    fmt="[%(levelname)s] %(asctime)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
console_handler.setFormatter(formatter)

# Add the handler to the logger
if not logger.hasHandlers():
    logger.addHandler(console_handler)

# Optional: convenience functions like JS style
def info(*args):
    logger.info(" ".join(str(a) for a in args))

def error(*args):
    logger.error(" ".join(str(a) for a in args))

def warn(*args):
    logger.warning(" ".join(str(a) for a in args))

def debug(*args):
    logger.debug(" ".join(str(a) for a in args))

def log(*args):
    logger.info(" ".join(str(a) for a in args))
