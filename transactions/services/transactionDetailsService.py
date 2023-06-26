# Importing Python Libraries
import logging
from rest_framework import status

# Importing Project Files
import common
import transactions.services.dbService as dbService
from ..common.transactionValidation import transactionValidator
from .transactionResponseService import getTransactionResponse

db_logger = logging.getLogger("db")

"""
getTransactionDetails: returns the filtered* transaction details of given accountId and transactionId.

Parameters of the function:
* data (type dictionary) - holds all the data posted by the client, required for retriving transaction details.

Return values of the function:
detailResult, can have following values - 
* errorResponse with statusCode 400 (type dictionary) - holds the statusCode, title and message of the response. This can occur if transactionId missing or violates the type rule.
* errorResponse with statusCode 404 (type dictionary) - holds the statusCode, title and message of the response. This can occur if transaction details does not exists in the database.
* successResponse (type dictionary) - returns the complete filtered* transaction details.


*MaxPay only returns the transaction status and payment mode information as transaction details.
It doesnot returns any sensitive information like email, upiId, card or bank details due to security norms.
"""


def getTransactionDetails(data):
    # transaction validation (empty validation and type validation)
    transactionValidationResult = transactionValidator(data=data)
    if transactionValidationResult != True:
        return transactionValidationResult

    detailResult = _details(data=data)
    return detailResult


"""
_details: returns the filtered* details.

Parameters of the function:
* data (type dictionary) - holds all the data posted by the client, required for retriving transaction details.

Return values of the function:
transactionResult, can have following values - 
* errorResponse with statusCode 404 (type dictionary) - holds the statusCode, title and message of the response. This can occur if transaction details does not exists in the database.
* successResponse (type dictionary) - returns the complete filtered* transaction details.
"""


def _details(data):
    transactionId = data["transactionId"]
    accountId = data["accountId"]

    try:
        transaction = dbService.transactionDetails(
            transactionId=transactionId, accountId=accountId
        )
        return getTransactionResponse(transaction=transaction)
    except Exception as exception:
        # incorrect transactionId.
        statusCode = status.HTTP_404_NOT_FOUND
        title = "Transaction Not Found"
        message = "Transaction details for given transactionId not found. Kindly check your request parameters or contact MaxPay tech team for support details."

        # Adding a error log showing that transaction with given transactionId not found.
        db_logger.error(
            "Transaction with transactionId:{} - Not Found.\nPossible Reason for error: {}".format(
                transactionId, exception.args
            )
        )

        # Adding the exception log
        db_logger.exception(exception)

        # 404 - NotFound.
        return common.generatingResponse(
            statusCode=statusCode, title=title, message=message
        )
