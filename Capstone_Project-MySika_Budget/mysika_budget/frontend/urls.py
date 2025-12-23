from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('wallets/', views.wallets_view, name='wallets'),
    path('transactions/', views.transactions_view, name='transactions'),
    path('budgets/', views.budgets_view, name='budgets'),
    path('investments/', views.investments_view, name='investments'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('investments/add/', views.add_investment_view, name='add_investment'),
    path('transactions/add/', views.add_transaction_view, name='add_transaction'),
]
