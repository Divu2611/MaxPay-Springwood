# Importing Python Libraries
import re
import time
import logging
from django.conf import settings
from rest_framework import status

# Importing Project Files
import common
import transactions.services.dbService as dbService

db_logger = logging.getLogger("db")

"""
Client Authenticator -
Client will recieve its AccountId and Account secret key in the on-boarding documents via mail.
Proper Hash generation logic is shared in the documentation. Visit the link to refer <https://wiki.springwoodlabs.co/s/1a8a3e73-0779-4075-83df-25ae0440897f>.

For authentication and authorization client need to provide the AccountId and generated hash in the request parameters.
Account stored in our databse is then retrived using AccountId provided by client.
If the account found, Hash is then again generated on the server side and is matched with hash provided by client in request parameters.
Response is then send to client accordingly.


clientAuthentication: authenticates the client.

Parameters of the function:
* data (type dictionary) - holds all the data posted by the client, required for authentication.

Return values of the function:
authResult, can have following values - 
* errorResponse with statusCode 400 (type dictionary) - holds the statusCode, title and message of the response. This can occur if mandatory fields are missing or violates the type rule.
* errorResponse with statusCode 401 (type dictionary) - holds the statusCode, title and message of the response. This can occur if accountId is incorrect or is there is hash mismatch.
* successResponse with statusCode 200 (type dictionary) - returns the account details (account_id and account_secret_key).
"""


def clientAuthenticator(data):
    startTime = time.time()

    try:
        postedData = dict()

        # remove white space, prepared postedData.
        postedData = _removeSpaceAndPreparePostData(params=data)

        # empty validation.
        emptyValidationResult = _emptyValidation(data=postedData)
        if emptyValidationResult != True:
            # atleast one mandatory parameter is empty.

            endTime = time.time() - startTime
            # Analyzing the efficiency of the Service
            serviceEfficiency = settings.CLIENT_AUTHENTICATOR_RESPONSE_TIME
            serviceEfficiency.observe(endTime)

            return emptyValidationResult

        # type validation.
        typeValidationResult = _typeValidation(data=postedData)
        if typeValidationResult != True:
            # atleast one mandatory parameter voilates the type rule.

            endTime = time.time() - startTime
            # Analyzing the efficiency of the Service
            serviceEfficiency = settings.CLIENT_AUTHENTICATOR_RESPONSE_TIME
            serviceEfficiency.observe(endTime)

            return typeValidationResult

        authResult = _authenticate(data=postedData)

        endTime = time.time() - startTime
        # Analyzing the efficiency of the Service
        serviceEfficiency = settings.CLIENT_AUTHENTICATOR_RESPONSE_TIME
        serviceEfficiency.observe(endTime)

        return authResult
    except KeyError as missingParameter:
        # The exception might have occured while removing the space and preparing the post data.
        statusCode = status.HTTP_400_BAD_REQUEST
        title = "Parameters are missing"
        message = "{} in the request message sent to MaxPay might be missing. Kindly check your request parameters.".format(
            missingParameter
        )

        endTime = time.time() - startTime
        # Analyzing the efficiency of the Service.
        serviceEfficiency = settings.CLIENT_AUTHENTICATOR_RESPONSE_TIME
        serviceEfficiency.observe(endTime)

        # Adding a warning log showing that required parameters are missing.
        db_logger.warning(
            "Parameters required for client authentication ({}) are missing".format(
                missingParameter
            )
        )

        # 400 - Bad Request.
        return common.generatingResponse(
            statusCode=statusCode, title=title, message=message
        )


"""
_removeSpaceAndPreparePostData: removes white space, and prepared the posted data.

Parameters of the function:
* params (type dictionary) - holds all the data posted by the client, required for authentication.

Return values of the function:
* postedData (type dictionary) - holds the all posted value after removing space.
"""


def _removeSpaceAndPreparePostData(params):
    data = {"accountId": params["accountId"].strip(), "hash": params["hash"].strip()}

    return data


"""
_emptyValidation: checks empty validation for mandatory parameters.

Parameters of the function:
* data (type dictionary) - holds all the posted value after removing space.

Return values of the function:
emptyValidationResult, can be one of the following values -
* errorResponse (type dictionary) - holds the statusCode, title and message of the response. This can occur if one/more mandatory parameters is/are missing from the request parameter.
* True (type boolean) - holds True value if all mandatory parameters are present in the request parameter.
"""


def _emptyValidation(data):
    # Defining a list of mandatory parameters for authenticating and authorizing the client.
    mandatoryParameters = ["accountId", "hash"]

    # Checking if mandatory parameters (accountId, hash and transactionId) are present in the request parameter.
    if not all(data.get(param) for param in mandatoryParameters):
        # accountId or hash or transactionId is/are missing from the request parameters.
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
            "Parameters required for client authentication ({}) are missing".format(
                map(str, missingParameters)
            )
        )

        # 400 - Bad Request.
        return common.generatingResponse(
            statusCode=statusCode, title=title, message=message
        )

    # Returning true if all mandatory parameters are present in the request parameter.
    return True


