from abc import ABC, abstractmethod

class PaymentGateway(ABC):
    @abstractmethod
    def create_payment(self, amount, order_id, user_data):
        pass
    
    @abstractmethod
    def verify_payment(self, payment_id, signature):
        pass
    
    @abstractmethod
    def refund_payment(self, payment_id, amount):
        pass
