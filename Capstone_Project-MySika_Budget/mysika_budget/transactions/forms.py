from django import forms
from .models import Transaction
from categories.models import Category
from django.db import models

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'amount', 'category', 'description']
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01', 'placeholder': '0.00'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'e.g. Monthly salary'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Show only user's categories + default ones if you have them
            self.fields['category'].queryset = Category.objects.filter(
                models.Q(user=user) | models.Q(user__isnull=True)  # default categories
            )