from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from decimal import Decimal
from datetime import datetime
import json

from wallets.models import Wallet
from transactions.models import Transaction
from categories.models import Category, DefaultCategory
from budgets.models import Budget
from investments.models import Investment, Stock
from investments.services import MarketDataService


@login_required
def dashboard(request):
    user = request.user

    # Wallet summary
    wallet, created = Wallet.objects.get_or_create(user=user)
    total_balance = float(wallet.balance)

    # Transactions
    transactions = Transaction.objects.filter(user=user)

    total_income = transactions.filter(transaction_type='INCOME') \
                              .aggregate(total=Sum('amount'))['total'] or 0
    total_expense = transactions.filter(transaction_type='EXPENSE') \
                               .aggregate(total=Sum('amount'))['total'] or 0
    net_balance = total_income - total_expense

    # Expense by category for chart
    expense_by_category = transactions.filter(transaction_type='EXPENSE') \
                                     .values('category__name') \
                                     .annotate(total=Sum('amount')) \
                                     .order_by('-total')

    category_labels = [item['category__name'] or 'Uncategorized' for item in expense_by_category]
    category_values = [float(item['total'] or 0) for item in expense_by_category]

    # Investments - now with live prices
    investments = Investment.objects.filter(user=user)
    total_portfolio_value = Decimal('0')
    for inv in investments:
        MarketDataService.update_stock_price(inv.stock)  # Refresh price
        latest_price = inv.stock.prices.first().price if inv.stock.prices.exists() else Decimal('0')
        total_portfolio_value += latest_price * inv.quantity

    context = {
        'total_balance': total_balance,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_balance': net_balance,
        'category_labels': category_labels,
        'category_values': category_values,
        'total_portfolio_value': float(total_portfolio_value),
        'year': datetime.now().year,
    }

    return render(request, 'dashboard.html', context)


@login_required
def wallets_view(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    return render(request, 'wallets.html', {'wallet': wallet})


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

    # Update prices for all investments
    for inv in investments:
        MarketDataService.update_stock_price(inv.stock)

    # Prepare detailed data
    investment_data = []
    for inv in investments:
        current_price = inv.stock.prices.first().price if inv.stock.prices.exists() else None
        data = {
            'stock': inv.stock,
            'quantity': inv.quantity,
            'average_buy_price': inv.average_buy_price,
            'cost_basis': inv.quantity * inv.average_buy_price,
            'current_price': current_price,
            'current_value': current_price * inv.quantity if current_price else None,
            'profit_loss': (current_price * inv.quantity - inv.quantity * inv.average_buy_price) if current_price else None,
        }
        investment_data.append(data)

    return render(request, 'investments.html', {'investment_data': investment_data})


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
        category_input = request.POST.get("category")  # now handles default/user
        description = request.POST.get("description", "")

        try:
            amount = float(amount_str)
            if amount <= 0:
                messages.error(request, "Amount must be greater than zero.")
                raise ValueError()

            wallet = Wallet.objects.get(user=request.user)

            # Handle category selection
            if category_input.startswith("default_"):
                cat_id = category_input.split("_")[1]
                default_cat = DefaultCategory.objects.get(id=cat_id)
                # Copy to user categories
                category, created = Category.objects.get_or_create(
                    user=request.user,
                    name=default_cat.name,
                    category_type=default_cat.category_type
                )
            elif category_input.startswith("user_"):
                cat_id = category_input.split("_")[1]
                category = Category.objects.get(id=cat_id, user=request.user)
            else:
                messages.error(request, "Invalid category.")
                raise ValueError()

            Transaction.objects.create(
                user=request.user,
                amount=amount,
                transaction_type=transaction_type,
                category=category,
                description=description
            )

            # Update balance
            if transaction_type == "INCOME":
                wallet.balance += Decimal(str(amount))
            elif transaction_type == "EXPENSE":
                wallet.balance -= Decimal(str(amount))
            wallet.save()

            messages.success(request, "Transaction added successfully!")
            return redirect("transactions")

        except ValueError:
            pass
        except (DefaultCategory.DoesNotExist, Category.DoesNotExist):
            messages.error(request, "Invalid category selected.")
        except Exception:
            messages.error(request, "Error adding transaction.")

    # GET - show form with default + user categories
    default_categories = DefaultCategory.objects.all()
    user_categories = Category.objects.filter(user=request.user)
    all_categories = list(default_categories) + list(user_categories)
    all_categories.sort(key=lambda c: c.name.lower())

    context = {
        "categories": all_categories,
        "has_categories": len(all_categories) > 0
    }
    return render(request, "add_transaction.html", context)


@login_required
def add_investment_view(request):
    if request.method == "POST":
        symbol = request.POST.get("symbol", "").strip().upper()
        market = request.POST.get("market")
        quantity_str = request.POST.get("quantity")
        buy_price_str = request.POST.get("buy_price")

        try:
            quantity = Decimal(quantity_str)
            buy_price = Decimal(buy_price_str)

            if not symbol or not market or quantity <= 0 or buy_price <= 0:
                messages.error(request, "All fields are required and must be positive.")
            else:
                stock, _ = Stock.objects.get_or_create(
                    symbol=symbol,
                    market=market,
                    defaults={'name': symbol}
                )

                Investment.objects.create(
                    user=request.user,
                    stock=stock,
                    quantity=quantity,
                    average_buy_price=buy_price
                )

                messages.success(request, "Investment added successfully!")
                return redirect("investments")
        except (ValueError, Decimal.InvalidOperation):
            messages.error(request, "Invalid number format.")

    return render(request, "add_investment.html")