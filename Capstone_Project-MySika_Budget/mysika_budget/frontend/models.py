from django.db import models
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from wallets.models import Wallet
from transactions.models import Transaction
from budgets.models import Budget
from investments.models import Investment, Stock
from decimal import Decimal
from django.db.models import Sum, F, FloatField

# Create your models here.
@login_required
def dashboard(request):
    user = request.user

    # Wallet summary
    wallets = Wallet.objects.filter(user=user)
    total_balance = wallets.aggregate(total=Sum('balance'))['total'] or 0
    wallet_count = wallets.count()

    # Transactions summary
    transactions = Transaction.objects.filter(user=user)
    total_income = transactions.filter(transaction_type='INCOME').aggregate(total=Sum('amount'))['total'] or 0
    total_expense = transactions.filter(transaction_type='EXPENSE').aggregate(total=Sum('amount'))['total'] or 0
    net_balance = total_income - total_expense

    # Investments summary
    investments = Investment.objects.filter(user=user)
    total_portfolio_value = 0
    for inv in investments:
        latest_price = inv.stock.prices.first()
        if latest_price:
            total_portfolio_value += latest_price.price * inv.quantity
    investment_count = investments.count()

    context = {
        'total_balance': total_balance,
        'wallet_count': wallet_count,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_balance': net_balance,
        'total_portfolio_value': total_portfolio_value,
        'investment_count': investment_count,
    }

    return render(request, 'dashboard.html', context)

@login_required
def wallets_view(request):
    wallets = Wallet.objects.filter(user=request.user)
    return render(request, 'wallets.html', {'wallets': wallets})

@login_required
def transactions_view(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'transactions.html', {'transactions': transactions})

@login_required
def budgets_view(request):
    budgets = Budget.objects.filter(user=request.user)
    return render(request, 'budgets.html', {'budgets': budgets})

@login_required
def investments_view(request):
    investments = Investment.objects.filter(user=request.user)
    return render(request, 'investments.html', {'investments': investments})

@login_required
def analytics_view(request):
    transactions = Transaction.objects.filter(user=request.user)
    categories = transactions.values_list('category__name', flat=True).distinct()
    expense_data = []
    for cat in categories:
        total = transactions.filter(category__name=cat, transaction_type='EXPENSE').aggregate(total=Sum('amount'))['total'] or 0
        expense_data.append({'category': cat, 'total': total})

    context = {
        'expense_data': expense_data
    }

    return render(request, 'analytics.html', context)