from django.conf import settings
from .providers.mock_provider import MockDeliveryProvider
from .models import Delivery

class DeliveryService:
    def __init__(self):
        # In a real app, this would be configurable via settings
        self.provider = MockDeliveryProvider()

    def create_delivery(self, order):
        if hasattr(order, 'delivery'):
            return order.delivery

        pickup_address = "Cloud Kitchen HQ, 123 Main St" # Should be from settings
        delivery_address = str(order.address)

        response = self.provider.create_delivery(
            order.public_id,
            pickup_address,
            delivery_address
        )

        delivery = Delivery.objects.create(
            order=order,
            provider_name='Mock',
            tracking_id=response['tracking_id'],
            status=response['status'],
            estimated_delivery_time=response['estimated_delivery_time'],
            metadata=response.get('metadata', {})
        )
        return delivery

    def update_delivery_status(self, delivery):
        if delivery.status in ['delivered', 'cancelled']:
            return delivery

        response = self.provider.track_delivery(delivery.tracking_id)
        
        delivery.status = response['status']
        if 'driver_name' in response:
            delivery.driver_name = response['driver_name']
        if 'driver_phone' in response:
            delivery.driver_phone = response['driver_phone']
        
        delivery.save()
        return delivery
