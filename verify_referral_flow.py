import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloud_kitchen.settings')
django.setup()

from django.contrib.auth import get_user_model
from referrals.models import Referral, ReferralUse
from wallet.models import CoinWallet, WalletCredit
from orders.models import Order
from django.utils import timezone
from referrals.tasks import process_referral_activation, check_expired_credits

User = get_user_model()

def run_verification():
    print("Starting Referral Flow Verification...")
    
    # 1. Cleanup
    print("\n1. Cleaning up old data...")
    User.objects.filter(username__in=['referrer_user', 'referee_user']).delete()
    
    # 2. Create Referrer
    print("\n2. Creating Referrer...")
    referrer = User.objects.create_user(username='referrer_user', email='referrer@example.com', password='password123')
    # Wallet created by signal
    
    # 3. Generate Referral Code
    print("\n3. Generating Referral Code...")
    referral = Referral.objects.create(
        referrer=referrer,
        description="Test Referral",
        referrer_reward_amount=50,
        referee_reward_amount=100,
        reward_expiry_days=30
    )
    print(f"Referral Code: {referral.code}")
    
    # 4. Create Referee (Signup with code)
    print("\n4. Creating Referee (Signup with code)...")
    # Simulate signup logic
    referee = User.objects.create_user(username='referee_user', email='referee@example.com', password='password123')
    # Wallet created by signal
    
    ReferralUse.objects.create(
        referral=referral,
        referred_user=referee
    )
    referral.uses_count += 1
    referral.save()
    
    # Add credits (simulating view logic)
    referee_credit = referee.wallet.add_credit(
        amount=referral.referee_reward_amount,
        source='REFERRAL_SIGNUP',
        description=f'Signup bonus via {referral.referrer.username}',
        expires_in_days=referral.reward_expiry_days,
        is_active=False
    )
    
    referrer_credit = referrer.wallet.add_credit(
        amount=referral.referrer_reward_amount,
        source='REFERRAL_REWARD',
        description=f'Referral bonus for {referee.username}',
        expires_in_days=referral.reward_expiry_days,
        is_active=False
    )
    
    # Link credits to usage
    usage = ReferralUse.objects.get(referred_user=referee)
    usage.referee_credit = referee_credit
    usage.referrer_credit = referrer_credit
    usage.save()
    
    print("Credits created (Inactive):")
    print(f"Referee Wallet Balance: {referee.wallet.balance} (Active), {referee.wallet.inactive_balance} (Inactive)")
    print(f"Referrer Wallet Balance: {referrer.wallet.balance} (Active), {referrer.wallet.inactive_balance} (Inactive)")
    
    assert referee.wallet.balance == 0
    assert referee.wallet.inactive_balance == 100
    assert referrer.wallet.inactive_balance == 50
    
    # 5. Activate Referee Bonus (Verification)
    print("\n5. Activating Referee Bonus (Verification)...")
    referee.is_verified = True
    referee.save()
    
    # Trigger signal logic manually (or via task)
    # Note: With new logic, verification alone does NOT activate bonus.
    # It triggers the task, which checks for 2 orders.
    # So we expect NO change in active balance yet.
    
    process_referral_activation(referee.id)
    
    print(f"Referee Wallet Balance: {referee.wallet.balance} (Active)")
    assert referee.wallet.balance == 0 # Should still be 0
    
    # 6. Activate Referrer & Referee Bonus (Order Completion)
    print("\n6. Activating Referrer & Referee Bonus (Order Completion)...")
    # Create 2 orders
    Order.objects.create(user=referee, status='completed', total_amount=100)
    Order.objects.create(user=referee, status='completed', total_amount=100)
    
    # Run task
    result = process_referral_activation(referee.id)
    print(f"Task Result: {result}")
    
    # Refresh from db
    referrer_credit.refresh_from_db()
    referee_credit.refresh_from_db()
    
    print(f"Referrer Credit Active: {referrer_credit.is_active}")
    print(f"Referee Credit Active: {referee_credit.is_active}")
    
    print(f"Referrer Wallet Balance: {referrer.wallet.balance} (Active)")
    print(f"Referee Wallet Balance: {referee.wallet.balance} (Active)")
    
    assert referrer.wallet.balance == 50
    assert referee.wallet.balance == 100
    
    # 7. Test Expiration
    print("\n7. Testing Expiration...")
    # Manually expire the credit
    referrer_credit.expires_at = timezone.now() - timezone.timedelta(days=1)
    referrer_credit.save()
    
    # Check balance before task (should be 0 because property filters by expiry)
    print(f"Referrer Wallet Balance (After manual expire, before task): {referrer.wallet.balance}")
    assert referrer.wallet.balance == 0
    
    # Run expiration task
    check_expired_credits()
    
    print("\nVerification Successful!")

if __name__ == '__main__':
    run_verification()
