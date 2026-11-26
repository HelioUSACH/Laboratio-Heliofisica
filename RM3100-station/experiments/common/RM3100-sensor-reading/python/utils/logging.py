import sys
import logging
from pathlib import Path

def config_logging(paths: dict):
    """
    Configure the logging system with file output and cmd
    """
    log_file = paths["log_file"]

    logging.basicConfig(
        level = logging.INFO,
        format = '%(asctime)s - %(levelname)s - %(message)s',
        handlers = [
            logging.FileHandler(log_file / "process.log", mode = "a", encoding = "utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )


def logging_info(debug_mode: bool, msg: str):
    if debug_mode:
        logging.info(msg)


def logging_title(debug_mode: bool, title: str, detail: str = ""):
    if debug_mode:
        width = 70
        logging.info("="*width)
        logging.info(title.center(width))

        if detail:
            logging.info(detail.center(width))

        logging.info("="*width)