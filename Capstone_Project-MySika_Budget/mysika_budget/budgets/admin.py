from django.contrib import admin
from .models import Budget

# Register your models here.
@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'category', 'amount_limit', 'total_spent', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'period', 'start_date')
    search_fields = ('user__email', 'category')
