import logging
import os
import requests

from boxing.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


RANDOM_ORG_URL = os.getenv("RANDOM_ORG_URL",
                            "https://www.random.org/decimal-fractions/?num=1&dec=2&col=1&format=plain&rnd=new")


def get_random() -> float:
    """
    Fetches a random integer from random.org.

    Returns:
        int: a random integer

    Raises:
        ValueError: Invalid response from random.org
        RuntimeError: timeout or failed request from random.org
    """
    logger.info(f"Attempting to retreive a random integer from random.org")
    try:
        response = requests.get(RANDOM_ORG_URL, timeout=5)

        # Check if the request was successful
        response.raise_for_status()

        random_number_str = response.text.strip()

        try:
            random_number = float(random_number_str)
        except ValueError:
            logger.info(f"Invalid response from random.org: {random_number_str}")
            raise ValueError(f"Invalid response from random.org")
        logger.info("Successfully retreived and returned random number")
        return random_number

    except requests.exceptions.Timeout:
        logger.info("Request to random.org timed out.")
        raise RuntimeError("Request to random.org timed out.")

    except requests.exceptions.RequestException as e:
        logger.info(f"Request to random.org failed: {e}")
        raise RuntimeError(f"Request to random.org failed: {e}")
