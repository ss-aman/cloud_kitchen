from django.contrib import admin
from .models import Expense, ExpenseType

admin.site.register(Expense)
admin.site.register(ExpenseType)