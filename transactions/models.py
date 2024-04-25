from django.db import models

from accounts.models import UserBankAccount

from .constants import TRANSACTION_TYPE


# Create your models here.
class Transaction(models.Model):
    account = models.ForeignKey(UserBankAccount, on_delete=models.CASCADE,related_name='transactions')
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPE,null=True,blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after_transaction = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    loan_approved = models.BooleanField(default=False)
    to_account = models.ForeignKey(UserBankAccount, on_delete=models.CASCADE,related_name='received',null=True,blank=True)
    class Meta:
        ordering = ['timestamp']
    