from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Global default categories
class DefaultCategory(models.Model):
    CATEGORY_TYPE_CHOICES = [
        ("INCOME", "Income"),
        ("EXPENSE", "Expense"),
    ]

    name = models.CharField(max_length=100, unique=True)
    category_type = models.CharField(
        max_length=10,
        choices=CATEGORY_TYPE_CHOICES
    )

    def __str__(self):
        return f"{self.name} ({self.category_type})"

    class Meta:
        unique_together = ("name", "category_type")
        ordering = ["name"]


# User-specific categories (custom ones)
class Category(models.Model):
    CATEGORY_TYPE_CHOICES = [
        ("INCOME", "Income"),
        ("EXPENSE", "Expense"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="categories"
    )
    name = models.CharField(max_length=100)
    category_type = models.CharField(
        max_length=10,
        choices=CATEGORY_TYPE_CHOICES
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "name", "category_type")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.category_type})"