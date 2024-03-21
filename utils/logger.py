import logging


def configure_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s - %(asctime)s - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
        handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()],
    )


# Call the function to configure the logger
configure_logger()

# Define a global variable for the logger
logger = logging.getLogger(__name__)
