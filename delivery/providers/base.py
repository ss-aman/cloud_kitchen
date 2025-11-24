from abc import ABC, abstractmethod

class DeliveryProvider(ABC):
    @abstractmethod
    def create_delivery(self, order_id, pickup_address, delivery_address):
        pass
    
    @abstractmethod
    def track_delivery(self, delivery_id):
        pass
    
    @abstractmethod
    def cancel_delivery(self, delivery_id):
        pass
