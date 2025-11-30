from django.db import models
from accounts.models import User
import secrets
import string
from django.utils import timezone
from wallet.models import WalletCredit

class Referral(models.Model):
    REFERRAL_TYPES = [
        ('signup', 'Signup Referral'),
        ('order', 'Order Share'),
    ]
    
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals')
    code = models.CharField(max_length=12, unique=True, editable=False)
    referral_type = models.CharField(max_length=10, choices=REFERRAL_TYPES, default='signup')
    description = models.CharField(max_length=200, blank=True)
    
    # Reward Configuration
    referrer_reward_amount = models.IntegerField(default=50)
    referee_reward_amount = models.IntegerField(default=100)
    reward_expiry_days = models.IntegerField(default=30)

    max_uses = models.IntegerField(default=0, help_text="0 means unlimited")
    uses_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'referrals'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.code:
            while True:
                new_code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(12))
                if not Referral.objects.filter(code=new_code).exists():
                    self.code = new_code
                    break
        super().save(*args, **kwargs)
    
    def is_valid(self):
        if not self.is_active:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        if self.max_uses > 0 and self.uses_count >= self.max_uses:
            return False
        return True
    
    def __str__(self):
        return f"{self.code} - {self.referrer.username}"

class ReferralUse(models.Model):
    """Track who used which referral code"""
    referral = models.ForeignKey(Referral, on_delete=models.CASCADE, related_name='uses')
    referred_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='used_referrals')
    
    # Link to the actual credits given
    referrer_credit = models.OneToOneField(
        WalletCredit, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='referral_use_as_referrer'
    )
    referee_credit = models.OneToOneField(
        WalletCredit, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='referral_use_as_referee'
    )

    referrer_bonus_granted = models.BooleanField(default=False)
    referee_bonus_granted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'referral_uses'
        unique_together = ['referral', 'referred_user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.referred_user.username} used {self.referral.code}"
