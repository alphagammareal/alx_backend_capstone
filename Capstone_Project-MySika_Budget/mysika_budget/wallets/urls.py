
from django.urls import path
# Importing our API views from the current app's views.py
from .views import (
    WalletView,           # GET: Returns current user's wallet info
    DepositView,          # POST: Add money to user's wallet
    WithdrawView,         # POST: Withdraw money from user's wallet
    TransferView,         # POST: Transfer money to another user
    TransactionHistoryView # GET: Returns user's full transaction history
)

# List of URL patterns for the wallet API
urlpatterns = [
    # 1. Get current user's wallet (balance, etc.)
    # GET  /wallet/               returns wallet data
    path('wallet/', WalletView.as_view(), name="wallet"),
    # 2. Deposit money into wallet
    # POST /deposit/              body: {"amount": "100.00"}
    path('deposit/', DepositView.as_view(), name="deposit"),
    # 3. Withdraw money from wallet
    # POST /withdraw/             body: {"amount": "50.00"}
    path('withdraw/', WithdrawView.as_view(), name="withdraw"),
    # 4. Transfer money to another user
    # POST /transfer/             body: {"receiver_id": 5, "amount": "25.00"}
    path('transfer/', TransferView.as_view(), name="transfer"),
    # 5. Get full transaction history for the logged-in user
    # GET  /transactions/         returns list of all transactions
    path('transactions/', TransactionHistoryView.as_view(), name="transactions"),
]


# Then final endpoints will be:
#   GET    http://127.0.0.1:8000/api/wallet/wallet/
#   POST   http://127.0.0.1:8000/api/wallet/deposit/
#   POST   http://127.0.0.1:8000/api/wallet/withdraw/
#   POST   http://127.0.0.1:8000/api/wallet/transfer/
#   GET    http://127.0.0.1:8000/api/wallet/transactions/

# All these endpoints require authentication (IsAuthenticated in views)