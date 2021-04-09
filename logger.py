import logging


class Logger:
    
    """ Logger class
    """
    
    def __init__(self, logger_name: str, file: str, level=logging.DEBUG) -> None:
        
        """ Initialise Loger
        Args:
            logger_name (str): Logger name
            file (str): File to save logging information to
            level (int, optional): Logging level. Defaults to logging.DEBUG.
        """

        self._log = logging.getLogger(logger_name)
        self._log.propagate = False
        self._log.setLevel(level)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        fh = logging.FileHandler(file)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        self._log.addHandler(fh)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        self._log.addHandler(ch)


    def debug(self, message: str):

        """ Debug log message
        Args:
            message (str): Log message
        """

        self._log.debug(message)
        self._exit()


    def info(self, message: str):

        """ Info log message
        Args:
            message (str): Log message
        """

        self._log.info(message)
        self._exit()


    def warning(self, message: str):

        """ Warning log message
        Args:
            message (str): Log message
        """

        self._log.warning(message)
        self._exit()

    
    def error(self, message: str):

        """ Error log message
        Args:
            message (str): Log message
        """

        self._log.error(message)
        self._exit()


    def _exit(self):

        """ Clear log handlers
        """
        
        if self._log.hasHandlers():
            self._log.handlers.clear()