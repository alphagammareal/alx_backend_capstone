from rest_framework import serializers
from .models import Budget

class BudgetSerializer(serializers.ModelSerializer):
    """
    This is a Django REST Framework (DRF) serializer for the Budget model.
    It automatically converts Budget model instances to/from JSON (and other formats)
    and handles validation when creating/updating objects via the API.
    """
    progress_percent = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Budget
        fields = [
            "id", "user", "category", "amount_limit",
            "period", "start_date", "end_date",
            "status", "total_spent", "progress_percent",
            "created_at", "updated_at"
        ]
        read_only_fields = ("user", "status", "total_spent", "progress_percent", "created_at", "updated_at")
        # This method is REQUIRED when using SerializerMethodField

    def get_progress_percent(self, obj):
        try:
            if obj.amount_limit and obj.amount_limit > 0:
                return float((obj.total_spent / obj.amount_limit) * 100)
        except Exception:
            pass
        return 0.0

    def validate(self, data):
        start = data.get("start_date") or getattr(self.instance, "start_date", None)
        end = data.get("end_date") or getattr(self.instance, "end_date", None)
        if start and end and start > end:
            raise serializers.ValidationError("start_date must be before end_date.")
        return data
