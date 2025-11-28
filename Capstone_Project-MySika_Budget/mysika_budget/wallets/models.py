from django.db import models
from django.contrib.auth.models import User  #importing the User Model to be used 


# Create your models here.
class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default= 0.00)
    currency = models.CharField(max_length=10, default= "GHS")
    created_at = models.DateTimeField(auto_created=True)

    def __str__(self):
        return f"{self.user.name}'s Wallet"
    
#transaction Model
class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ("DEPOSIT", "deposit"),
        ("WITHDRAW", "withdraw"),
         ("TRANSFER_IN", "Transfer In"),
        ("TRANSFER_OUT", "Transfer Out"),
    )

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions") # Wallet serve as the primary key
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"
    
