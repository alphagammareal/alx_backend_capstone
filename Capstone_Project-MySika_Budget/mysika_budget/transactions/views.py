# transactions/views.py

from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework import generics, permissions

from .models import Transaction
from .serializers import TransactionSerializer
from .forms import TransactionForm  # Make sure you have this form


# API Views 

class TransactionAPIListCreateView(generics.ListCreateAPIView):
    """
    API endpoint: GET/POST /api/transactions/
    - List all transactions for the logged-in user
    - Create a new transaction (expects JSON)
    """
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).select_related(
            "category", "wallet"
        )

    def perform_create(self, serializer):
        # Serializer already handles wallet assignment and validation
        serializer.save()


class TransactionAPIDetailView(generics.RetrieveDestroyAPIView):
    """
    API endpoint: GET/DELETE /api/transactions/<id>/
    """
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

# HTML Views 
class TransactionListView(LoginRequiredMixin, ListView):
    """
    HTML page: /transactions/
    Shows a list of user's transactions
    """
    model = Transaction
    template_name = "transactions/transaction_list.html"
    context_object_name = "transactions"
    paginate_by = 20  
    template_name = "transactions/transaction_list.html"

    def get_queryset(self):
        return (
            Transaction.objects.filter(user=self.request.user)
            .select_related("category", "wallet")
            .order_by("-created_at")
        )


class TransactionCreateView(LoginRequiredMixin, CreateView):
    """
    HTML page: /transactions/add/
    Form to add a new transaction with proper redirect on success
    """
    model = Transaction
    form_class = TransactionForm
    template_name = "transactions/add.html"
    success_url = reverse_lazy("transaction-list")

    def get_form_kwargs(self):
        """Pass the current user to the form for category filtering"""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Set user and wallet automatically before saving"""
        form.instance.user = self.request.user
        # Assuming each user has exactly one wallet (created on signup)
        form.instance.wallet = self.request.user.wallet
        return super().form_valid(form)