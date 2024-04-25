from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMessage
from django.db.models import Sum
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView

from accounts.models import UserBankAccount

from .constants import DEPOSIT, LOAN, LOAN_PAID, RECEIVE, TRANSFER, WITHDRAWAL
from .forms import DepositForm, LoanForm, TransferForm, WithdrawForm
from .models import Transaction


def send_transaction_email(user,amount,subject,template_name):
    mail_subject = subject
    message = render_to_string(template_name, {
        'user': user,
        'amount': amount,
    })
    send_email = EmailMessage(
        mail_subject,
        message,
        to=[user.email]
    )
    send_email.content_subtype = 'html'
    send_email.send()



class TransactionCreateMixin(LoginRequiredMixin,CreateView):
    template_name = 'transactions_form.html'
    model = Transaction
    title = ''
    success_url = reverse_lazy('transaction_report')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'account': self.request.user.account}) 
        return kwargs
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "title": self.title,
        })
        return context

class DepositView(TransactionCreateMixin):
    form_class = DepositForm
    title = 'Deposit'
    
    def get_initial(self):
        initial = {'transaction_type': DEPOSIT}
        return initial
    
    
    def form_valid(self, form):
        amount = form.cleaned_data['amount']
        account = self.request.user.account
        account.balance += amount
        account.save(
            update_fields=['balance']
        )
        messages.success(
            self.request,
            f'{"{:,.2f}".format(float(amount))}$ was deposited to your account successfully'
        )
        send_transaction_email(self.request.user,amount,"Deposit Confirmation",'deposit_email.html')
        return super().form_valid(form)

class WithdrawView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = 'Withdraw'
    
    def get_initial(self):
        initial = {'transaction_type': WITHDRAWAL}
        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data['amount']
        account = self.request.user.account
        account.balance -= amount
        account.save(
            update_fields=['balance']
        )
        messages.success(
            self.request,
            f'{"{:,.2f}".format(float(amount))}$ was withdrawn from your account successfully'
        )
        send_transaction_email(self.request.user,amount,"Withdraw Confirmation",'withdrawal_email.html')
        return super().form_valid(form)

class LoanRequestsView(TransactionCreateMixin):
    form_class = LoanForm
    title = 'Request Loan'
    
    def get_initial(self):
        initial = {'transaction_type': LOAN}
        return initial
    def form_valid(self, form):
        amount = form.cleaned_data['amount']
        current_loan_count = Transaction.objects.filter(account = self.request.user.account,
            transaction_type=LOAN,
            loan_approved=True
        ).count()
        if current_loan_count > 3:
            messages.warning(
                self.request,
                'You have crossed the limit of 3 loans at a time'
            )
            return self.form_invalid(form)
        messages.success(
            self.request,
            f'{"{:,.2f}".format(float(amount))}$ was deposited to your account successfully'
        )
        send_transaction_email(self.request.user,amount,"Loan Request Confirmation",'loan_email.html')
        return super().form_valid(form)

class TransactionReportView(LoginRequiredMixin,ListView):
    template_name = 'transactions_report.html'
    model = Transaction
    balance = 0.0
    
    def get_queryset(self):
        querySet = super().get_queryset().filter(account=self.request.user.account)
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')            
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            querySet = querySet.filter(
                timestamp__date__gte=start_date,timestamp__date__lte=end_date
            )
            self.balance = Transaction.objects.filter(timestamp__date__gte=start_date,timestamp__date__lte=end_date).aggregate(Sum('amount'))['amount__sum']
        else:
            self.balance = self.request.user.account.balance
        
        return querySet.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user.account,
        })
        return context        
    
class LoanPaidView(LoginRequiredMixin,View):
    def get(self,request,loan_id):
        loan = get_object_or_404(Transaction,id=loan_id)
        if loan.loan_approved:
            user_account = loan.account
            if loan.amount <user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()
                loan.loan_approved = True
                loan.transaction_type = LOAN_PAID
                loan.save()
                messages.success(
                    request,
                    f'{"{:,.2f}".format((loan.amount))}$ was paid successfully'
                )
                return redirect('loan_list')
            else:
                messages.warning(
                    request,
                    'You do not have enough balance to pay the loan'
                )    
        return redirect('loan_list')
    
class LoanListView(LoginRequiredMixin,ListView):
    model = Transaction
    template_name = 'loan_request.html'
    context_object_name = 'loans'
    
    def get_queryset(self):
        user_account = self.request.user.account
        queryset = Transaction.objects.filter(account = user_account,transaction_type = LOAN)
        return queryset
                

def transfer_send_email(user,amount,subject,template_name,account_number):
    mail_subject = subject
    message = render_to_string(template_name, {
        'user': user,
        'amount': amount,
        'account_number':account_number,
    })
    send_email = EmailMessage(
        mail_subject,
        message,
        to=[user.email]
    )
    send_email.content_subtype = 'html'
    send_email.send()
    
            
class TransferView(TransactionCreateMixin):
    form_class = TransferForm
    title = 'Transfer Money'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'from_account': self.request.user.account})
        return kwargs
    
    def get_initial(self):
        initial = {'transaction_type': TRANSFER}
        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data['amount']
        to_account_number = form.cleaned_data['to_account_number']
        from_account = self.request.user.account
        
        if from_account.balance < amount:
            messages.warning(
                self.request,
                'You do not have enough balance to transfer'
            )
            return self.form_invalid(form)
        
        to_account = get_object_or_404(UserBankAccount,account_number=to_account_number)
        
        from_account.balance -= amount
        to_account.balance += amount
        
        receiver_transaction = Transaction(
            account=to_account,
            to_account=from_account,
            amount=amount,
            transaction_type=RECEIVE,
            balance_after_transaction=to_account.balance,
        )
        receiver_transaction.save()
        
        from_account.save(update_fields=['balance'])
        to_account.save(update_fields=['balance'])
        
        messages.success(
            self.request,
            f'{"{:,.2f}".format(float(amount))}$ was transferred to account {to_account_number} successfully'
        )
        transfer_send_email(self.request.user,amount,"Transfer Confirmation",'transfer_email.html',to_account_number)
        transfer_send_email(to_account.user,amount,"Transfer Confirmation",'receive_email.html',from_account.account_number)
        return super().form_valid(form)
        
         
                  