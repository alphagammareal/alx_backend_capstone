from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from categories.models import Category

User = get_user_model()

# Create your models here.
class Budget(models.Model):
    PERIOD_CHOICES = [
        ("monthly", "Monthly"),
        ("weekly", "Weekly"),
        ("yearly", "Yearly"),
        ("custom", "Custom"),
    ]

    STATUS_CHOICES = [
        ("not_started", "Not Started"),
        ("active", "Active"),
        ("exceeded", "Exceeded"),
        ("completed", "Completed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "budgets")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    amount_limit = models.DecimalField(max_digits=12, decimal_places=2)
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default="monthly")
    
    start_date = models.DateField()
    end_date = models.DateField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="not_started")
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_status(self):
        """Automatically update budget status."""
        today = timezone.now().date()

        if today < self.start_date:
            return "not_started"

        if today > self.end_date:
            # If time is over, check if they overspent or stayed within limit.
            if self.total_spent > self.amount_limit:
                return "exceeded"
            return "completed"
        
        # Active budget
        if self.total_spent > self.amount_limit:
            return "exceeded"

        return "active"
    def save(self, *args, **kwargs):
        # Auto-update status before saving
        self.status = self.calculate_status()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category} ({self.status})"


