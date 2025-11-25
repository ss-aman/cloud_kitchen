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
        if ref_code:
            from referrals.models import Referral, ReferralUse
            try:
                referral = Referral.objects.get(code=ref_code.upper())
                if referral.is_valid():
                    ReferralUse.objects.create(
                        referral=referral,
                        referred_user=user
                    )
                    referral.uses_count += 1
                    referral.save()
                    messages.success(request, f'Account created! You were referred by {referral.referrer.username}.')
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