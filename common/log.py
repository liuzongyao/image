from common import settings
import logging
import os


class Logging(object):
    @classmethod
    def get_logger(cls):
        level = getattr(logging, settings.LOG_LEVEL, logging.INFO)
        if not os.path.exists(settings.LOG_PATH):
            os.mkdir(settings.LOG_PATH)
        log_path = "{}/{}".format(settings.LOG_PATH, "pytest.log")
        cls.logger = cls.create_logger('api-test', level, log_path)
        return cls.logger

    @classmethod
    def create_logger(cls, name, level, log_path):
        logger = logging.getLogger(name)
        logger.setLevel(level)

        if not logger.handlers:
            formatter = logging.Formatter(
                '%(asctime)s - %(filename)s - [%(levelname)s]'
                + '[%(lineno)d] %(message)s')
            file_handler = logging.FileHandler(log_path)
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            formatter = logging.Formatter('>  %(message)s')
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        return logger
