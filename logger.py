import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(message)s",
    filename="debug.log",
    filemode="w",
)

logger = logging.getLogger(__name__)
