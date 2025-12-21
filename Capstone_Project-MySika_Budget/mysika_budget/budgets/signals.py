
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
from .models import Budget
from decimal import Decimal

# Try to import the transaction model; adapt path if your transactions app name differs.
try:
    from transactions.models import Transaction
except Exception:
    Transaction = None

def compute_budget_total(user, category, start_date, end_date):
    """
    Sum all expense transactions matching the user, category and date range.
    This expects Transaction model to have: user (FK), category (string), amount (positive decimal), created_at/date.
    """
    if Transaction is None:
        return Decimal("0.00")

    qs = Transaction.objects.filter(user=user, category__iexact=category, created_at__date__gte=start_date, created_at__date__lte=end_date)
    agg = qs.aggregate(total=Sum('amount'))
    total = agg.get('total') or Decimal("0.00")
    return total

@receiver(post_save, sender=Budget)
def on_budget_save(sender, instance, created, **kwargs):
    # Ensure budget has correct total_spent after being created/updated
    if Transaction is None:
        return
    total = compute_budget_total(instance.user, instance.category, instance.start_date, instance.end_date)
    # use update to avoid recursion issues with save()
    Budget.objects.filter(pk=instance.pk).update(total_spent=total, status=instance.calculate_status())

if Transaction:
    @receiver(post_save, sender=Transaction)
    def on_transaction_save(sender, instance, created, **kwargs):
        # when a transaction is created or updated, update any budgets that match category and date range
        user = instance.user
        category = instance.category
        # find budgets for this user/category where transaction date falls within the budget range
        tx_date = instance.created_at.date() if hasattr(instance, "created_at") else (instance.date if hasattr(instance, "date") else timezone.now().date())
        budgets = Budget.objects.filter(user=user, category__iexact=category, start_date__lte=tx_date, end_date__gte=tx_date)
        for b in budgets:
            new_total = compute_budget_total(b.user, b.category, b.start_date, b.end_date)
            Budget.objects.filter(pk=b.pk).update(total_spent=new_total, status=b.calculate_status())

    @receiver(post_delete, sender=Transaction)
    def on_transaction_delete(sender, instance, **kwargs):
        # when a transaction is deleted, update budgets similarly
        user = instance.user
        category = instance.category
        tx_date = instance.created_at.date() if hasattr(instance, "created_at") else (instance.date if hasattr(instance, "date") else timezone.now().date())
        budgets = Budget.objects.filter(user=user, category__iexact=category, start_date__lte=tx_date, end_date__gte=tx_date)
        for b in budgets:
            new_total = compute_budget_total(b.user, b.category, b.start_date, b.end_date)
            Budget.objects.filter(pk=b.pk).update(total_spent=new_total, status=b.calculate_status())
