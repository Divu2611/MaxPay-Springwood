# Importing Libraries
from django.db import models, connection

from common.models import (
    Transaction,
    Account,
    FormDetails,
    ArchivedTransaction,
    CountryMapping,
    CurrencyMapping,
)


# CustomersProductsTransactions Table
class CustomerProductTransaction(models.Model):
    reference = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        to_field="reference_id",
        db_column="reference_id",
    )
    app_username = models.CharField(max_length=100, null=True)
    email_id = models.CharField(max_length=50, null=True)
    phone_number = models.CharField(max_length=15, null=True)
    cart_details = models.CharField(max_length=100, null=False)
    country = models.ForeignKey(
        CountryMapping, on_delete=models.CASCADE, to_field="country_code"
    )
    currency = models.ForeignKey(
        CurrencyMapping, on_delete=models.CASCADE, to_field="currency_code"
    )
    user_id = models.CharField(max_length=50, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "customers_products_transactions"


# ArchivedCustomersProductsTransactions Table
class ArchivedCustomerProductTransaction(models.Model):
    transaction = models.OneToOneField(
        ArchivedTransaction, on_delete=models.CASCADE, to_field="reference_id"
    )
    app_username = models.CharField(max_length=100, null=True)
    email_id = models.CharField(max_length=50, null=True)
    phone_number = models.CharField(max_length=15, null=True)
    cart_details = models.CharField(max_length=100, null=False)
    country = models.SmallIntegerField(null=False)
    currency = models.SmallIntegerField(null=False)
    user_id = models.CharField(max_length=50, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "archived_customers_products_transactions"


# MaxpayHostedPGResponse Table
class MaxpayHostedPGResponse(models.Model):
    reference = models.OneToOneField(
        Transaction, on_delete=models.CASCADE, to_field="reference_id"
    )
    html_response = models.BooleanField(null=False, default=False)
    response = models.CharField(max_length=50000, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "maxpay_hosted_pg_response"


# ArchivedMaxpayHostedPGResponse Table
class ArchivedMaxpayHostedPGResponse(models.Model):
    reference = models.OneToOneField(
        ArchivedTransaction, on_delete=models.CASCADE, to_field="reference_id"
    )
    html_response = models.BooleanField(null=False, default=False)
    response = models.CharField(max_length=50000, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "archived_maxpay_hosted_pg_response"
