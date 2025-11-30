from django.db import models
from orders.models import Order

class Delivery(models.Model):
    STATUS_CHOICES = [
        ('searching', 'Searching for Driver'),
        ('confirmed', 'Driver Confirmed'),
        ('picked_up', 'Picked Up'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    provider_name = models.CharField(max_length=50, default='Mock')
    tracking_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='searching')
    estimated_delivery_time = models.DateTimeField(blank=True, null=True)
    driver_name = models.CharField(max_length=100, blank=True, null=True)
    driver_phone = models.CharField(max_length=20, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Delivery for Order {self.order.public_id} - {self.status}"

    class Meta:
        db_table = 'deliveries'
        verbose_name_plural = 'Deliveries'