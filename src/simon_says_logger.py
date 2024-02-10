import logging

class SimonSaysLogger:
    def __init__(self, log_file='simon_says.log'):
        self.log_file = log_file
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.handler = logging.FileHandler(self.log_file)
        self.handler.setFormatter(formatter)
        self.logger.addHandler(self.handler)

    def log_message(self, message):
        try:
            self.logger.debug(f"{message}")
        except Exception as e:
            self.logger.error(f"Error logging message: {e}")

    def close(self):
        self.handler.close()
        logging.shutdown()