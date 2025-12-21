
from django.urls import path
from .views import BudgetListCreateView, BudgetDetailView, budget_progress_view

urlpatterns = [
    path("", BudgetListCreateView.as_view(), name="budget-list-create"),
    path("<int:pk>/", BudgetDetailView.as_view(), name="budget-detail"),
    path("<int:pk>/progress/", budget_progress_view, name="budget-progress"),
]
