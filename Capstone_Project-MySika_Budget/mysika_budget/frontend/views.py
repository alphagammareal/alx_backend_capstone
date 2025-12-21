from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from wallets.models import Wallet
from transactions.models import Transaction
from budgets.models import Budget
from investments.models import Investment
from decimal import Decimal
from django.db.models import Sum

@login_required
def dashboard(request):
    user = request.user

    # Wallet summary
    wallets = Wallet.objects.filter(user=user)
    wallet_labels = [w.name for w in wallets]
    wallet_values = [float(w.balance) for w in wallets]
    total_balance = sum(wallet_values)

    # Transactions summary
    transactions = Transaction.objects.filter(user=user)
    total_income = transactions.filter(transaction_type='INCOME').aggregate(total=Sum('amount'))['total'] or 0
    total_expense = transactions.filter(transaction_type='EXPENSE').aggregate(total=Sum('amount'))['total'] or 0
    net_balance = total_income - total_expense

    # Expense by category
    categories = transactions.values_list('category__name', flat=True).distinct()
    category_labels = []
    category_values = []
    for cat in categories:
        total = transactions.filter(category__name=cat, transaction_type='EXPENSE').aggregate(total=Sum('amount'))['total'] or 0
        category_labels.append(cat)
        category_values.append(float(total))

    # Investments summary
    investments = Investment.objects.filter(user=user)
    investment_labels = []
    investment_values = []
    for inv in investments:
        investment_labels.append(inv.stock.symbol)
        latest_price = inv.stock.prices.first()
        if latest_price:
            investment_values.append(float(inv.quantity * latest_price.price))
        else:
            investment_values.append(0)
    total_portfolio_value = sum(investment_values)

    context = {
        'wallet_labels': wallet_labels,
        'wallet_values': wallet_values,
        'total_balance': total_balance,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_balance': net_balance,
        'category_labels': category_labels,
        'category_values': category_values,
        'investment_labels': investment_labels,
        'investment_values': investment_values,
        'total_portfolio_value': total_portfolio_value,
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
        expense_data.append({'category': cat, 'total': float(total)})

    context = {
        'expense_data': expense_data
    }

    return render(request, 'analytics.html', context)
