# Importing Python libraries
import logging
from rest_framework import status

# Importing Project Files
from . import generatingResponse

db_logger = logging.getLogger("db")


# methodChecker - generates the error response if method not supported for the requested resource.
def methodChecker(method):
    # Adding a error log showing that chosen HTTP method not allowed for the API.
    db_logger.info("HTTP {} method not allowed".format(method))

    statusCode = status.HTTP_405_METHOD_NOT_ALLOWED
    title = "Method not allowed"
    message = "{} method is not supported for the requested resource.".format(method)

    # 405 - Method Not Allowed
    return generatingResponse(statusCode=statusCode, title=title, message=message)
