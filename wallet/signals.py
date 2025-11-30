from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User
from .models import CoinWallet

@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        CoinWallet.objects.create(user=instance)
