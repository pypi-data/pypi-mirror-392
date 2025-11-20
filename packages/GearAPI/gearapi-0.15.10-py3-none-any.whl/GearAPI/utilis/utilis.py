import time
from functools import wraps
from http.client import RemoteDisconnected
from requests import ConnectionError, HTTPError, RequestException
from urllib3.exceptions import ProtocolError
import re

def retry(attempts=3, delay=2, backoff=2, exceptions=(TimeoutError, ConnectionError, HTTPError, RequestException, ProtocolError, RemoteDisconnected), on_error=None):

    """
    Retry decorator for synchronous functions with exponential backoff.

    Parameters:
    - attempts: Maximum number of retries.
    - delay: Initial delay between retries in seconds.
    - backoff: Factor by which the delay is multiplied on each retry.
    - exceptions: Tuple of exceptions to catch and retry on.
    - on_error: Optional function to call on error with the exception and attempt number as arguments.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal delay
            current_delay = delay  # Initialize current_delay to the initial delay

            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if on_error:
                        on_error(e, attempt)
                    if attempt < attempts:
                        time.sleep(current_delay)
                        current_delay *= backoff  # Increment the delay for the next attempt
                    else:
                        raise
        return wrapper
    return decorator

def remove_empty_params(data:dict) -> dict:
    """
    remove empty dict's values. Sometimes, to eliminate behavior where empty value is treated as True in ThingsCloud API. 
    """
    return {k: v for k, v in data.items() if v is not None}


def validate_date_str(date: str) -> None:
    """
    Validate that the input date is in the YYYY-MM-DD format.

    Args:
    date (DateString): The date string to validate.

    Returns:
    DateString: The validated date string.

    Raises:
    ValueError: If the date is not in the correct format.
    """
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date):
        raise ValueError(f"Date {date} is not in YYYY-MM-DD format")
    

def validate_datetime_str(datetime_str: str) -> None:
    """
    Validate that the input datetime string is in the format YYYY-MM-DDTHH:MM:SS.sssZ.

    Args:
    datetime_str (str): The datetime string to validate.

    Returns:
    None

    Raises:
    ValueError: If the datetime string is not in the correct format.
    """
    # Regular expression for the format YYYY-MM-DDTHH:MM:SS.sssZ
    pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$'
    
    if not re.match(pattern, datetime_str):
        raise ValueError(f"Datetime {datetime_str} is not in the correct format YYYY-MM-DDTHH:MM:SS.sssZ")