import logging
import os
from logging.handlers import TimedRotatingFileHandler

log_directory = "logs"
log_file = "app.log"

if not os.path.exists(log_directory):
    os.makedirs(log_directory)

file_handler = TimedRotatingFileHandler(
    filename=os.path.join(log_directory, log_file),
    when="midnight",
    interval=1,
    backupCount=10,
    encoding="utf-8"
)
file_handler.setLevel(logging.DEBUG)
file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_format)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(file_format)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def get_logger(name):
    return logging.getLogger(name)
