# Importing Libraries
from django.db import models, connection

# Importing Project Models
from common.models import Transaction, FormDetails, Account


# PG Table
class PG(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False, unique=True)
    auth_key = models.CharField(max_length=20, null=False, blank=False, unique=True)

    class Meta:
        db_table = "pg"

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if not self.pk:
            # Generate unique id using the function defined in PostgreSQL
            cursor = connection.cursor()
            cursor.execute("SELECT generate_auth_key()")
            auth_key = cursor.fetchone()[0]
            self.auth_key = auth_key
        super(PG, self).save(*args, **kwargs)


# CumulativeTransacitionAmount Table
class CumulativeTransactionAmount(models.Model):
    account = models.ForeignKey(
        Account, on_delete=models.SET_NULL, to_field="account_id", null=True
    )
    total_success_amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cumulative_transaction_amount"
