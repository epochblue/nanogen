import logging

log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)

file_log_handler = logging.FileHandler('nanogen.log')
log.addHandler(file_log_handler)

stdout_log_handler = logging.StreamHandler()
log.addHandler(stdout_log_handler)

format_string = '%(levelname)s: %(message)s'
formatter = logging.Formatter(format_string)
file_log_handler.setFormatter(formatter)
stdout_log_handler.setFormatter(formatter)
