# Importing Python Libraries
import time
import logging
from django.conf import settings
from rest_framework import status

# Importing Python Libraries
import common
import transactions.services.dbService as dbService
from ..common.transactionValidation import transactionValidator
from .payloadService import payloadCreator

db_logger = logging.getLogger("db")

"""
verifyUniqueTransaction: verifies if there already exists transactionId againsts the given accountId.

Parameters of the function:
* data (type dictionary) - holds all the data posted by the client, required for authentication.
* account (type dictionary) - holds the account details (account_id and account_secret_key).

Return values of the function:
authResult, can have following values - 
* errorResponse with statusCode 400 (type dictionary) - holds the statusCode, title and message of the response. This can occur if transactionId missing or violates the type rule.
* successResponse with statusCode 200 (type dictionary) - returns the complete postedData.
"""


def verifyUniqueTransaction(data, account):
    startTime = time.time()

    try:
        postedData = dict()

        # remove white space, prepared postedData.
        postedData = _removeSpaceAndPreparePostData(params=data)

        # transaction validation (empty validation and type validation)
        transactionValidationResult = transactionValidator(data=postedData)
        if transactionValidationResult != True:
            # transactionId might be empty or voilated the type rule.

            endTime = time.time() - startTime
            # Analyzing the efficiency of the Service
            serviceEfficiency = settings.UNIQUE_TRANSACTION_VERIFICATION_RESPONSE_TIME
            serviceEfficiency.observe(endTime)

            return transactionValidationResult

        verificationResult = _verify(data=postedData, requestData=data, account=account)

        endTime = time.time() - startTime
        # Analyzing the efficiency of the Service
        serviceEfficiency = settings.UNIQUE_TRANSACTION_VERIFICATION_RESPONSE_TIME
        serviceEfficiency.observe(endTime)

        return verificationResult
    except KeyError as missingParameter:
        # The exception might have occured while removing the space and preparing the post data.
        statusCode = status.HTTP_400_BAD_REQUEST
        title = "Parameters are missing"
        message = "{} in the request message sent to MaxPay might be missing. Kindly check your request parameters.".format(
            missingParameter
        )

        endTime = time.time() - startTime
        # Analyzing the efficiency of the Service
        serviceEfficiency = settings.UNIQUE_TRANSACTION_VERIFICATION_RESPONSE_TIME
        serviceEfficiency.observe(endTime)

        # Adding a warning log showing that required parameters are missing.
        db_logger.warning(
            "Parameters required for unique transaction checking ({}) are missing".format(
                missingParameter
            )
        )

        # 400 - Bad Request.
        return common.generatingResponse(
            statusCode=statusCode, title=title, message=message
        )
    except Exception as exception:
        # The exception might have occured if there is internal database failure.
        statusCode = status.HTTP_500_INTERNAL_SERVER_ERROR
        title = "Internal Database Failure"
        message = exception.args

        endTime = time.time() - startTime
        # Analyzing the efficiency of the Service
        serviceEfficiency = settings.UNIQUE_TRANSACTION_VERIFICATION_RESPONSE_TIME
        serviceEfficiency.observe(endTime)

        # Adding a error log showing that there might be a database failure.
        db_logger.error(
            "Internal Database Failure\nPossible Reason for error: {}".format(
                exception.args
            )
        )

        # Adding the exception log
        db_logger.exception(exception)

        # 500 - Internal Server Error.
        return common.generatingResponse(
            statusCode=statusCode, title=title, message=message
        )


"""
_removeSpaceAndPreparePostData: removes white space, and prepared the posted data.

Parameters of the function:
* params (type dictionary) - holds all the data posted by the client, required unique transaction verification.

Return values of the function:
* postedData (type dictionary) - holds the all posted value after removing space.
"""


def _removeSpaceAndPreparePostData(params):
    data = {
        "transactionId": params["transactionId"].strip(),
    }

    return data


"""
_verify: verifies the presence of unique transactionId.

Parameters of the function:
* data (type dictionary) - holds all the posted value which passed all validations after removing space, required for transaction verification.
* requestData (type dictionary) - holds all the data posted by the client, required for transaction to initiate.
* account (type dictionary) - holds the account details (account_id and account_secret_key).

Return values of the function:
authResult, can have following values - 
* errorResponse with statusCode 409 (type dictionary) - holds the statusCode, title and message of the response. This can occur if transactionId already exists
* successResponse with statusCode 200 (type dictionary) - returns the complete postedData.
"""


def _verify(data, requestData, account):
    try:
        transactionExists = dbService.transactionExists(
            accountId=account.account_id, transactionId=data["transactionId"]
        )
    except:
        raise Exception("Unable to retrieve the transaction details from the database.")
    if transactionExists:
        # transactionId against accountId already exists.
        statusCode = status.HTTP_409_CONFLICT
        title = "transactionId already exist"
        message = "transactionId for this account already exists. Kindly provide a new unique transactionId."

        # Adding a error log showing that transactionId already exists.
        db_logger.error(
            "transactionId: {} already exists.".format(data["transactionId"])
        )

        # 409 - Conflict
        return common.generatingResponse(
            statusCode=statusCode, title=title, message=message
        )

    else:
        # creating the payload from the client request data
        payloadResponse = payloadCreator(data=requestData)
        if "statusCode" in payloadResponse and payloadResponse["statusCode"] == 400:
            """
            Payload response failed:
            Following is the reason -
            * 400 - Bad Request: Mandatory parameters might be missing or violates the data type rule.
            """
            return payloadResponse

        # In case of success, payloadResponse contains the postedData.
        postedData = payloadResponse

        try:
            # Populating the Database
            postedData = dbService.transactionCreate(
                transactionId=data["transactionId"],
                transactionStatus="Client Initiated",
                account=account,
                requestDetails=postedData,
            )

            # Adding a info log showing that transaction with unique referenceId is successfully initiated by the client.
            db_logger.info(
                "Transaction successfully initiated by client.\nAccount: {}.\nReference ID: {}".format(
                    account.name, postedData["referenceId"]
                )
            )

            return postedData
        except:
            raise Exception("Unable to create new transaction details in the database.")
