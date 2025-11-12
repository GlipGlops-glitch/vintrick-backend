# vintrick-backend/tools/utils/logging_utils.py

import logging

def setup_logging(name: str = None, level=logging.INFO) -> logging.Logger:
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    return logging.getLogger(name)