# frontend/views.py - FINAL CORRECTED VERSION

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from decimal import Decimal
from datetime import datetime
import json

from wallets.models import Wallet
from transactions.models import Transaction
from categories.models import Category
from budgets.models import Budget
from investments.models import Investment


@login_required
def dashboard(request):
    user = request.user

    # Wallet summary (single wallet per user)
    wallet, created = Wallet.objects.get_or_create(user=user)
    total_balance = float(wallet.balance)

    # All transactions for this user (linked directly via user field)
    transactions = Transaction.objects.filter(user=user)

    # Income & Expense totals
    total_income = transactions.filter(transaction_type='INCOME') \
                              .aggregate(total=Sum('amount'))['total'] or 0
    total_expense = transactions.filter(transaction_type='EXPENSE') \
                               .aggregate(total=Sum('amount'))['total'] or 0
    net_balance = total_income - total_expense

    # Expense by category
    expense_by_category = transactions.filter(transaction_type='EXPENSE') \
                                     .values('category__name') \
                                     .annotate(total=Sum('amount')) \
                                     .order_by('-total')

    category_labels = [item['category__name'] or 'Uncategorized' for item in expense_by_category]
    category_values = [float(item['total'] or 0) for item in expense_by_category]

    # Investments summary
    investments = Investment.objects.filter(user=user)
    investment_labels = []
    investment_values = []
    for inv in investments:
        investment_labels.append(inv.stock.symbol if hasattr(inv.stock, 'symbol') else 'Unknown')
        latest_price = inv.stock.prices.first() if hasattr(inv.stock, 'prices') else None
        if latest_price:
            investment_values.append(float(inv.quantity * latest_price.price))
        else:
            investment_values.append(0)
    total_portfolio_value = sum(investment_values)

    context = {
        'total_balance': total_balance,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_balance': net_balance,
        'category_labels': category_labels,
        'category_values': category_values,
        'investment_labels': investment_labels,
        'investment_values': investment_values,
        'total_portfolio_value': total_portfolio_value,
        'year': datetime.now().year,
    }

    return render(request, 'dashboard.html', context)


@login_required
def wallets_view(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    return render(request, 'wallets.html', {'wallet': wallet})


@login_required
def transactions_view(request):
    transactions = Transaction.objects.filter(user=request.user) \
                                     .order_by('-created_at')
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
    expense_qs = Transaction.objects.filter(
        user=request.user,
        transaction_type='EXPENSE'
    ).values('category__name') \
     .annotate(total=Sum('amount')) \
     .order_by('-total')

    expense_data = [
        {
            'category': item['category__name'] or 'Uncategorized',
            'total': float(item['total'] or 0)
        }
        for item in expense_qs
    ]

    context = {
        'expense_data_json': json.dumps(expense_data),
        'has_data': len(expense_data) > 0
    }
    return render(request, 'analytics.html', context)


@login_required
def add_transaction_view(request):
    if request.method == "POST":
        amount_str = request.POST.get("amount")
        transaction_type = request.POST.get("transaction_type")
        category_id = request.POST.get("category")
        description = request.POST.get("description", "")

        try:
            amount = float(amount_str)
            if amount <= 0:
                messages.error(request, "Amount must be greater than zero.")
                raise ValueError("Invalid amount")

            # Get user's wallet
            wallet = Wallet.objects.get(user=request.user)

            # Get category (must belong to user)
            category = Category.objects.get(id=category_id, user=request.user)

            # Create transaction - linked to USER, not wallet
            Transaction.objects.create(
                user=request.user,
                amount=amount,
                transaction_type=transaction_type,
                category=category,
                description=description
            )

            # Manually update wallet balance
            if transaction_type == "INCOME":
                wallet.balance += Decimal(str(amount))
            elif transaction_type == "EXPENSE":
                wallet.balance -= Decimal(str(amount))
            wallet.save()

            messages.success(request, "Transaction added successfully!")
            return redirect("transactions")

        except ValueError:
            pass  # Message already shown
        except Category.DoesNotExist:
            messages.error(request, "Invalid category selected.")
        except Exception as e:
            messages.error(request, "Error adding transaction. Please try again.")

    # GET request - show form
    categories = Category.objects.filter(user=request.user)
    context = {
        "categories": categories,
        "has_categories": categories.exists()
    }
    return render(request, "add_transaction.html", context)