"""
_typeValidation: checks type validation of mandatory parameters.

Parameters of the function:
* data (type dictionary) - holds all the posted value after removing space.

Return values of the function:
typeValidationResult, can be one of the following values -
* errorResponse (type dictionary) - holds the statusCode, title and message of the response. This can occur if one/more mandatory parameters is/are violating the type validation.
* True (type boolean) - holds True value if all mandatory parameters are follows the type validation.
"""


def _typeValidation(data):
    message = str()

    if not (isinstance(data["accountId"], str)):
        message += "accountId must be string. "
    elif not len(data["accountId"]) == 6 and re.match(
        "^[a-zA-Z0-9]+$", data["accountId"]
    ):
        message += (
            "accountId must be valid. It must match our internal value structure. "
        )

    if not (isinstance(data["hash"], str)):
        message += "hash must be string. "

    # Checking if mandatory parameters are following the type validation.
    if len(message) > 0:
        # one or more mandatory parameters is/are violating the type validation.
        statusCode = status.HTTP_400_BAD_REQUEST
        title = "Parameters violates type validation"
        message += "Kindly check your request parameters."

        # Adding a warning log showing that parameters violates the type validation.
        db_logger.warning(
            "Parameters required for client authentication are violating the type validation"
        )

        # 400 - Bad Request.
        return common.generatingResponse(
            statusCode=statusCode, title=title, message=message
        )

    # Returning true if all mandatory parameters are follows the type validation.
    return True


"""
_authenticate: authenticates the client using accountId and hash.

Parameters of the function:
* data (type dictionary) - holds all the posted value which passed all validations after removing space.

Return values of the function:
authResult, can have following values - 
* errorResponse with statusCode 401 (type dictionary) - holds the statusCode, title and message of the response. This can occur if accountId is incorrect or is there is hash mismatch
* successResponse with statusCode 200 (type dictionary) - returns the account details (account_id and account_secret_key).
"""


def _authenticate(data):
    accountId = data["accountId"]
    clientHash = data["hash"]

    if settings.ENV == "staging":
        if accountId not in ["0b1078", "3679f8"]:
            """
            For staging accountId is set to : 0b1078
            For staging acountSecretKey is set to : \x6b4f054b0588d26c3f8f24b6d1ea3de8cfff0d1fe1cb16e0c88b74877f0a7117
            For staging hash is set to : e5f1980954fb2544441ba8f4d00be991f160f74bff650981c5eccfb0859ad99a71591222a76bae52811d73c05b5ca5edf9dcebba7c0410da5cacd9b7a5c25d6e
            """
            statusCode = status.HTTP_401_UNAUTHORIZED
            title = "Account not found"
            message = "Invalid accountId. Kindly check your request parameters and enter the accountId as per the staging documentation."

            return common.generatingResponse(
                statusCode=statusCode, title=title, message=message
            )

    try:
        import hashlib

        # Making a DB call to get the account details from given accountId.
        account = dbService.getAccount(accountId=accountId)

        # Getting accountSecretKey from the account.
        accountSecretKey = account.account_secret_key

        # Generating hash value for verification.
        generatedHash = hashlib.sha512(
            str(accountId + "|" + accountSecretKey).encode("utf-8")
        ).hexdigest()
    except Exception as exception:
        # account from given accountId is not found in the database.
        statusCode = status.HTTP_401_UNAUTHORIZED
        title = "Account not found"
        message = "Account with given accountId does not exists. Incorrect accountID. Kindly check your request parameters or contact MaxPay tech team for support details."

        # Adding a error log showing that account with given accountId not found.
        db_logger.error(
            "Account with accountId:{} - Not Found.\nPossible Reason for error: {}".format(
                accountId, exception.args
            )
        )

        # Adding the exception log
        db_logger.exception(exception)

        # 401 - Unauthorized.
        return common.generatingResponse(
            statusCode=statusCode, title=title, message=message
        )

    # Comparing generatedHash with clientHash.
    if clientHash != generatedHash:
        # hash mismatch.
        statusCode = status.HTTP_401_UNAUTHORIZED
        title = "Hash value mismatch"
        message = "hash value provided in the request does not match for the given account. Kindly check your parameters."

        # Adding a warning log showing that there is hash value mismatch.
        db_logger.warning(
            "There is hash value mismatch for accountId:{}.\nHash provided: {}.\nActual Hash: {}".format(
                accountId, clientHash, generatedHash
            )
        )

        # 401 - Unauthorized.
        return common.generatingResponse(
            statusCode=statusCode, title=title, message=message
        )
    else:
        # hash matches.
        statusCode = status.HTTP_200_OK
        title = "Authenticated"
        message = "Your credentials are valid. Allowed to call our API."

        # Adding a info log showing that authentication is successful.
        db_logger.info(
            "Client Authentication for accountId:{} Successful!".format(accountId)
        )

        # 200 - OK.
        return account
