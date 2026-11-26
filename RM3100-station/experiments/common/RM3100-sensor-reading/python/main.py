from datetime import datetime

from .utils import path_file, config_load, config_logging, logging_info, logging_title
from .data import conect_mc

def main():
    """
    """
    paths = path_file()
    cfg = config_load(paths)
    config_logging(paths)

    debug_mode = cfg["logging"]["debug_mode"]
    cycle_count = cfg["cycle_count"]

    logging_title(debug_mode, title = f"Reading data in {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", detail = f"Cycle Count = {cycle_count}   |   Address 0x{cfg['RM3100_address']:02X}")

    logging_info(debug_mode, msg = f"Connecting...")
    conect_mc(cfg, paths, logging_info)


if __name__ == "__main__":
    main()