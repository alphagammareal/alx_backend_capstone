from rest_framework import serializers
from .models import Stock, Investment

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ["id", "symbol", "name", "market"]


class InvestmentSerializer(serializers.ModelSerializer):
    stock = StockSerializer(read_only=True)
    cost_basis = serializers.SerializerMethodField()
    current_price = serializers.SerializerMethodField()
    current_value = serializers.SerializerMethodField()
    profit_loss = serializers.SerializerMethodField()

    class Meta:
        model = Investment
        fields = [
            "id",
            "stock",
            "quantity",
            "average_buy_price",
            "cost_basis",
            "current_price",
            "current_value",
            "profit_loss",
        ]

    def get_cost_basis(self, obj):
        return obj.cost_basis()

    def get_current_price(self, obj):
        latest = obj.stock.prices.first()
        return latest.price if latest else None

    def get_current_value(self, obj):
        price = self.get_current_price(obj)
        return price * obj.quantity if price else None

    def get_profit_loss(self, obj):
        current = self.get_current_value(obj)
        return current - obj.cost_basis() if current else None
