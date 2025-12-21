from django.contrib import admin
from .models import Category

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category_type", "user")
    list_filter = ("category_type",)
    search_fields = ("name", "user__email")