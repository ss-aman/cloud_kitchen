from django.db import models

class ExpenseType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'expense_types'
    
    def __str__(self):
        return self.name

class Expense(models.Model):
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'expenses'
        ordering = ['-date']
