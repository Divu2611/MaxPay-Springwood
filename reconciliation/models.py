# Importing Files
from django.db import models

# Importing PRoject Models
from payment_response.models import PG, CumulativeTransactionAmount
from common.models import Account, CountryMapping, CurrencyMapping
from transactions.models import Transaction, CustomerProductTransaction


# MaxPayFees Table
class MaxPayFees(models.Model):
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, to_field="account_id", null=False
    )
    payment_mode = models.CharField(max_length=20, null=False)
    lower_transaction_bucket = models.FloatField(null=False)
    higher_transaction_bucket = models.FloatField(null=False)
    currency = models.ForeignKey(
        CurrencyMapping, on_delete=models.CASCADE, to_field="currency_code"
    )
    fees = models.FloatField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "maxpay_fees"


# PaymentChannelFees Table
class PaymentChannelFees(models.Model):
    payment_channel = models.ForeignKey(
        PG, on_delete=models.CASCADE, to_field="auth_key", null=False
    )
    payment_mode = models.CharField(max_length=20, null=False)
    country = models.ForeignKey(
        CountryMapping, on_delete=models.CASCADE, to_field="country_code"
    )
    fees = models.FloatField(null=False)
    tax = models.FloatField(null=False)
    total_fees = models.FloatField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payment_channel_fees"


# WithholdTax Table
class WithholdTax(models.Model):
    country = models.ForeignKey(
        CountryMapping, on_delete=models.CASCADE, to_field="country_code"
    )
    tax = models.FloatField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "withhold_tax"


# Reconciliation Table
class Reconciliation(models.Model):
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.SET_NULL,
        to_field="reference_id",
        null=True,
    )
    tax = models.FloatField(null=False, default=0.18)
    total_amount = models.FloatField(null=False)
    payment_channel_fees = models.FloatField(null=False)
    net = models.FloatField(null=False)
    publisher_fee = models.FloatField(null=False)
    payable_to_publisher = models.FloatField(null=False)
    equilization_levy = models.FloatField(null=False)
    gross_profit = models.FloatField(null=False)
    conversion_rate = models.FloatField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reconciliation"
