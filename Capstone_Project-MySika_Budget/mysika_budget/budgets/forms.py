from django import forms
from .models import Budget
from categories.models import Category
from django.db.models import Q
from transactions.models import Transaction

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'amount_limit', 'start_date', 'end_date']
        widgets = {
            'amount_limit': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00',
                'class': 'form-control'
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }
        labels = {
            'amount_limit': 'Budget Limit (GHS)',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(
                Q(user=user) | Q(user__isnull=True)
            ).order_by('name')