from rest_framework import serializers
from .models import Transaction
from wallets.models import Wallet
from categories.models import Category
from django.db import transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id",
            "transaction_type",
            "amount",
            "category",
            "description",
            "created_at",
        ]
        read_only_fields = ("id", "created_at")

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate(self, data):
        user = self.context["request"].user
        category = data["category"]
        transaction_type = data["transaction_type"]

        if category.user != user:
            raise serializers.ValidationError("Invalid category.")

        if category.category_type != transaction_type:
            raise serializers.ValidationError(
                f"Category type must be {transaction_type}."
            )

        return data

    def create(self, validated_data):
        user = self.context["request"].user
        wallet = Wallet.objects.select_for_update().get(user=user)

        with transaction.atomic():
            tx = Transaction.objects.create(
                user=user,
                wallet=wallet,
                **validated_data
            )
            tx.apply_to_wallet()

        return tx