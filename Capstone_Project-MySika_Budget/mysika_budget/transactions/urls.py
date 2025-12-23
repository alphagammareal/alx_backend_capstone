from django.urls import path
from .views import (
    TransactionAPIListCreateView,
    TransactionAPIDetailView,
    TransactionListView,       
    TransactionCreateView,  
)

urlpatterns = [
    # API endpoints (JSON)
    path("api/", TransactionAPIListCreateView.as_view(), name="api-transaction-list-create"),
    path("api/<int:pk>/", TransactionAPIDetailView.as_view(), name="api-transaction-detail"),

    # HTML pages
    path("", TransactionListView.as_view(), name="transaction-list"),
    path("add/", TransactionCreateView.as_view(), name="add_transaction"),
]