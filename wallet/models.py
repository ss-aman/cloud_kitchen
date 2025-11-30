from django.db import models
from accounts.models import User
from django.utils import timezone
from django.db.models import Sum

class CoinWallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    # Deprecated fields, keeping for backward compatibility if needed, but logic moves to credits
    # balance = models.IntegerField(default=0) 
    # inactive_balance = models.IntegerField(default=0)
    transactions = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'coin_wallets'

    @property
    def balance(self):
        """Calculate active balance from unexpired, active credits"""
        return self.credits.filter(
            is_active=True,
            expires_at__gt=timezone.now()
        ).aggregate(total=Sum('amount'))['total'] or 0

    @property
    def inactive_balance(self):
        """Calculate inactive balance (e.g. pending verification)"""
        return self.credits.filter(
            is_active=False
        ).aggregate(total=Sum('amount'))['total'] or 0

    def add_credit(self, amount, source, description='', expires_in_days=30, is_active=True):
        """Helper to add a new credit"""
        expires_at = timezone.now() + timezone.timedelta(days=expires_in_days)
        return self.credits.create(
            amount=amount,
            source=source,
            description=description,
            is_active=is_active,
            expires_at=expires_at,
            activated_at=timezone.now() if is_active else None
        )

class WalletCredit(models.Model):
    SOURCE_CHOICES = [
        ('REFERRAL_SIGNUP', 'Referral Signup Bonus'),
        ('REFERRAL_REWARD', 'Referrer Reward'),
        ('ORDER_REWARD', 'Order Reward'),
        ('MANUAL', 'Manual Adjustment'),
    ]

    wallet = models.ForeignKey(CoinWallet, on_delete=models.CASCADE, related_name='credits')
    amount = models.IntegerField()
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    description = models.CharField(max_length=255, blank=True)
    
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField()
    activated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'wallet_credits'
        ordering = ['expires_at']

    def __str__(self):
        return f"{self.amount} - {self.source} ({self.wallet.user.username})"
