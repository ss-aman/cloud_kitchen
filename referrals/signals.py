from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User
from .models import ReferralUse, Referral
from wallet.models import CoinWallet
from django.conf import settings
from .tasks import process_referral_activation
from django.utils import timezone

@receiver(post_save, sender=User)
def create_referral_use(sender, instance, created, **kwargs):
    pass

@receiver(post_save, sender=User)
def activate_signup_bonus(sender, instance, created, **kwargs):
    """
    Trigger check when user verifies their account.
    """
    if not created and instance.is_verified:
        # Check if this update was actually a verification change to avoid redundant calls
        # (Though checking in task is safe too)
        process_referral_activation.delay(instance.id)

from orders.models import Order

@receiver(post_save, sender=Order)
def check_referral_activation(sender, instance, created, **kwargs):
    if instance.status == 'completed': 
        process_referral_activation.delay(instance.user.id)
