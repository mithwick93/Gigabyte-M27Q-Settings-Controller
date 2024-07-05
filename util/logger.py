import logging

# Create a custom logger
logger = logging.getLogger(__name__)

# Set the default logging level (this can be adjusted as needed)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# Function to retrieve the configured logger
def get_logger(name):
    return logging.getLogger(name)


# Prevent the logger from propagating messages to the root logger
logger.propagate = False
