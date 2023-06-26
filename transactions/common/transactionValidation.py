# Importing Python Libraries
import re
import logging
from rest_framework import status

# Importing Python Libraries
import common

db_logger = logging.getLogger("db")

"""
transactionValidator: checks validation (empty and type) for mandatory parameters (transactionId).

Parameters of the function:
* data (type dictionary) - holds all the posted value after removing space, required for validation.

Return values of the function:
transactionValidationResult, can be one of the following values -
* errorResponse with statusCode 400 (type dictionary) - holds the statusCode, title and message of the response. This can occur if transactionId is either missing from the request parameter or voilates the type rule.
* True (type boolean) - holds True value if validation is successful.
"""


def transactionValidator(data):
    # empty validation.
    emptyValidationResult = _emptyValidation(data=data)
    if emptyValidationResult != True:
        # transactionId might be empty.
        return emptyValidationResult

    # type validation.
    typeValidationResult = _typeValidation(data=data)
    if typeValidationResult != True:
        # transactionId might voilated the type rule.
        return typeValidationResult

    return True


"""
_emptyValidation: checks empty validation for mandatory parameters.

Parameters of the function:
* data (type dictionary) - holds all the posted value after removing space, required for transaction empty validation.

Return values of the function:
emptyValidationResult, can be one of the following values -
* errorResponse with statusCode 400 (type dictionary) - holds the statusCode, title and message of the response. This can occur if transactionId is missing from the request parameter.
* True (type boolean) - holds True value if transactionId is present in the request parameter.
"""


def _emptyValidation(data):
    # Defining a list of mandatory parameters for authenticating and authorizing the client.
    mandatoryParameters = ["transactionId"]

    # Checking if mandatory parameters (transactionId) are present in the request parameter.
    if not all(data.get(param) for param in mandatoryParameters):
        # transactionId is missing from the request parameters.
        missingParameters = [
            params
            for params in mandatoryParameters
            if params in data and (not data[params])
        ]

        statusCode = status.HTTP_400_BAD_REQUEST
        title = "Parameters are missing"
        message = (
            " ".join(map(str, missingParameters))
            + " in the request message sent to MaxPay might be missing. Kindly check your request parameters."
        )

        # Adding a warning log showing that required parameters are missing.
        db_logger.warning(
            "Parameters required for transaction validation ({}) are missing".format(
                map(str, missingParameters)
            )
        )

        # 400 - Bad Request.
        return common.generatingResponse(
            statusCode=statusCode, title=title, message=message
        )

    # Returning true if transactionId is present in the request parameter.
    return True


"""
_typeValidation: checks type validation of transactionId.

Parameters of the function:
* data (type dictionary) - holds all the posted value after removing space, required for transaction type validation.

Return values of the function:
typeValidationResult, can be one of the following values -
* errorResponse with statusCode 400 (type dictionary) - holds the statusCode, title and message of the response. This can occur if transactionId is violating the type validation.
* True (type boolean) - holds True value if transactionId follows the type validation.
"""


def _typeValidation(data):
    message = str()

    if not (isinstance(data["transactionId"], str)):
        message += "transactionId must be string. "
    elif not re.match(r"txn_\w{0,30}$", data["transactionId"]):
        message += "transactionId must be valid. It must be of form 'txn_' followed by atmost 30 alpha-numeric characters. "

    # Checking if transactionId is following the type validation.
    if len(message) > 0:
        # transactionId is violating the type validation.
        statusCode = status.HTTP_400_BAD_REQUEST
        title = "Parameters violates type validation"
        message += "Kindly check your request parameters."

        # Adding a warning log showing that parameters violates the type validation.
        db_logger.warning(
            "Parameters required for transaction validation are violating the type validation"
        )

        # 400 - Bad Request.
        return common.generatingResponse(
            statusCode=statusCode, title=title, message=message
        )

    # Returning true if all transactionId is follows the type validation.
    return True
