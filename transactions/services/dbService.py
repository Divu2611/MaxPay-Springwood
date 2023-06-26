# Importing Python Libraries.
import time
from django.conf import settings
from django.db.models import F

# Importing Project Files.
from ..models import (
    Transaction,
    CustomerProductTransaction,
    Account,
    FormDetails,
    MaxpayHostedPGResponse,
    CountryMapping,
    CurrencyMapping,
)


# transactionCreate - creates a new entry in the Transactions, CustomerProductTransaction and FormDetails Table.
def transactionCreate(transactionId, transactionStatus, account, requestDetails):
    startTime = time.time()

    # updating Transactions table.
    newTransaction = Transaction(
        transaction_id=transactionId,
        payment_mode=requestDetails["paymentMode"]
        if "paymentMode" in requestDetails
        else None,
        checkout_flow="Merchant Hosted"
        if "paymentMode" in requestDetails
        else "MaxPay Hosted",
        account=account,
        amount=requestDetails["amount"],
        transaction_status_code=settings.MAPPINGS[transactionStatus],
        transaction_status=transactionStatus,
        transaction_response=None,
    )
    newTransaction.save()

    # getting country and currency details using the countryCode and currencyCode.
    country = CountryMapping.objects.get(country_code=requestDetails["countryCode"])
    currency = CurrencyMapping.objects.get(currency_code=requestDetails["currencyCode"])

    # updating CustomerProductTransaction table.
    newCustomerProductTransaction = CustomerProductTransaction(
        reference=newTransaction,
        app_username=requestDetails["firstName"],
        email_id=requestDetails["emailId"]
        if not (account.account_id == "3679f8")
        else None,
        phone_number=requestDetails["phoneNumber"],
        cart_details=requestDetails["productInformation"],
        country=country,
        currency=currency,
        user_id=requestDetails["emailId"] if account.account_id == "3679f8" else None,
    )
    newCustomerProductTransaction.save()

    # updating FormDetails Table.
    newDetails = FormDetails(
        reference=newTransaction, account=account, form_details=requestDetails
    )
    newDetails.save()

    requestDetails["referenceId"] = newTransaction.reference_id
    requestDetails["transactionId"] = newTransaction.transaction_id

    endTime = time.time() - startTime
    # Analyzing the efficiency of the API.
    dbEfficiency = settings.TRANSACTION_CREATE_DB_RESPONSE_TIME
    dbEfficiency.observe(endTime)

    return requestDetails


# transactionDetails - returns the transaction details of given accountId and transactionId.
def transactionDetails(transactionId, accountId):
    startTime = time.time()

    transaction = Transaction.objects.filter(
        account_id=accountId, transaction_id=transactionId
    ).first()

    endTime = time.time() - startTime
    # Analyzing the efficiency of the API.
    dbEfficiency = settings.RETRIEVE_TRANSACTION_DETAILS_DB_RESPONSE_TIME
    dbEfficiency.observe(endTime)

    return transaction


# transactionExists - verifies if transactionId exists for a given accountId.
def transactionExists(accountId, transactionId):
    startTime = time.time()

    exists = (
        Transaction.objects.filter(account_id=accountId)
        .filter(transaction_id=transactionId)
        .exists()
    )

    endTime = time.time() - startTime
    # Analyzing the efficiency of the API.
    dbEfficiency = settings.CHECK_TRANSACTION_EXISTS_DB_RESPONSE_TIME
    dbEfficiency.observe(endTime)

    return exists


# updateTransactionStatus - updates the transactionStatus and paymentChannel in the Transactions table.
def updateTransactionStatus(transactionStatus, paymentChannel, referenceId, metaData):
    startTime = time.time()

    transaction = Transaction.objects.get(reference_id=referenceId)

    transaction.payment_channel = paymentChannel
    transaction.transaction_status_code = settings.MAPPINGS[transactionStatus]
    transaction.transaction_status = transactionStatus
    transaction.meta_data = metaData

    transaction.save()

    endTime = time.time() - startTime
    # Analyzing the efficiency of the API.
    apiEfficiency = settings.UPDATE_TRANSACTION_STATUS_DB_RESPONSE_TIME
    apiEfficiency.observe(endTime)


# getAccount - returns the account of given accountId, requried for verification.
def getAccount(accountId):
    startTime = time.time()

    account = Account.objects.get(account_id=accountId)

    endTime = time.time() - startTime
    # Analyzing the efficiency of the API.
    apiEfficiency = settings.RETRIEVE_ACCOUNT_DB_RESPONSE_TIME
    apiEfficiency.observe(endTime)

    return account


# createPGResponse - creates a new entry in the MaxpayHostedPGResponse table.
def createPGResponse(referenceId, htmlResponse, response):
    startTime = time.time()

    transaction = Transaction.objects.get(reference_id=referenceId)

    newPGResponse = MaxpayHostedPGResponse(
        reference=transaction, html_response=htmlResponse, response=response
    )
    newPGResponse.save()

    endTime = time.time() - startTime
    # Analyzing the efficiency of the API.
    apiEfficiency = settings.PG_RESPONSE_CREATE_DB_RESPONSE_TIME
    apiEfficiency.observe(endTime)


# getPGResponse - returns the PG response (either HTML response or a URL).
def getPGResponse(referenceId):
    startTime = time.time()

    pgResponse = MaxpayHostedPGResponse.objects.get(reference_id=referenceId)

    endTime = time.time() - startTime
    # Analyzing the efficiency of the API.
    apiEfficiency = settings.RETRIEVE_PG_RESPONSE_DB_RESPONSE_TIME
    apiEfficiency.observe(endTime)

    return pgResponse


# getLocation - verifies if the countryCode and currencyCode are correct.
def getLocation(countryCode, currencyCode):
    countryExists = CountryMapping.objects.filter(country_code=countryCode).exists()
    currencyExists = CurrencyMapping.objects.filter(currency_code=currencyCode).exists()

    return countryExists and currencyExists
