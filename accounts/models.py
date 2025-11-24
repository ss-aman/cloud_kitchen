from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    VERIFICATION_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Phone'),
    ]
    
    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True)
    is_verified = models.BooleanField(default=False)
    verification_method = models.CharField(max_length=10, choices=VERIFICATION_CHOICES, default='email')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.username
