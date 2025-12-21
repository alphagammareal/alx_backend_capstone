from django.db.models import Sum
from django.utils.timezone import now
from datetime import timedelta

from transactions.models import Transaction


class AnalyticsService:

    @staticmethod
    def income_vs_expense(user, start_date=None, end_date=None):
        qs = Transaction.objects.filter(user=user)

        if start_date:
            qs = qs.filter(created_at__date__gte=start_date)
        if end_date:
            qs = qs.filter(created_at__date__lte=end_date)

        income = qs.filter(transaction_type="INCOME").aggregate(
            total=Sum("amount")
        )["total"] or 0

        expense = qs.filter(transaction_type="EXPENSE").aggregate(
            total=Sum("amount")
        )["total"] or 0

        return {
            "income": income,
            "expense": expense,
            "net": income - expense,
        }

    @staticmethod
    def category_breakdown(user):
        qs = (
            Transaction.objects
            .filter(user=user, transaction_type="EXPENSE")
            .values("category__name")
            .annotate(total=Sum("amount"))
            .order_by("-total")
        )

        return qs

    @staticmethod
    def last_30_days_cashflow(user):
        start_date = now().date() - timedelta(days=30)

        qs = (
            Transaction.objects
            .filter(user=user, created_at__date__gte=start_date)
            .values("created_at__date", "transaction_type")
            .annotate(total=Sum("amount"))
            .order_by("created_at__date")
        )

        return qs
