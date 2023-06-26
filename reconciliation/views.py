# Importing Python Libraries
import logging
from dotenv import load_dotenv
from forex_python.converter import CurrencyRates
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view

# Importing Project Files
import common
import reconciliation.services.dbService as dbService

load_dotenv()
currencyRates = CurrencyRates()
db_logger = logging.getLogger("db")

# GST value - 18% (9% SGST, 9% CGST)
tax = 0.18

"""
"""


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def reconciliation(request, referenceId):
    if request.method != "POST":
        methodResult = common.methodChecker(method=request.method)
        return JsonResponse(methodResult, status=methodResult["statusCode"])

    try:
        # Fetching the net_amount_debit, payment_channel, payment_mode, country associated with the transaction, from the database.
        transactionDetails = dbService.transactionDetails(referenceId=referenceId)
        account = transactionDetails.account

        amount = transactionDetails.net_amount_debit
        paymentChannel = transactionDetails.payment_channel
        paymentMode = transactionDetails.payment_mode
        country = account.country

        # Calculating the total amount by adding tax.
        totalAmount = amount + amount * tax
        totalAmount = round(totalAmount, 5)

        # Fetching the fees charged by payment channel from MaxPay
        paymentChannelFees = dbService.getPaymentChannelFees(
            paymentChannel=paymentChannel, paymentMode=paymentMode, country=country
        )
        paymentChannelFees = totalAmount * paymentChannelFees
        paymentChannelFees = round(paymentChannelFees, 5)

        # Calulating the net amount left with MaxPay after deducting tax and fees.
        net = amount - paymentChannelFees
        net = round(net, 5)

        # Fetching the total amount of successful transactions.
        totalSuccessAmount = dbService.getTotalSuccessTransactionAmount(account=account)
        totalSuccessAmountDollar = currencyRates.convert(
            "INR", "USD", totalSuccessAmount
        )

        # Fetching the fees charged by MaxPay from account (depends on payment mode and total successful transaction amount).
        publisherFee = dbService.getMaxPayFees(
            account=account,
            paymentMode=paymentMode,
            transactionAmount=totalSuccessAmountDollar,
        )
        publisherFee = amount * publisherFee
        publisherFee = round(publisherFee, 5)

        # Calculating the amount to be payed to publisher after charging the fees
        payableToPublisher = amount - publisherFee
        payableToPublisher = round(payableToPublisher, 5)

        # Fetching the withhold tax.
        withHoldTax = dbService.getWithHoldTax(country=country)
        # Calculating the equilization levy using the withhold tax
        equilizationLevy = payableToPublisher * withHoldTax
        equilizationLevy = round(equilizationLevy, 5)

        # Calculating the gross profit of MaxPay after deducting the equilization levy and money payed to publisher from the net amount left.
        grossProfit = net - (payableToPublisher + equilizationLevy)
        grossProfit = round(grossProfit, 5)

        # Updating the reconciliation table with transactionDetails, expenses (amount to be paid to payment channel and publisher and total tax) and the total profit.
        dbService.reconciliationCreate(
            transaction=transactionDetails,
            tax=tax,
            totalAmount=totalAmount,
            paymentChannelFees=paymentChannelFees,
            net=net,
            publisherFee=publisherFee,
            payableToPublisher=payableToPublisher,
            equilizationLevy=equilizationLevy,
            grossProfit=grossProfit,
        )
    except:
        pass
