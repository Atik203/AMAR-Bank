
from django.urls import include, path

from .views import (DepositView, LoanListView, LoanPaidView, LoanRequestsView,
                    TransactionReportView, TransferView, WithdrawView)

urlpatterns = [
    path('deposit/',DepositView.as_view(),name='deposit_money'),
    path("report/", TransactionReportView.as_view(), name="transaction_report"),
    path("withdraw/", WithdrawView.as_view(), name="withdraw_money"),
    path("loan_request/", LoanRequestsView.as_view(), name="loan_request"),
    path("loans/", LoanListView.as_view(), name="loan_list"),
    path("loans/<int:loan_id>/", LoanPaidView.as_view(), name="pay"),
    path("transfer/", TransferView.as_view(), name="transfer_money"),
]

