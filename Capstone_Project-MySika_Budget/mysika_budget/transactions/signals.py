from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from decimal import Decimal

from .models import Transaction
from budgets.models import Budget


def recalculate_budgets(user, category, date):
    budgets = Budget.objects.filter(
        user=user,
        category=category,
        start_date__lte=date,
        end_date__gte=date
    )

    for budget in budgets:
        total = Transaction.objects.filter(
            user=user,
            category=category,
            transaction_type="EXPENSE",
            created_at__date__gte=budget.start_date,
            created_at__date__lte=budget.end_date
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        budget.total_spent = total
        budget.save()


@receiver(post_save, sender=Transaction)
def update_budget_on_create(sender, instance, created, **kwargs):
    if instance.transaction_type == "EXPENSE":
        recalculate_budgets(
            instance.user,
            instance.category,
            instance.created_at.date()
        )


@receiver(post_delete, sender=Transaction)
def update_budget_on_delete(sender, instance, **kwargs):
    if instance.transaction_type == "EXPENSE":
        recalculate_budgets(
            instance.user,
            instance.category,
            instance.created_at.date()
        )
