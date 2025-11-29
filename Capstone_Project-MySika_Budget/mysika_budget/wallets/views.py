# views.py - Explained in detail (Python comment format)

from django.shortcuts import render
from rest_framework.views import APIView                 # Base class for DRF views
from rest_framework.response import Response             # DRF's version of HttpResponse (handles JSON)
from rest_framework.permissions import IsAuthenticated  # Only logged-in users can access these endpoints
from rest_framework import status                        # For HTTP status codes like 400, 201, etc.
from .models import Wallet, Transaction                  # Our custom models
from .serializers import WalletSerializer, TransactionSerializer  # Convert model instances to JSON
from django.contrib.auth.models import User              # Default Django User model

# 1. GET current user's wallet (creates one if it doesn't exist)

class WalletView(APIView):
    permission_classes = [IsAuthenticated]  # User must be logged in

    def get(self, request):
        # Get or create a wallet for the current logged-in user
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        
        # Serialize the wallet object to JSON-friendly format
        serializer = WalletSerializer(wallet)
        
        # Return the wallet data (balance, user, etc.)
        return Response(serializer.data)


# 2. Deposit money into the user's wallet

class DepositView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get("amount")          # Expecting JSON like {"amount": "50.00"}
        
        if not amount:
            return Response({"error": "Amount is required"}, status=400)
        
        # Get or create wallet for current user
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        
        # Add the amount to balance (convert to float)
        wallet.balance += float(amount)
        wallet.save()
        
        # Record the transaction in history
        Transaction.objects.create(
            wallet=wallet,
            amount=amount,
            transaction_type="DEPOSIT",
            description="Deposit to wallet"
        )
       
        # Success response with new balance
        return Response({
            "message": "Deposit successful",
            "balance": wallet.balance
        })


# 3. Withdraw money from the user's wallet
class WithdrawView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get("amount")
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        
        # Check if user has enough balance
        if wallet.balance < float(amount):
            return Response({"error": "Insufficient balance"}, status=400)
        
        # Deduct amount
        wallet.balance -= float(amount)
        wallet.save()
        
        # Record withdrawal transaction
        Transaction.objects.create(
            wallet=wallet,
            amount=amount,
            transaction_type="WITHDRAW",
            description="Money withdrawn"
        )
        
        return Response({
            "message": "Withdraw successful",
            "balance": wallet.balance
        })


# 4. Transfer money from current user to another user (by user ID)
class TransferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        receiver_id = request.data.get("receiver_id")   # ID of the user receiving money
        amount = float(request.data.get("amount"))      # Amount to transfer
        
        # Sender's wallet
        sender_wallet, _ = Wallet.objects.get_or_create(user=request.user)
        
        # Find receiver user and their wallet
        try:
            receiver = User.objects.get(id=receiver_id)
            receiver_wallet, _ = Wallet.objects.get_or_create(user=receiver)
        except User.DoesNotExist:
            return Response({"error": "Receiver not found"}, status=400)
        
        # Check if sender has enough money
        if sender_wallet.balance < amount:
            return Response({"error": "Insufficient funds"}, status=400)
        
        # Perform the transfer 
        sender_wallet.balance -= amount
        sender_wallet.save()
        
        receiver_wallet.balance += amount
        receiver_wallet.save()
        
        # Record transaction for sender
        Transaction.objects.create(
            wallet=sender_wallet,
            amount=amount,
            transaction_type="TRANSFER_OUT",
            description=f"Transfer to {receiver.username}"
        )
        
        # Record transaction for receiver
        Transaction.objects.create(
            wallet=receiver_wallet,
            amount=amount,
            transaction_type="TRANSFER_IN",
            description=f"Transfer from {request.user.username}"
        )
        
        return Response({"message": "Transfer successful"})


# 5. Get transaction history for the current user

class TransactionHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get user's wallet
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        
        # Get all transactions related to this wallet, newest first
        transactions = wallet.transactions.order_by("-timestamp")
        
        # Serialize list of transactions
        serializer = TransactionSerializer(transactions, many=True)
        
        # Return JSON list of transactions
        return Response(serializer.data)