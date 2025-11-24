from django.db import models
from accounts.models import User
import jwt
from datetime import datetime, timedelta

class Referral(models.Model):
    REFERRAL_TYPES = [
        ('signup', 'Signup Referral'),
        ('order', 'Order Share'),
    ]
    
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals')
    token = models.CharField(max_length=500, unique=True)
    referral_type = models.CharField(max_length=10, choices=REFERRAL_TYPES)
    reason = models.CharField(max_length=200)
    user_limit = models.IntegerField(default=0)
    uses_count = models.IntegerField(default=0)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'referrals'
