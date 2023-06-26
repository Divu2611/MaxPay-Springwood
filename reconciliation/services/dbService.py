# Importing Python Libraries
from forex_python.converter import CurrencyRates

# Importing Project Models
from ..models import (
    Transaction,
    PaymentChannelFees,
    CumulativeTransactionAmount,
    MaxPayFees,
    WithholdTax,
    Reconciliation,
    CustomerProductTransaction,
)


currencyRates = CurrencyRates()


# transactionDetails - returns the netAmountDebit, paymentChannel, paymentMode and account details associated with the transaction.
def transactionDetails(referenceId):
    transaction = Transaction.objects.get(reference_id=referenceId)
    return transaction


# paymentChannelFees - returns the fees charged by payment channel from MaxPay.
def getPaymentChannelFees(paymentChannel, paymentMode, country):
    paymentChannelFees = PaymentChannelFees.objects.filter(
        payment_channel=paymentChannel, payment_mode=paymentMode, country=country
    )

    fees = paymentChannelFees.fees
    return fees


# getTotalSuccessTransactionAmount - returns the total amount for the successful transactions.
def getTotalSuccessTransactionAmount(account):
    cummulativeTransactionAmount = CumulativeTransactionAmount.objects.get(
        account=account
    )

    totalSuccessTransactionAmount = cummulativeTransactionAmount.total_success_amount
    return totalSuccessTransactionAmount


# getMaxPayFees - returns the fees charged by MaxPay from an account.
def getMaxPayFees(account, paymentMode, transactionAmount):
    maxpayFees = MaxPayFees.objects.filter(
        account=account,
        payment_mode=paymentMode,
        lower_transaction_bucket__lt=transactionAmount,
        higher_transaction_bucket__gte=transactionAmount,
    )

    fees = maxpayFees.fees
    return fees


# getWithHoldTax - returns the withhold tax of the country.
def getWithHoldTax(country):
    withHoldTax = WithholdTax.objects.filter(country=country)

    tax = withHoldTax.tax
    return tax


# reconciliationCreate - adds the new entry in reconciliation table.
def reconciliationCreate(
    transaction,
    tax,
    totalAmount,
    paymentChannelFees,
    net,
    publisherFee,
    payableToPublisher,
    equilizationLevy,
    grossProfit,
):
    # Fetching the customerProductTransaction details to know the currency in which transaction was made.
    customerProductTransaction = CustomerProductTransaction.objects.get(
        transaction=transaction
    )

    currency = customerProductTransaction.currency
    currencyCode = currency.currency

    # Getting the conversion rate from USD to currency in which transaction was made.
    currencyRate = currencyRates.get_rate("USD", currencyCode)

    reconciliation = Reconciliation(
        transaction=transaction,
        tax=tax,
        total_amount=totalAmount,
        payment_channel_fees=paymentChannelFees,
        net=net,
        publisher_fee=publisherFee,
        payable_to_publisher=payableToPublisher,
        equilization_levy=equilizationLevy,
        gross_profit=grossProfit,
        conversion_rate=currencyRate,
    )

    reconciliation.save()
