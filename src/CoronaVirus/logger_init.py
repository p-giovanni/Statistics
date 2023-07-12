
import os
import sys

import logging
from logging.handlers import RotatingFileHandler

# ----------------------------------------
# init_logger
# ----------------------------------------
def init_logger(log_dir:str, file_name:str, log_level, std_out_log_level=logging.ERROR) -> None :
    """
    Logger initializzation for file logging and stdout logging with
    different level.

    :param log_dir: path for the logfile;
    :param log_level: logging level for the file logger;
    :param std_out_log_level: logging level for the stdout logger;
    :return:
    """
    root = logging.getLogger()
    dap_format = '%(asctime)s %(levelname)s %(name)s %(message)s'
    formatter = logging.Formatter(dap_format)
    # File logger.
    root.setLevel(logging.DEBUG)
    fh = RotatingFileHandler(os.path.join(log_dir, file_name), maxBytes=1000000, backupCount=5)
    fh.setLevel(log_level)
    fh.setFormatter(formatter)
    root.addHandler(fh)

    # Stdout logger.
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(std_out_log_level)
    ch.setFormatter(formatter)
    root.addHandler(ch)

    for _ in ("urllib3", "urllib3.connectionpool", "matplotlib", "chardet"):
        logging.getLogger(_).setLevel(logging.CRITICAL)

