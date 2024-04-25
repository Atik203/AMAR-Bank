
from django import forms

from accounts.models import UserBankAccount

from .models import Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'amount']
        
    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].widget = forms.HiddenInput()
        self.fields['transaction_type'].disabled = True
    
    def save(self,commit = True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save(commit=commit)

class DepositForm(TransactionForm):
    def clean_amount(self):
        min_deposit = 100
        amount = self.cleaned_data['amount']
        if amount < min_deposit:
            raise forms.ValidationError('Amount should be greater than 100')
        return amount
class WithdrawForm(TransactionForm):
    def clean_amount(self):
        account = self.account
        balance = account.balance
        min_withdraw = 100
        max_withdraw = 100000
        amount = self.cleaned_data['amount']
        if amount < min_withdraw:
            raise forms.ValidationError('Amount should be greater than 100')
        if amount > max_withdraw:
            raise forms.ValidationError('Amount should be less than 100000')
        if amount > balance:
            raise forms.ValidationError(f'Insufficient balance. Your balance is {balance}')
        if account.is_bankrupt:
            raise forms.ValidationError('Your account is bankrupt')
        return amount      

class LoanForm(TransactionForm):
    def clean_amount(self):
        account = self.account
        balance = account.balance
        max_loan = balance * 3
        amount = self.cleaned_data['amount']
        if amount > max_loan:
            raise forms.ValidationError('Amount should be less than 100000')
        return amount

class TransferForm(TransactionForm):
    to_account_number = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.from_account = kwargs.pop('from_account')
        super().__init__(*args, **kwargs)

    def clean_to_account_number(self):
        to_account_number = self.cleaned_data['to_account_number']
        if not UserBankAccount.objects.filter(account_number=to_account_number).exists():
            raise forms.ValidationError('Invalid account number')
        return to_account_number

    def save(self, commit=True):
        self.instance.account = self.from_account
        self.instance.balance_after_transaction = self.from_account.balance

        to_account_number = self.cleaned_data['to_account_number']
        to_account = UserBankAccount.objects.get(account_number=to_account_number)
        self.instance.to_account = to_account
        self.instance.to_account_balance_after_transaction = to_account.balance

        return super().save(commit=commit)