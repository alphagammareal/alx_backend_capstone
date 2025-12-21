from rest_framework import serializers


class IncomeExpenseSerializer(serializers.Serializer):
    income = serializers.DecimalField(max_digits=12, decimal_places=2)
    expense = serializers.DecimalField(max_digits=12, decimal_places=2)
    net = serializers.DecimalField(max_digits=12, decimal_places=2)


class CategoryBreakdownSerializer(serializers.Serializer):
    category__name = serializers.CharField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2)


class CashflowSerializer(serializers.Serializer):
    created_at__date = serializers.DateField()
    transaction_type = serializers.CharField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2)
