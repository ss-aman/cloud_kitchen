from celery import shared_task
from django.utils import timezone
from wallet.models import WalletCredit
from .models import ReferralUse
from django.db.models import Count
from django.contrib.auth import get_user_model

@shared_task
def check_expired_credits():
    """
    Periodic task to mark credits as expired.
    Should be scheduled to run daily.
    """
    now = timezone.now()
    # Find active credits that have passed their expiry date
    expired_credits = WalletCredit.objects.filter(
        is_active=True,
        expires_at__lt=now
    )
    
    count = expired_credits.count()
    if count > 0:
        # Credits are effectively expired by the balance property filter,
        # but we can log or perform other cleanup here if needed.
        pass
    
    return f"Checked for expired credits. Found {count}."

@shared_task
def process_referral_activation(user_id):
    """
    Check if referral bonuses should be activated.
    Triggered when:
    1. User verifies their account.
    2. User completes an order.
    
    Condition for activation (BOTH Referrer and Referee):
    - Referee is verified AND
    - Referee has completed 2 orders.
    """
    try:
        User = get_user_model()
        user = User.objects.get(id=user_id)
        
        # Find who referred this user
        referral_use = ReferralUse.objects.get(referred_user=user)
        
        # Check conditions
        is_verified = user.is_verified
        
        from orders.models import Order
        completed_orders_count = Order.objects.filter(
            user=user, 
            status='completed'
        ).count()
        
        conditions_met = is_verified and completed_orders_count >= 2
        
        results = []
        
        if conditions_met:
            now = timezone.now()
            
            # 1. Activate Referrer Bonus
            if referral_use.referrer_credit and not referral_use.referrer_bonus_granted:
                referral_use.referrer_credit.is_active = True
                referral_use.referrer_credit.activated_at = now
                referral_use.referrer_credit.save()
                
                referral_use.referrer_bonus_granted = True
                results.append(f"Activated referrer bonus for {referral_use.referral.referrer.username}")
            
            # 2. Activate Referee Bonus
            if referral_use.referee_credit and not referral_use.referee_bonus_granted:
                referral_use.referee_credit.is_active = True
                referral_use.referee_credit.activated_at = now
                referral_use.referee_credit.save()
                
                referral_use.referee_bonus_granted = True
                results.append(f"Activated referee bonus for {user.username}")
                
            referral_use.save()
            
            if not results:
                return "Conditions met, but bonuses already granted."
            return ", ".join(results)
        else:
            return f"Conditions not met. Verified: {is_verified}, Orders: {completed_orders_count}/2"
            
    except ReferralUse.DoesNotExist:
        return "No referral use found"
    except User.DoesNotExist:
        return "User not found"
    except Exception as e:
        return f"Error: {str(e)}"
