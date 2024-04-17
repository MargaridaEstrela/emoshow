import logging


class SimonSaysLogger:
    """
    A class representing the logger class for the Simon Says game.

    Attributes:
        log_file (str): The name of the log file.
        logger (object): The logger object.

    Methods:
        log_message(message): Logs a debug message with the provided message.
        log_error(message): Logs an error message with the provided message.
        close(): Closes the file handler and shuts down the logging system.
    """

    def __init__(self, log_file="simon_says.log"):
        self.log_file = log_file
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        self.handler = logging.FileHandler(self.log_file)
        self.handler.setFormatter(formatter)
        self.logger.addHandler(self.handler)

    def log_message(self, message):
        """
        Logs a debug message with the provided message.

        Args:
            message (str): The message to be logged.
        """
        try:
            self.logger.debug(f"{message}")
        except Exception as e:
            self.logger.error(f"Error logging message: {e}")

    def log_error(self, message):
        """
        Logs an error message with the provided message.

        Args:
            message (str): The error message to be logged.
        """
        try:
            self.logger.error(f"{message}")
        except Exception as e:
            self.logger.error(f"Error logging error message: {e}")

    def close(self):
        """
        Closes the file handler and shuts down the logging system.
        """
        self.handler.close()
        logging.shutdown()
