from logging import handlers

def configure_file_log_handler(fpath, level=logging.INFO, max_file_size=5000000, num_backups=10):
    handler = handlers.RotatingFileHandler(fpath, maxBytes=max_file_size, backupCount=num_backups)
    formatter = logging.Formatter('[%(asctime)s] --- [%(levelname)5s] --- %(message)s')
    handler.setFormatter(formatter)
    handler.setLevel(level)
    return handler


def add_stream_log_handler(logger_id, log_level=logging.INFO):
    logger = logging.getLogger(logger_id)
    logger.setLevel(log_level)
    logger.addHandler(logging.StreamHandler())


def add_file_log_handlers(logger_id, fpath, log_level=logging.INFO, max_file_size=5000000, num_backups=10):
    logger = logging.getLogger(logger_id)
    logger.setLevel(log_level)
    logger.addHandler(configure_file_log_handler(fpath, log_level, max_file_size, num_backups))


def init_stream_loggers(log_level=logging.INFO):
    for logger_id in logger_ids:
        add_stream_log_handler(logger_id, log_level=log_level)


def init_file_loggers(fpath, log_level=logging.INFO):
    for logger_id in logger_ids:
        add_file_log_handlers(logger_id, fpath, log_level=log_level)