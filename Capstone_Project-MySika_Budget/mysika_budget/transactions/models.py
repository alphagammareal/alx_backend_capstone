from django.db import models, transaction as db_transaction
from django.contrib.auth import get_user_model
from decimal import Decimal

from wallets.models import Wallet
from categories.models import Category

User = get_user_model()

# Create your models here.
class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ("INCOME", "Income"),
        ("EXPENSE", "Expense"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="transactions"
    )
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name= "wallet_transactions")


    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="transactions"
    )

    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPE_CHOICES
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    description = models.CharField(
        max_length=255,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"

    def apply_to_wallet(self):
        """
        Apply transaction effect to wallet balance safely.
        """
        if self.transaction_type == "INCOME":
            self.wallet.balance += self.amount
        elif self.transaction_type == "EXPENSE":
            if self.wallet.balance < self.amount:
                raise ValueError("Insufficient wallet balance")
            self.wallet.balance -= self.amount

        self.wallet.save(update_fields=["balance"])
    
    def save(self, *args, **kwargs):
        """
        Override save to apply wallet changes AFTER the transaction is saved.
        """
        super().save(*args, **kwargs)  # Save transaction first
        self.apply_to_wallet()        # Then update wallet balance