from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import random

from menu.models import MenuItem
from .models import Order, OrderItem, PaymentQRCode
from wallet.models import CoinWallet

@login_required
def order_page(request):
    menu_items = MenuItem.objects.filter(is_active=True)
    try:
        wallet = CoinWallet.objects.get(user=request.user)
        balance = wallet.balance
    except CoinWallet.DoesNotExist:
        balance = 0
        
    context = {
        'menu_items': menu_items,
        'wallet_balance': balance
    }
    return render(request, 'orders/order_page.html', context)

@login_required
def place_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart_items = data.get('items', {})
            
            if not cart_items:
                return JsonResponse({'error': 'Cart is empty'}, status=400)
            
            # Create Order
            order = Order.objects.create(
                user=request.user,
                total_amount=0, # Will update later
                status='pending'
            )
            
            total_amount = 0
            
            for item_id, quantity in cart_items.items():
                if quantity > 0:
                    menu_item = MenuItem.objects.get(id=item_id)
                    price = menu_item.price
                    total_price = price * quantity
                    
                    OrderItem.objects.create(
                        order=order,
                        menu_item=menu_item,
                        quantity=quantity,
                        price=price
                    )
                    total_amount += total_price
            
            order.total_amount = total_amount
            order.save()
            
            return JsonResponse({'order_id': order.id, 'redirect_url': f'/orders/payment/{order.id}/'})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def payment_page(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Get random active QR code
    qr_codes = PaymentQRCode.objects.filter(is_active=True)
    qr_code = None
    if qr_codes.exists():
        qr_code = random.choice(qr_codes)
        
    context = {
        'order': order,
        'qr_code': qr_code
    }
    return render(request, 'orders/payment.html', context)

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})

@login_required
def order_success(request, order_id):
    return render(request, 'orders/order_success.html')