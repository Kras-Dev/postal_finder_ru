# custom_logger.py

import logging
import inspect

class CustomLogger:
    def __init__(self, name):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(name)

    def log_with_context(self, message):
        stack = inspect.stack()
        caller_function = stack[1].function
        self.logger.info(f"{message} (called from {caller_function})")
