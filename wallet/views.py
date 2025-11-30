from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import CoinWallet

@login_required
def wallet_view(request):
    """Display user's wallet balance and history"""
    wallet, created = CoinWallet.objects.get_or_create(user=request.user)
    
    # Get all credits, ordered by creation date
    credits = wallet.credits.all().order_by('-created_at')
    
    context = {
        'wallet': wallet,
        'credits': credits,
        'active_balance': wallet.balance,
        'inactive_balance': wallet.inactive_balance
    }
    return render(request, 'wallet/wallet.html', context)