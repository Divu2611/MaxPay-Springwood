# Importing Python Libraries
import time
import logging
from django.conf import settings
from rest_framework import status

# Importing Project files
import common
import transactions.services.dbService as dbService
import transactions.services.gatewaySelectionService as selectGateway
from .payu.views import initiate_transaction_payu
from .easebuzz.views import initiate_transaction_easebuzz
from .decentro.views import initiateTransactionDecentro, generatePaymentLinkDecentro
from .pinelabs.views import initiate_transaction_pinelabs
from .airpay.views import initiateTransactionAirPay
from .itzpay.views import initiateTransactionItzPay
from .paymob.views import initiateTransactionPayMob
from .ezcash.genie.views import initiateTransactionGenie
from .yoomoney.views import initiateTransactionYooMoney

db_logger = logging.getLogger("db")

"""
pgBalancer: pass the flow of transaction to one of the payment gateways.

Parameters of the function:
* data (type dictionary) - holds all the data posted by the client, required for transaction to initiate.

Return values of the function:
* pgResponse (type dictionary) - response received from payment gateway after transaction successfully initiates.
"""


# @common.retry(
#     5, [1, 3, 5, 10, 15]
# )  # Retry logic that will execute 5 times with interval of 1s, 3s, 5s, 10s and 15s.
def pgBalancer(data):
    startTime = time.time()

    # Seleting the appropriate payment gateway.
    gatewayObject = selectGateway.selectGateway(data=data)
    if gatewayObject["statusCode"] == 503:
        # Appropriate payment gateway service for selected location and payment mode is not available.
        return gatewayObject

    gateway = gatewayObject["message"]

    try:
        gatewayResult = None
        metaData = None
        transactionInitiated = False

        # Adding a info log showing the payment channel.
        db_logger.info(
            "Chosen payment channel is: {}.\nReference ID: {}".format(
                gateway, data["referenceId"]
            )
        )

        # process to pass the flow to a payment gateway.
        if gateway == "PayU":
            # Initiate with PayU.
            payUResult = initiate_transaction_payu(data)
            metaData = payUResult
        elif gateway == "EaseBuzz":
            # Inititate with EaseBuzz.
            easeBuzzResult = initiate_transaction_easebuzz(data)
            metaData = easeBuzzResult
        elif gateway == "Decentro":
            # Inititate with Decentro.
            if data["upiChoice"] == "upiId":
                # Adding a info log showing that chosen payment mode is UPI ID.
                db_logger.info(
                    "Payment Mode: UPI-ID.\nReference ID: {}".format(
                        data["referenceId"]
                    )
                )

                # Inititating using upiId.
                decentroResult = initiateTransactionDecentro(data=data)
                metaData = decentroResult

                if "status" in decentroResult and decentroResult["status"] == "SUCCESS":
                    # transaction via Decentro initated successfully.
                    response = {
                        "statusCode": status.HTTP_200_OK,
                        "title": "SUCCESS",
                        "message": "Transaction has been initiated successfully.",
                        "transactionId": data["transactionId"],
                    }

                    transactionInitiated = True

                    # Adding a info log showing that transaction initiated successfully.
                    db_logger.info(
                        "Transaction initiated successfully.\nReference ID: {}".format(
                            data["referenceId"]
                        )
                    )

                    gatewayResult = response
                else:
                    # Adding a error log showing that transaction was failed to initiated.
                    db_logger.error(
                        "Transaction failed to initate via Decentro. Might be an Internal Server Error.\nReference ID: {}".format(
                            data["referenceId"]
                        )
                    )

                    # failed to initiate the transaction.
                    gatewayResult = decentroResult
            elif data["upiChoice"] == "upiApp":
                # Adding a info log showing that chosen payment mode is UPI Intent.
                db_logger.info(
                    "Payment Mode: UPI Intent\nReference ID: {}".format(
                        data["referenceId"]
                    )
                )

                # Inititate using upiApp - Intent Flow.
                decentroResult = generatePaymentLinkDecentro(data=data)
                metaData = decentroResult

                if "status" in decentroResult and decentroResult["status"] == "SUCCESS":
                    # transaction link via Decentro created successfully.
                    if "upiApp" in data:
                        # Adding a info log showing the chosen payment method will return the link for speicif PSP App.
                        db_logger.info(
                            "Chosen method returned the link for specific PSP App: {}.\n Reference ID: {}".format(
                                data["upiApp"], data["referenceId"]
                            )
                        )

                        # specific UPI app is selected for payment.
                        if data["upiApp"] == "GPay":
                            # specific UPI app is GPay.
                            url = decentroResult["data"]["pspUri"]["gpayUri"]
                        elif data["upiApp"] == "PhonePe":
                            # specific UPI app is PhonePe.
                            url = decentroResult["data"]["pspUri"]["phonepeUri"]
                        elif data["upiApp"] == "PayTM":
                            # specific UPI app is PayTM.
                            url = decentroResult["data"]["pspUri"]["paytmUri"]
                    else:
                        # Adding a info log showing that chosen payment method will display tray of all PSP Apps.
                        db_logger.info(
                            "Chosen method displyed the tray showing all PSP Apps.\n Refernce ID: {}".format(
                                data["referenceId"]
                            )
                        )

                        # no specific UPI app is selected for payment.
                        url = decentroResult["data"]["generatedLink"]

                    response = {
                        "statusCode": status.HTTP_200_OK,
                        "url": url,
                    }

                    transactionInitiated = True

                    # Adding a info log showing that transaction initiated successfully.
                    db_logger.info(
                        "Transaction initiated successfully.\nReference ID: {}".format(
                            data["referenceId"]
                        )
                    )

                    gatewayResult = response
                else:
                    # Adding a error log showing that transaction was failed to initiated.
                    db_logger.error(
                        "Transaction failed to initate via Decentro. Might be an Internal Server Error.\nReference ID: {}".format(
                            data["referenceId"]
                        )
                    )

                    # failed to generate the UPI link.
                    gatewayResult = decentroResult
        elif gateway == "PineLabs":
            # Inititate with PineLabs.
            pineLabsResult = initiate_transaction_pinelabs(data)
            metaData = pineLabsResult
        elif gateway == "AirPay":
            # Inititate with AirPay.
            airPayResult = initiateTransactionAirPay(data=data)
            metaData = airPayResult

            response = responseURLGeneration(
                data=data, isHtmlResponse=True, pgResponse=airPayResult
            )

            transactionInitiated = True

            # Adding a info log showing that AirPay's payment portal page in HTML form is added to database.
            db_logger.info(
                "{}'s payment portal page is successfully added to the database in HTML form.\nPayment URL generated: {}.\nReference ID".format(
                    gateway, url, data["referenceId"]
                )
            )

            gatewayResult = response
        elif gateway == "ItzPay":
            # Inititate with ItzPay.
            itzPayResult = initiateTransactionItzPay(data=data)
            metaData = itzPayResult

            if "status" in itzPayResult and itzPayResult["status"] == "success":
                # transaction via ItzPay initated successfully.
                response = {
                    "statusCode": status.HTTP_200_OK,
                    "title": "SUCCESS",
                    "message": "Transaction has been initiated successfully.",
                    "transactionId": data["transactionId"],
                }

                transactionInitiated = True

                gatewayResult = response
            else:
                # failed to initiate the transaction.
                gatewayResult = itzPayResult
        elif gateway == "Paymob":
            # Initiate with Paymob.
            paymobResult = initiateTransactionPayMob(data=data)
            metaData = paymobResult

            # Retriving the URL from the PG's response.
            if data["paymentMode"] == "Card":  # paymentMode is 'Card'.
                # If the paymentMode is 'Card' the response is itself the link.
                url = paymobResult
            elif data["paymentMode"] == "Wallet":  # paymentMode is 'Wallet'.
                url = paymobResult["redirect_url"]

            response = responseURLGeneration(
                data=data, isHtmlResponse=False, pgResponse=url
            )

            transactionInitiated = True

            gatewayResult = response
        elif gateway == "eZCash - Genie":
            # Initiate with eZCash - Genie
            genieResult = initiateTransactionGenie(data=data)
            metaData = genieResult

            # Retriving the URL from the PG's response.
            url = genieResult["url"]

            response = responseURLGeneration(
                data=data, isHtmlResponse=False, pgResponse=url
            )

            transactionInitiated = True

            gatewayResult = response
        elif gateway == "YooMoney":
            # Inititate with YooMoney.
            yooMoneyResult = initiateTransactionYooMoney(data=data)
            metaData = yooMoneyResult

            # getting the confirmationURL from the yooMoney's response object.
            confirmationURL = yooMoneyResult.confirmation.confirmation_url

            response = responseURLGeneration(
                data=data, isHtmlResponse=False, pgResponse=confirmationURL
            )

            transactionInitiated = True

            gatewayResult = response

        if transactionInitiated:
            # Adding a info log showing that flow of transaction with unique referenceId is successfully pushed to a payment gateway.
            db_logger.info(
                "Transaction successfully pushed to {} payment channel.\nReference ID: {}".format(
                    gateway, data["referenceId"]
                )
            )

            transactionStatus = "Pushed To Payment Gateway"
        else:
            # Adding a info log showing that flow of transaction with unique referenceId is successfully pushed to a payment gateway.
            db_logger.error(
                "Error reported post pushing the transaction to {} payment channel.\nReference ID: {}.\nPossible Reason for error: {}".format(
                    gateway, data["referenceId"], metaData
                )
            )

            transactionStatus = "Client Initiated - Gateway Error"

        # updating transaction status in DB (from 'Client Initiated' to 'Pushed To Payment Gateway').
        dbService.updateTransactionStatus(
            transactionStatus=transactionStatus,
            metaData=metaData,
            paymentChannel=gateway,
            referenceId=data["referenceId"],
        )

        endTime = time.time() - startTime
        # Analyzing the efficiency of the gateway
        gatewayEfficiency = settings.PG_BALANCER_RESPONSE_TIME
        gatewayEfficiency.observe(endTime)

        return gatewayResult
    except Exception as exception:
        statusCode = status.HTTP_500_INTERNAL_SERVER_ERROR
        title = "Internal Server Error"
        message = exception.args

        # updating transaction status in DB (from 'Client Initiated' to 'Client Initiated - Gateway Error').
        dbService.updateTransactionStatus(
            transactionStatus="Client Initiated - Gateway Error",
            metaData=exception.args,
            paymentChannel=gateway,
            referenceId=data["referenceId"],
        )

        # Adding a error log showing that there might be a database failure.
        db_logger.error(
            "Internal Database Failure.\nPossible Reason for error: {}.\nReference ID: {}".format(
                message, data["referenceId"]
            )
        )

        # Adding the exception log
        db_logger.exception(exception)

        return common.generatingResponse(
            statusCode=statusCode, title=title, message=message
        )


"""
"""


def responseURLGeneration(data, isHtmlResponse, pgResponse):
    """
    Updating the database -
    * A checker which checks whether the response from the PG is in HTML form or a URL.
    * Actual response from the PG.
    """
    dbService.createPGResponse(
        referenceId=data["referenceId"],
        htmlResponse=isHtmlResponse,
        response=pgResponse,
    )

    # Generating the uniform response URL for client.
    url = (
        "https://prod.max-payments.com/api/pay/"
        if settings.ENV == "production"
        else "https://staging.max-payments.com/api/pay/"
    )
    url += data["referenceId"] + "/"

    # Generating the response for client and returning it.
    response = {
        "statusCode": status.HTTP_200_OK,
        "url": url,
    }

    return response
