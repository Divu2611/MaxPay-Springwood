# Importing Python Libraries
import time
import logging
from django.conf import settings
from rest_framework import status

# Importing Project Files
import common
import payment_response.services.dbService as dbService

db_logger = logging.getLogger("db")

"""
Payment Gateway Authenticator -
"""


def pgAuthenticator(request):
    startTime = time.time()

    # empty validation.
    emptyValidationResult = _emptyValidation(request=request)
    if emptyValidationResult != True:
        # authKey in the headers might be empty

        endTime = time.time() - startTime
        # Analyzing the efficiency of the Service
        serviceEfficiency = settings.PG_AUTHENTICATOR_RESPONSE_TIME
        serviceEfficiency.observe(endTime)

        return emptyValidationResult

    authResult = _authenticate(request=request)

    endTime = time.time() - startTime
    # Analyzing the efficiency of the Service
    serviceEfficiency = settings.PG_AUTHENTICATOR_RESPONSE_TIME
    serviceEfficiency.observe(endTime)

    return authResult


"""
_emptyValidation: checks empty validation for Auth-Key header.

Parameters of the function:
* request (type HttpRequest) - holds all the entire request, required for payment gateway authentication.

Return values of the function:
emptyValidationResult, can be one of the following values -
* errorResponse with statusCode 400 (type dictionary) - holds the statusCode, title and message of the response. This can occur if Auth-Key is missing from the request header.
* True (type boolean) - holds True value if Auth-Key is present in the request header.
"""


def _emptyValidation(request):
    authKey = request.headers.get("HTTP-AUTH")

    if authKey == None:
        # Auth-Key is missing from the request headers.
        statusCode = status.HTTP_400_BAD_REQUEST
        title = "Headers are missing"
        message = "Auth-Key in the request message sent to MaxPay might be missing. Kindly check your request headers."

        # Adding a warning log showing that required headers are missing.
        db_logger.warning(
            "Auth-Key in the request headers required for gateway authentication is missing."
        )

        # 400 - Bad Request.
        return common.generatingResponse(
            statusCode=statusCode, title=title, message=message
        )

    # Returning true if all Auth-Key is present in the request header.
    return True


"""
_authenticate: authenticates the payment gateway using Auth-Key.

Parameters of the function:
* data (type dictionary) - holds all the entire request, required for payment gateway authentication.

Return values of the function:
authResult, can have following values - 
* errorResponse with statusCode 401 (type dictionary) - holds the statusCode, title and message of the response. This can occur if Auth-Key is incorrect in the request header.
* successResponse with statusCode 200 (type dictionary) - returns the payment gateway details (name and auth_key).
"""


def _authenticate(request):
    authKey = request.headers.get("HTTP-AUTH")
    try:
        paymentGateway = dbService.pgDetails(authKey=authKey)

        # payment gateway authenticated.
        statusCode = status.HTTP_200_OK
        title = "Authenticated"
        message = (
            "Provided Auth-Key is valid for - "
            + paymentGateway.name
            + " payment gateway."
        )

        # Adding a info log showing that authentication is successful.
        db_logger.info(
            "Payment Gateway Authentication Successful!.\nPayment Gateway: {}.".format(
                paymentGateway.name
            )
        )

        # 200 - OK.
        return paymentGateway
    except Exception as exception:
        # incorrect Auth-Key.
        statusCode = status.HTTP_401_UNAUTHORIZED
        title = "Invalid Auth-Key"
        message = "Auth-key provided in the request header is invalid. Kindly check your request headers or contact MaxPay tech team for support details."

        # Adding a error log showing that payment-gateway with given auth-key not found.
        db_logger.error(
            "Payment Gateway with auth-key:{} - Not Found.\nPossible Reason for error: {}.".format(
                authKey, exception.args
            )
        )

        # Adding the exception log
        db_logger.exception(exception)

        # 401 - Unauthorized.
        return common.generatingResponse(
            statusCode=statusCode, title=title, message=message
        )
