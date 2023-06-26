# Importing Python Libraries
import time
import logging
from django.conf import settings
from rest_framework import status

# Importing Project Files
import common
import payment_response.services.dbService as dbService
from .vocabularyService import paymentGatewayVocabulary

db_logger = logging.getLogger("db")

"""
"""


def createRequest(data, paymentGateway):
    startTime = time.time()

    requestData = dict()

    # defining the list of keys that will sent in the request to client
    requestDataKeys = [
        "transactionStatus",
        "transactionId",
        "transactionTime",
        "paymentMode",
        "unmappedstatus",
        "error",
        "errorMessage",
        "errorReason",
        "productInformation",
        "discount",
        "netAmountDebit",
        "checkoutFlow",
        "redirectURL",
    ]

    # defining the list of keys that are mandatory in the request i.e., whose value cannot be 'N.A.'
    requiredKeys = [
        "transactionStatus",
        "transactionId",
        "transactionTime",
        "paymentMode",
        "productInformation",
        "netAmountDebit",
        "checkoutFlow",
        "redirectURL",
    ]

    # vocabulary of a payment gateway.
    vocabulary = paymentGatewayVocabulary[paymentGateway]
    """
    Following assumptions are made:
    Response from payment gateway must contains the following fields:
    1.) Transaction Status
    2.) Transaction Amount
    3.) MaxPay Reference Id
    """

    # Adding a info log showing the callback from payment gateway.
    db_logger.info("Callback from payment gateway {}: {}.".format(paymentGateway, data))

    try:
        if all(key in vocabulary for key in requestDataKeys):
            # all key-values are provided by the payment gateway in the request.
            for key in requestDataKeys:
                requestData[key] = data[vocabulary[key]]
        else:
            # there are missing key-values in the request from payment gateway.
            missingKeys = [keys for keys in requestDataKeys if keys not in vocabulary]
            if any(key in missingKeys for key in requiredKeys):
                # these missing key-values are one of the required keys.
                presentKeys = [keys for keys in requestDataKeys if keys in vocabulary]
                for key in presentKeys:
                    # first updating the request with those key-values which are present.
                    requestData[key] = data[vocabulary[key]]
                # then retrieving the key-values, that are missing and required, from the database.
                requestDetails = dbService.getRequestDetails(
                    uniqueIdentifier=data[vocabulary["uniqueIdentifier"]]
                )
                for key in missingKeys:
                    # now updating the request.
                    # if key is required then request is updated from database fetched value.
                    # else is set to 'N.A.'.
                    requestData[key] = (
                        requestDetails[key] if key in requiredKeys else "N.A."
                    )
            else:
                # none of the missing key-values is required.
                # its value is then set to 'N.A.' if it is missing.
                for key in requestDataKeys:
                    requestData[key] = (
                        data[vocabulary[key]] if key in vocabulary else "N.A."
                    )

        requestData["transactionStatus"] = requestData["transactionStatus"].lower()
        requestData["paymentSource"] = paymentGateway

        # Adding a info log showing that MaxPay is about to update the database after completion of transaction.
        db_logger.info(
            "About to update the database after completion of transaction.\nReference ID: {}.".format(
                data[vocabulary["uniqueIdentifier"]]
            )
        )

        # updating the database with complete transaction details.
        dbService.completeTransaction(
            referenceId=data[vocabulary["uniqueIdentifier"]],
            paymentMode=requestData["paymentMode"],
            transactionResponse=requestData,
            metaData=data,
            transactionStatus=requestData["transactionStatus"],
            discount=requestData["discount"]
            if requestData["discount"] != "N.A."
            else 0,
            netAmountDebit=requestData["netAmountDebit"],
        )

        # Adding a info log showing that MaxPay has successfully updated the database.
        db_logger.info(
            "Updated the database after completion of transaction.\nReference ID: {}.".format(
                data[vocabulary["uniqueIdentifier"]]
            )
        )

        endTime = time.time() - startTime
        # Analyzing the efficiency of the Service
        serviceEfficiency = settings.FINAL_REQUEST_CREATOR_RESPONSE_TIME
        serviceEfficiency.observe(endTime)

        # Adding a info log showing that CallBack for client is generated successfully.
        db_logger.info(
            "CallBack message is generated successfully and is also updated in the database.\nReference ID: {}.".format(
                data[vocabulary["uniqueIdentifier"]]
            )
        )

        requestData["transactionStatus"] = (
            "failure"
            if requestData["transactionStatus"] == "expired"
            else requestData["transactionStatus"]
        )
        return requestData
    except Exception as exception:
        statusCode = status.HTTP_500_INTERNAL_SERVER_ERROR
        title = "Internal Server Error"
        message = exception.args

        # Adding a error log showing that there might be an internal server error.
        db_logger.error(
            "Internal Server Error.\nPossible Reason for error: {}.\nReference ID: {}".format(
                exception.args, data[vocabulary["uniqueIdentifier"]]
            )
        )

        # Adding the exception log
        db_logger.exception(exception)

        return common.generatingResponse(
            statusCode=statusCode, title=title, message=message
        )
