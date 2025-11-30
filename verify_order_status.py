import os
import django
from datetime import timedelta
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloud_kitchen.settings')
django.setup()

from django.contrib.auth import get_user_model
from orders.models import Order
from locations.models import Address, ServingBuilding

User = get_user_model()

def run_verification():
    print("Starting Order Status Page Verification...")
    
    # 1. Setup User and Address
    username = 'status_test_user'
    User.objects.filter(username=username).delete()
    user = User.objects.create_user(username=username, password='password123')
    
    building = ServingBuilding.objects.first()
    if not building:
        building = ServingBuilding.objects.create(name="Test Building", address="123 Test St")
        
    address = Address.objects.create(user=user, serving_building=building, flat_number="101")
    
    # 2. Create Orders
    now = timezone.now()
    
    # Order 1: Recent (1 hour ago)
    order1 = Order.objects.create(user=user, address=address, total_amount=100, status='pending')
    order1.created_at = now - timedelta(hours=1)
    order1.save()
    
    # Order 2: Recent (35 hours ago)
    order2 = Order.objects.create(user=user, address=address, total_amount=200, status='confirmed')
    order2.created_at = now - timedelta(hours=35)
    order2.save()
    
    # Order 3: Old (37 hours ago)
    order3 = Order.objects.create(user=user, address=address, total_amount=300, status='delivered')
    order3.created_at = now - timedelta(hours=37)
    order3.save()
    
    print(f"Created 3 orders: 1h ago, 35h ago, 37h ago.")
    
    # 3. Verify Query Logic (Simulating View)
    cutoff_time = now - timedelta(hours=36)
    current_orders = Order.objects.filter(
        user=user,
        created_at__gte=cutoff_time
    ).order_by('-created_at')
    
    print(f"Found {current_orders.count()} current orders.")
    
    ids = [o.id for o in current_orders]
    
    assert order1.id in ids, "Order 1 (1h ago) should be visible"
    assert order2.id in ids, "Order 2 (35h ago) should be visible"
    assert order3.id not in ids, "Order 3 (37h ago) should NOT be visible"
    
    print("Verification Successful! Logic correctly filters last 36 hours.")

if __name__ == '__main__':
    run_verification()
