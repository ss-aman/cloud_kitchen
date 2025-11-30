import uuid
import random
from datetime import timedelta
from django.utils import timezone
from .base import DeliveryProvider

class MockDeliveryProvider(DeliveryProvider):
    def create_delivery(self, order_id, pickup_address, delivery_address):
        # Simulate API call to create delivery
        tracking_id = f"MOCK-{uuid.uuid4().hex[:8].upper()}"
        estimated_time = timezone.now() + timedelta(minutes=random.randint(30, 60))
        
        return {
            'tracking_id': tracking_id,
            'status': 'searching',
            'estimated_delivery_time': estimated_time,
            'metadata': {
                'provider': 'MockProvider',
                'pickup': pickup_address,
                'drop': delivery_address
            }
        }

    def track_delivery(self, delivery_id):
        # Simulate status update
        statuses = ['searching', 'confirmed', 'picked_up', 'out_for_delivery', 'delivered']
        current_status = random.choice(statuses)
        
        data = {
            'status': current_status,
            'metadata': {}
        }
        
        if current_status in ['confirmed', 'picked_up', 'out_for_delivery']:
            data['driver_name'] = "John Doe"
            data['driver_phone'] = "+1234567890"
            
        return data

    def cancel_delivery(self, delivery_id):
        return True
