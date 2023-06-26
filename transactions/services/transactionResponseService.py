# Importing Python Libraries.
import logging
from rest_framework import status

# Importing Project Libraries.
import common

db_logger = logging.getLogger("db")


# getTransactionResponse - returns the transaction response
def getTransactionResponse(transaction):
    if transaction.transaction_response is not None:
        # transaction has been completed (it is either success or failure).

        transactionResponse = eval(transaction.transaction_response)

        response = {
            "statusCode": status.HTTP_200_OK,
            "msg": "1 out of 1 Transactions Fetched Successfully",
            "transactionDetails": {
                transaction.reference_id: {
                    "transactionStatus": transactionResponse["transactionStatus"],
                    "referenceId": transaction.reference_id,
                    "transactionTime": transactionResponse["transactionTime"],
                    "paymentMode": transactionResponse["paymentMode"],
                    "unmappedstatus": transactionResponse["unmappedstatus"],
                    "error": transactionResponse["error"],
                    "errorMessage": transactionResponse["errorMessage"],
                    "errorReason": transactionResponse["errorReason"],
                    "productInformation": transactionResponse["productInformation"],
                    "discount": transactionResponse["discount"],
                    "netAmountDebit": transactionResponse["netAmountDebit"],
                    "checkoutFlow": transaction.checkout_flow,
                    "paymentSource": transactionResponse["paymentSource"],
                    # "request_id": data['request_id'],
                    # "additional_charges": data['additional_charges'],
                    # "Merchant_UTR": data['merchant_utr'],
                    # "Settled_At": data['settled_at']
                }
            },
        }

        return response

    else:
        # transaction is pending or under process.
        statusCode = status.HTTP_206_PARTIAL_CONTENT
        title = "Transaction Incomplete."
        message = "Transaction is pending or might be under process. Complete the transaction to get the deatils."

        # Adding a warning log showing that transaction is incomplete.
        db_logger.info(
            "Transaction is either pending or might be under process.\nReference ID: {}".format(
                transaction.reference_id
            )
        )

        # 406 - PartialContent.
        return common.generatingResponse(
            statusCode=statusCode, title=title, message=message
        )
