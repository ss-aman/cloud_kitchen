import os
import django
import sys

# Set up Django environment
sys.path.append('/home/nine/code/cloud_kitchen')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloud_kitchen.settings')
django.setup()

from django.contrib.auth import get_user_model
from orders.models import Order, OrderItem
from menu.models import MenuItem
from locations.models import Address, ServingBuilding
from delivery.models import Delivery
from delivery.services import DeliveryService

User = get_user_model()

def verify_delivery_flow():
    print("Verifying Delivery Flow...")
    
    # 1. Create User and Address
    user, created = User.objects.get_or_create(username='test_delivery_user', defaults={'email': 'test@example.com', 'phone_number': '1234567890'})
    building, _ = ServingBuilding.objects.get_or_create(name="Test Building", address="123 Test St")
    address, _ = Address.objects.get_or_create(user=user, serving_building=building, defaults={'flat_number': '101', 'is_default': True})
    
    # 2. Create Order
    menu_item = MenuItem.objects.first()
    if not menu_item:
        print("No menu items found. Creating one.")
        menu_item = MenuItem.objects.create(name="Test Item", price=100, is_active=True)
        
    order = Order.objects.create(user=user, address=address, total_amount=menu_item.price, status='pending')
    OrderItem.objects.create(order=order, menu_item=menu_item, quantity=1, price=menu_item.price)
    print(f"Order created: {order.public_id}")
    
    # 3. Confirm Payment (Simulate View Logic)
    print("Simulating payment confirmation...")
    order.status = 'confirmed'
    order.save()
    
    service = DeliveryService()
    delivery = service.create_delivery(order)
    print(f"Delivery created: {delivery.tracking_id} - Status: {delivery.status}")
    
    if delivery.status == 'searching':
        print("SUCCESS: Delivery created with initial status.")
    else:
        print(f"FAILURE: Unexpected initial status: {delivery.status}")
        
    # 4. Track Delivery
    print("Tracking delivery...")
    updated_delivery = service.update_delivery_status(delivery)
    print(f"Updated Status: {updated_delivery.status}")
    
    if updated_delivery.status in ['searching', 'confirmed', 'picked_up', 'out_for_delivery', 'delivered']:
        print("SUCCESS: Delivery tracking working.")
    else:
        print(f"FAILURE: Unexpected tracking status: {updated_delivery.status}")

if __name__ == '__main__':
    verify_delivery_flow()
