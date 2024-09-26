import logging

LOGGING_LEVEL = logging.INFO

logger = logging.getLogger(__name__)
logger.setLevel(LOGGING_LEVEL)
file_handler = logging.FileHandler('read_sas.log')
file_handler.setLevel(LOGGING_LEVEL)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
