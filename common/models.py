# Importing Libraries
from django.db import models, connection


# CountryMapping Table
class CountryMapping(models.Model):
    country = models.CharField(max_length=50, null=False, unique=True)
    country_code = models.SmallIntegerField(null=False, unique=True)

    class Meta:
        db_table = "country_mapping"


# CurrencyMapping Table
class CurrencyMapping(models.Model):
    currency = models.CharField(max_length=5, null=False, unique=True)
    country = models.ForeignKey(
        CountryMapping, on_delete=models.CASCADE, to_field="country_code"
    )
    currency_code = models.SmallIntegerField(null=False, unique=True)

    class Meta:
        db_table = "currency_mapping"


# Organization Table
class Organization(models.Model):
    organization_id = models.CharField(
        max_length=100, null=False, blank=False, unique=True
    )
    org_name = models.CharField(max_length=100, null=False)
    country = models.ForeignKey(
        CountryMapping, on_delete=models.SET_NULL, to_field="country_code", null=True
    )
    is_active = models.BooleanField(default=False, null=False)
    document_link = models.CharField(max_length=500, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "organizations"

    def __str__(self):
        return str(self.org_name)


# Accounts Table
class Account(models.Model):
    account_id = models.CharField(max_length=100, null=False, blank=False, unique=True)
    account_secret_key = models.CharField(max_length=100, null=False, blank=False)
    name = models.CharField(max_length=100, null=False)
    is_web = models.BooleanField(default=False, null=False)
    is_android = models.BooleanField(default=False, null=False)
    is_ios = models.BooleanField(default=False, null=False)
    is_active = models.BooleanField(default=False, null=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, to_field="organization_id"
    )
    country = models.ForeignKey(
        CountryMapping, on_delete=models.SET_NULL, to_field="country_code", null=True
    )
    source = models.CharField(max_length=100, null=False)
    created_by = models.CharField(max_length=100, null=False)
    updated_by = models.CharField(max_length=100, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounts"

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if not self.pk:
            # Generate unique id using the function defined in PostgreSQL
            cursor = connection.cursor()

            cursor.execute("SELECT generate_account_id()")
            account_id = cursor.fetchone()[0]
            self.account_id = account_id

            cursor.execute("SELECT generate_account_secret_key()")
            account_secret_key = cursor.fetchone()[0]
            self.account_secret_key = account_secret_key
        super(Account, self).save(*args, **kwargs)


# Transactions Table
class Transaction(models.Model):
    transaction_id = models.CharField(max_length=100, null=False, blank=False)
    reference_id = models.CharField(
        max_length=100, null=False, blank=False, unique=True
    )
    payment_mode = models.CharField(max_length=20, null=True)
    checkout_flow = models.CharField(max_length=20, null=False, default="MaxPay Hosted")
    account = models.ForeignKey(
        Account, on_delete=models.SET_NULL, to_field="account_id", null=True
    )
    amount = models.FloatField(null=False)
    discount = models.FloatField(null=True)
    net_amount_debit = models.FloatField(null=True)
    payment_channel = models.CharField(max_length=20, null=True)
    transaction_status_code = models.SmallIntegerField(null=False)
    transaction_status = models.CharField(max_length=30, null=False)
    transaction_response = models.CharField(max_length=10000, null=True)
    meta_data = models.CharField(max_length=10000, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transactions"

    def __str__(self):
        return str(self.transaction_id)

    def save(self, *args, **kwargs):
        if not self.pk:
            # Generate unique id using the function defined in PostgreSQL
            cursor = connection.cursor()
            cursor.execute("SELECT generate_reference_id()")
            reference_id = cursor.fetchone()[0]
            self.reference_id = reference_id
        super(Transaction, self).save(*args, **kwargs)


# ArchivedTransactions Table
class ArchivedTransaction(models.Model):
    transaction_id = models.CharField(max_length=100, null=False, blank=False)
    reference_id = models.CharField(
        max_length=100, null=False, blank=False, unique=True
    )
    payment_mode = models.CharField(max_length=20, null=True)
    checkout_flow = models.CharField(max_length=20, null=False, default="MaxPay Hosted")
    account_id = models.CharField(max_length=100, null=False, blank=False)
    amount = models.FloatField(null=False)
    discount = models.FloatField(null=True)
    net_amount_debit = models.FloatField(null=True)
    payment_channel = models.CharField(max_length=20, null=True)
    transaction_status_code = models.SmallIntegerField(null=False)
    transaction_status = models.CharField(max_length=30, null=False)
    transaction_response = models.CharField(max_length=10000, null=True)
    meta_data = models.CharField(max_length=10000, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "archived_transactions"

    def __str__(self):
        return str(self.transaction_id)


# Form Details table
class FormDetails(models.Model):
    reference = models.OneToOneField(
        Transaction, on_delete=models.CASCADE, to_field="reference_id"
    )
    account = models.OneToOneField(
        Account, on_delete=models.CASCADE, to_field="account_id", unique=False
    )
    form_details = models.CharField(max_length=10000, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "form_details"


# Archived Form Details table
class ArchivedFormDetails(models.Model):
    reference = models.OneToOneField(
        ArchivedTransaction, on_delete=models.CASCADE, to_field="reference_id"
    )
    account_id = models.CharField(max_length=100, null=False, blank=False)
    form_details = models.CharField(max_length=10000, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "archived_form_details"
