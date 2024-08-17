import time
import logging

log_path = f"../{__name__}.log"
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, filename=log_path, filemode="a",
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.info(f"{func.__name__} took {end - start} seconds to execute")
        return result

    return wrapper
