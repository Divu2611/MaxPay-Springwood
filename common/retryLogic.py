# Importing Libraries
import time
from functools import wraps


# Defining a retry logic
def retry(attempts, interval_list):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == attempts - 1:
                        raise e
                    interval = interval_list[i]
                    time.sleep(interval)

        return wrapper

    return decorator
