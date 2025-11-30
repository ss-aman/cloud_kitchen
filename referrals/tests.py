from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from referrals.models import Referral, ReferralUse
from wallet.models import CoinWallet
from orders.models import Order
from django.conf import settings
from decimal import Decimal

User = get_user_model()

class ReferralSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.referrer = User.objects.create_user(username='referrer', password='password')
        self.referee_data = {
            'username': 'referee',
            'email': 'referee@example.com',
            'password': 'password',
            'password_confirm': 'password'
        }
        
        # Create referral code
        self.referral = Referral.objects.create(referrer=self.referrer)
        self.referral_code = self.referral.code

    def test_signup_with_referral(self):
        # Signup with referral code
        response = self.client.post('/signup/', {
            **self.referee_data,
            'referral_code': self.referral_code
        })
        
        self.assertEqual(response.status_code, 302) # Redirects on success
        
        referee = User.objects.get(username='referee')
        
        # Check ReferralUse created
        self.assertTrue(ReferralUse.objects.filter(referral=self.referral, referred_user=referee).exists())
        
        # Check Inactive Bonuses
        self.referrer.refresh_from_db()
        referee.refresh_from_db()
        
        self.assertEqual(referee.wallet.inactive_balance, settings.REFERRAL_SIGNUP_BONUS)
        self.assertEqual(self.referrer.wallet.inactive_balance, settings.REFERRAL_ORDER_BONUS)
        
        self.assertEqual(referee.wallet.balance, 0)
        self.assertEqual(self.referrer.wallet.balance, 0)

    def test_referee_verification_activation(self):
        # Signup first
        self.client.post('/signup/', {
            **self.referee_data,
            'referral_code': self.referral_code
        })
        referee = User.objects.get(username='referee')
        
        # Verify user
        referee.is_verified = True
        referee.save()
        
        referee.refresh_from_db()
        
        # Check Bonus Activated
        self.assertEqual(referee.wallet.balance, settings.REFERRAL_SIGNUP_BONUS)
        self.assertEqual(referee.wallet.inactive_balance, 0)
        
        # Check Flag Set
        referral_use = ReferralUse.objects.get(referred_user=referee)
        self.assertTrue(referral_use.referee_bonus_granted)

    def test_referrer_bonus_activation_on_orders(self):
        # Signup first
        self.client.post('/signup/', {
            **self.referee_data,
            'referral_code': self.referral_code
        })
        referee = User.objects.get(username='referee')
        
        # Create 1st Order
        order1 = Order.objects.create(
            user=referee,
            total_amount=Decimal('100.00'),
            status='delivered'
        )
        
        self.referrer.refresh_from_db()
        self.assertEqual(self.referrer.wallet.balance, 0) # Still 0
        
        # Create 2nd Order
        order2 = Order.objects.create(
            user=referee,
            total_amount=Decimal('100.00'),
            status='delivered'
        )
        
        self.referrer.refresh_from_db()
        
        # Check Bonus Activated
        self.assertEqual(self.referrer.wallet.balance, settings.REFERRAL_ORDER_BONUS)
        self.assertEqual(self.referrer.wallet.inactive_balance, 0)
        
        # Check Flag Set
        referral_use = ReferralUse.objects.get(referred_user=referee)
        self.assertTrue(referral_use.referrer_bonus_granted)
