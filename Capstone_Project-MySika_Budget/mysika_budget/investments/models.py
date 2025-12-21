from django.db import models
from django.conf import settings
from decimal import Decimal


# Create your models here.
class Stock(models.Model):
    MARKET_CHOICES = [
        ("GSE", "Ghana Stock Exchange"),
        ("US", "United States"),
    ]

    symbol = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    market = models.CharField(max_length=10, choices=MARKET_CHOICES)

    def __str__(self):
        return f"{self.symbol} ({self.market})"

    class Meta:
        unique_together = ("symbol", "market")

class Investment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="investments"
    )

    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name="investments"
    )

    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=4
    )

    average_buy_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "stock")

    def cost_basis(self):
        return self.quantity * self.average_buy_price
    

class PriceSnapshot(models.Model):
    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name="prices"
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    captured_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-captured_at"]