from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Referral, ReferralUse
from django.utils import timezone
from datetime import timedelta

@login_required
def generate_referral(request):
    """Generate a new referral code for the user"""
    if request.method == 'POST':
        description = request.POST.get('description', '')
        max_uses = int(request.POST.get('max_uses', 0))
        days_valid = int(request.POST.get('days_valid', 30))
        
        expires_at = timezone.now() + timedelta(days=days_valid) if days_valid > 0 else None
        
        referral = Referral.objects.create(
            referrer=request.user,
            description=description,
            max_uses=max_uses,
            expires_at=expires_at
        )
        
        messages.success(request, f'Referral code generated: {referral.code}')
        return redirect('my_referrals')
    
    return render(request, 'referrals/generate.html')

@login_required
def my_referrals(request):
    """View all referrals created by the user"""
    referrals = Referral.objects.filter(referrer=request.user).prefetch_related('uses')
    
    # Build referral data with usage info
    referral_data = []
    for ref in referrals:
        referral_data.append({
            'referral': ref,
            'url': request.build_absolute_uri(f'/signup/?ref={ref.code}'),
            'used_by': ref.uses.all()
        })
    
    context = {
        'referral_data': referral_data
    }
    return render(request, 'referrals/my_referrals.html', context)

@login_required
def get_referral_link(request):
    """API endpoint to get or create a default referral link"""
    # Get or create a default unlimited referral for the user
    referral, created = Referral.objects.get_or_create(
        referrer=request.user,
        referral_type='signup',
        description='Default referral link',
        max_uses=0,
        defaults={'is_active': True}
    )
    
    url = request.build_absolute_uri(f'/signup/?ref={referral.code}')
    
    return JsonResponse({
        'code': referral.code,
        'url': url,
        'uses': referral.uses_count
    })