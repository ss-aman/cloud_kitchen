from django.db import models
from django.contrib.postgres.fields import JSONField  # Use appropriate JSON field based on your version of Django

class CoinWallet(models.Model):
    """
    A model representing a Coin Wallet for Cloud Kitchen.
    """
    user_id = models.IntegerField()  # Assuming there is a user associated
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    metadata = JSONField(default=dict)  # JSON field for additional data

    def add_coins(self, amount):
        """Add coins to the wallet."""
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        self.balance += amount
        self.save()

    def deduct_coins(self, amount):
        """Deduct coins from the wallet."""
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        if amount > self.balance:
            raise ValueError("Insufficient balance.")
        self.balance -= amount
        self.save()