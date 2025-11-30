from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import random

from menu.models import MenuItem
from .models import Order, OrderItem, PaymentQRCode
from wallet.models import CoinWallet
from delivery.services import DeliveryService

@login_required
def order_page(request):
    menu_items = MenuItem.objects.filter(is_active=True)
    try:
        wallet = CoinWallet.objects.get(user=request.user)
        balance = wallet.balance
    except CoinWallet.DoesNotExist:
        balance = 0
    
    # Get user's default address
    from locations.models import Address, ServingBuilding
    default_address = Address.objects.filter(user=request.user, is_default=True).select_related('serving_building').first()
    all_addresses = Address.objects.filter(user=request.user).select_related('serving_building')
    buildings = ServingBuilding.objects.filter(is_active=True)
        
    context = {
        'menu_items': menu_items,
        'wallet_balance': balance,
        'default_address': default_address,
        'all_addresses': all_addresses,
        'buildings': buildings,
    }
    return render(request, 'orders/order_page.html', context)

@login_required
def place_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart_items = data.get('items', {})
            address_id = data.get('address_id')  # Get selected address
            
            if not cart_items:
                return JsonResponse({'error': 'Cart is empty'}, status=400)
            
            # Validate user has phone number
            if not request.user.phone_number:
                return JsonResponse({
                    'error': 'Phone number required',
                    'validation_error': True,
                    'missing_field': 'phone'
                }, status=400)
            
            # Validate user has a delivery address
            from locations.models import Address
            
            # If address_id provided, use it; otherwise use default
            if address_id:
                delivery_address = Address.objects.filter(id=address_id, user=request.user).first()
            else:
                delivery_address = Address.objects.filter(user=request.user, is_default=True).first()
            
            if not delivery_address:
                return JsonResponse({
                    'error': 'Delivery address required',
                    'validation_error': True,
                    'missing_field': 'address'
                }, status=400)
            
            # Create Order
            order = Order.objects.create(
                user=request.user,
                address=delivery_address,
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

@login_required
def current_orders(request):
    """Display orders placed in the last 36 hours"""
    from django.utils import timezone
    from datetime import timedelta
    
    cutoff_time = timezone.now() - timedelta(hours=36)
    
    orders = Order.objects.filter(
        user=request.user,
        created_at__gte=cutoff_time
    ).order_by('-created_at')
    
    return render(request, 'orders/current_orders.html', {'orders': orders})

@login_required
def confirm_payment(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # In a real app, verify payment here
        order.status = 'confirmed'
        order.save()
        
        # Trigger delivery
        service = DeliveryService()
        try:
            service.create_delivery(order)
        except Exception as e:
            # Log error but don't fail the request? Or fail?
            print(f"Failed to create delivery: {e}")
            
        return JsonResponse({'status': 'success'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def track_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    data = {
        'order_status': order.status,
        'delivery': None
    }
    
    if hasattr(order, 'delivery'):
        # Update status from provider
        service = DeliveryService()
        service.update_delivery_status(order.delivery)
        
        delivery = order.delivery
        data['delivery'] = {
            'status': delivery.status,
            'tracking_id': delivery.tracking_id,
            'estimated_time': delivery.estimated_delivery_time,
            'driver_name': delivery.driver_name,
            'driver_phone': delivery.driver_phone,
        }
        
    return JsonResponse(data)