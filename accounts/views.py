from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import User

def home(request):
    return redirect('order_page')

from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser or user.is_staff:
                return redirect('/admin/')
            return redirect('order_page')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')

def signup_view(request):
    referral_code = request.GET.get('ref', '')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        ref_code = request.POST.get('referral_code', '')
        
        # Validation
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/signup.html', {'referral_code': ref_code})
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'accounts/signup.html', {'referral_code': ref_code})
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'accounts/signup.html', {'referral_code': ref_code})
        
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        
        # Handle referral code if provided
        # Handle referral code if provided
        if ref_code:
            from referrals.models import Referral, ReferralUse
            from wallet.models import WalletCredit
            from django.conf import settings
            
            try:
                referral = Referral.objects.get(code=ref_code.upper())
                if referral.is_valid():
                    # Create ReferralUse record
                    referral_use = ReferralUse.objects.create(
                        referral=referral,
                        referred_user=user
                    )
                    
                    referral.uses_count += 1
                    referral.save()
                    
                    # 1. Credit Referee (New User) - Signup Bonus
                    # This credit is INACTIVE until verification
                    referee_credit = user.wallet.add_credit(
                        amount=referral.referee_reward_amount,
                        source='REFERRAL_SIGNUP',
                        description=f'Signup bonus via {referral.referrer.username}',
                        expires_in_days=referral.reward_expiry_days,
                        is_active=False # Inactive until verified
                    )
                    referral_use.referee_credit = referee_credit
                    
                    # 2. Credit Referrer - Referrer Bonus
                    # This credit is INACTIVE until referee completes orders
                    referrer_credit = referral.referrer.wallet.add_credit(
                        amount=referral.referrer_reward_amount,
                        source='REFERRAL_REWARD',
                        description=f'Referral bonus for {user.username}',
                        expires_in_days=referral.reward_expiry_days,
                        is_active=False # Inactive until conditions met
                    )
                    referral_use.referrer_credit = referrer_credit
                    
                    referral_use.save()
                    
                    messages.success(request, f'Account created! You were referred by {referral.referrer.username}. Bonus credits added to your wallet (pending verification).')
                else:
                    messages.warning(request, 'Referral code is no longer valid, but account created successfully.')
            except Referral.DoesNotExist:
                messages.warning(request, 'Invalid referral code, but account created successfully.')
        else:
            messages.success(request, 'Account created successfully!')
        
        # Log the user in
        login(request, user)
        return redirect('order_page')
    
    return render(request, 'accounts/signup.html', {'referral_code': referral_code})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def update_phone(request):
    """Update user phone number"""
    if request.method == 'POST':
        from django.http import JsonResponse
        import json
        
        try:
            data = json.loads(request.body)
            phone_number = data.get('phone_number', '').strip()
            
            if not phone_number:
                return JsonResponse({'error': 'Phone number is required'}, status=400)
            
            # Check if phone number already exists for another user
            if User.objects.filter(phone_number=phone_number).exclude(id=request.user.id).exists():
                return JsonResponse({'error': 'Phone number already in use'}, status=400)
            
            request.user.phone_number = phone_number
            request.user.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Phone number updated successfully'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)