from django.urls import path
from .views import (
    IncomeExpenseView,
    CategoryBreakdownView,
    CashflowView,
)

urlpatterns = [
    path("summary/", IncomeExpenseView.as_view(), name="income-expense"),
    path("categories/", CategoryBreakdownView.as_view(), name="category-breakdown"),
    path("cashflow/", CashflowView.as_view(), name="cashflow"),
]
