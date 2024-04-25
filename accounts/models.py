from django.contrib.auth.models import User
from django.db import models
from django.forms import DateInput

from .constants import ACCOUNT_TYPE, GENDER_TYPE


class UserBankAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='account')
    account_type = models.CharField(max_length=100,choices=ACCOUNT_TYPE,)
    account_number = models.CharField(max_length=100,unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    birthday = models.DateField(null=True,blank=True)
    gender = models.CharField(max_length=100,choices=GENDER_TYPE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    is_bankrupt = models.BooleanField(default=False,blank=True,null=True)
    
    def __str__(self):
        return self.user.username+"-"+self.account_number

class UserAddress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='address')
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=100)
    
    def __str__(self):
        return self.user.username
    