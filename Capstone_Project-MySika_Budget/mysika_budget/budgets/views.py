from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Budget
from .serializers import BudgetSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.utils import timezone
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Budget
from .forms import BudgetForm


# Create your views here.
class BudgetListCreateView(generics.ListCreateAPIView):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # optionally filter by active or category via ?status=active or ?category=Food
        qs = Budget.objects.filter(user=self.request.user)
        status_q = self.request.query_params.get("status")
        category_q = self.request.query_params.get("category")
        if status_q:
            qs = qs.filter(status=status_q)
        if category_q:
            qs = qs.filter(category__iexact=category_q)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BudgetDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def budget_progress_view(request, pk):
    """
    Returns progress details for a budget:
    - total_spent
    - amount_limit
    - percent_used
    - status
    """
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    percent = 0.0
    if budget.amount_limit and float(budget.amount_limit) > 0:
        percent = float((budget.total_spent / budget.amount_limit) * 100)
    data = {
        "id": budget.id,
        "category": budget.category,
        "total_spent": str(budget.total_spent),
        "amount_limit": str(budget.amount_limit),
        "percent_used": percent,
        "status": budget.status,
        "start_date": budget.start_date,
        "end_date": budget.end_date,
    }
    return Response(data, status=status.HTTP_200_OK)

class BudgetListHTMLView(LoginRequiredMixin, ListView):
    model = Budget
    template_name = "budgets/budget_list.html"
    context_object_name = "budgets"

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user).select_related('category').order_by('-start_date')

class BudgetCreateHTMLView(LoginRequiredMixin, CreateView):
    model = Budget
    form_class = BudgetForm
    template_name = "budgets/budget_form.html"
    success_url = reverse_lazy("budget-list-html")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)