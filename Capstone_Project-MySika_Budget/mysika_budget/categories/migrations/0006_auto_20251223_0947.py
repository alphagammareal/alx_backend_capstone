
from django.db import migrations

def create_default_categories(apps, schema_editor):
    Category = apps.get_model('categories', 'Category')
    
    default_categories = [
        # Expenses
        ("Food & Dining", "EXPENSE"),
        ("Groceries", "EXPENSE"),
        ("Transport", "EXPENSE"),
        ("Fuel", "EXPENSE"),
        ("Entertainment", "EXPENSE"),
        ("Shopping", "EXPENSE"),
        ("Utilities", "EXPENSE"),
        ("Rent/Mortgage", "EXPENSE"),
        ("Healthcare", "EXPENSE"),
        ("Education", "EXPENSE"),
        ("Subscriptions", "EXPENSE"),
        ("Personal Care", "EXPENSE"),
        ("Miscellaneous", "EXPENSE"),
        
        # Income
        ("Salary", "INCOME"),
        ("Business Income", "INCOME"),
        ("Freelance", "INCOME"),
        ("Investments", "INCOME"),
        ("Side Hustle", "INCOME"),
        ("Other Income", "INCOME"),
    ]
    
    for name, cat_type in default_categories:
        Category.objects.get_or_create(
            name=name,
            category_type=cat_type,
            defaults={'user': None} 
        )

class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0005_alter_category_user_alter_defaultcategory_name'), 
    ]

    operations = [
        migrations.RunPython(create_default_categories),
    ]
