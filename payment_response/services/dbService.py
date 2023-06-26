# Importing Python Libraries.
import time
from django.conf import settings

# Importing Project Files.
from ..models import Transaction, PG, FormDetails, CumulativeTransactionAmount


# getReuestDetails - returns the transactionId, transactionTime, paymentMode, productInformation, redirectURL and checkoutFlow, required for creating the final request to be sent to merchant.
def getRequestDetails(uniqueIdentifier):
    startTime = time.time()

    transaction = Transaction.objects.get(reference_id=uniqueIdentifier)

    transactionId = transaction.transaction_id
    transactionTime = transaction.updated_at
    paymentMode = transaction.payment_mode
    checkoutFlow = transaction.checkout_flow

    formDetails = FormDetails.objects.get(reference_id=uniqueIdentifier)
    formDetails = eval(formDetails.form_details)

    productInformation = formDetails["productInformation"]
    redirectURL = formDetails["redirectURL"]

    endTime = time.time() - startTime
    # Analyzing the efficiency of the API.
    apiEfficiency = settings.RETRIEVE_REQUEST_DETAILS_DB_RESPONSE_TIME
    apiEfficiency.observe(endTime)

    return {
        "transactionId": transactionId,
        "transactionTime": transactionTime,
        "paymentMode": paymentMode,
        "productInformation": productInformation,
        "redirectURL": redirectURL,
        "checkoutFlow": checkoutFlow,
    }


# completeTransaction - update the Transactions table after the transaction is completely processed by user (either success or failure).
def completeTransaction(
    referenceId,
    paymentMode,
    transactionResponse,
    metaData,
    transactionStatus,
    discount,
    netAmountDebit,
):
    startTime = time.time()

    transaction = Transaction.objects.get(reference_id=referenceId)
    # cummulativeTransactionAmount = CumulativeTransactionAmount.objects.get(
    #     account=transaction.account
    # )

    transaction.discount = discount
    transaction.net_amount_debit = netAmountDebit
    transaction.payment_mode = paymentMode

    transaction.transaction_response = transactionResponse
    transaction.meta_data = metaData

    transaction.transaction_status_code = settings.MAPPINGS[transactionStatus]
    transaction.transaction_status = transactionStatus

    # if transactionStatus == "success":
    #     successTransactionAmountTillDate = (
    #         cummulativeTransactionAmount.total_success_amount
    #     )
    #     totalSuccessTransactionAmount = (
    #         successTransactionAmountTillDate + netAmountDebit
    #     )

    #     cummulativeTransactionAmount.total_success_amount = (
    #         totalSuccessTransactionAmount
    #     )
    # else:
    #     pass

    transaction.save()
    # cummulativeTransactionAmount.save()

    endTime = time.time() - startTime
    # Analyzing the efficiency of the API.
    apiEfficiency = settings.COMPLETE_TRANSACTION_DB_RESPONSE_TIME
    apiEfficiency.observe(endTime)


# getTransactionResponse - returns the transaction response that is to be sent to client
def getTransactionResponse(referenceId):
    transaction = Transaction.objects.get(reference_id=referenceId)

    transactionResponse = transaction.transaction_response
    transactionResponse = eval(transactionResponse)
    return transactionResponse


# pgDetails - returns the payment gateway details, requried for verification.
def pgDetails(authKey):
    startTime = time.time()

    pg = PG.objects.get(auth_key=authKey)

    endTime = time.time() - startTime
    # Analyzing the efficiency of the API.
    apiEfficiency = settings.RETRIEVE_PG_DETAILS_DB_RESPONSE_TIME
    apiEfficiency.observe(endTime)

    return pg
