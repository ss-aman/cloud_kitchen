from django.db import models
from django.conf import settings

class SocialConnection(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='social_connections')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'social_connections'
        verbose_name = 'Social Connection'
        verbose_name_plural = 'Social Connections'

    def __str__(self):
        return f"Social Connection - {self.user}"

class ReferralToken(models.Model):
    REFERRAL_TYPES = [
        ('signup', 'User Signup Referral'),
        ('order_share', 'User Order Share')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='referral_tokens')
    token = models.CharField(max_length=255, unique=True)
    referral_type = models.CharField(max_length=20, choices=REFERRAL_TYPES)
    reason = models.CharField(max_length=255)
    user_limit = models.IntegerField(default=0, help_text="0 means unlimited")
    usage_count = models.IntegerField(default=0)
    expire_datetime = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'referral_tokens'
        verbose_name = 'Referral Token'
        verbose_name_plural = 'Referral Tokens'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.referral_type} - {self.token[:10]}..."

    def is_valid(self):
        from django.utils import timezone
        if not self.is_active:
            return False
        if self.expire_datetime < timezone.now():
            return False
        if self.user_limit > 0 and self.usage_count >= self.user_limit:
            return False
        return True

    def increment_usage(self):
        self.usage_count += 1
        if self.user_limit > 0 and self.usage_count >= self.user_limit:
            self.is_active = False
        self.save()

class ReferralUsage(models.Model):
    referral_token = models.ForeignKey(ReferralToken, on_delete=models.CASCADE, related_name='usages')
    referred_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='referral_usages')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'referral_usages'
        verbose_name = 'Referral Usage'
        verbose_name_plural = 'Referral Usages'
        unique_together = [['referral_token', 'referred_user']]

    def __str__(self):
        return f"{self.referred_user} used {self.referral_token.user}'s referral"