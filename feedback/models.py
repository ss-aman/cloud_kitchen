from django.db import models
from accounts.models import User
from orders.models import Order
from delivery.models import Delivery

class Feedback(models.Model):
    FEEDBACK_TYPE_CHOICES = [
        ('delivery', 'Delivery Feedback'),
        ('order', 'Order Feedback'),
        ('idea', 'Idea/Suggestion'),
        ('tip', 'Tip/General Feedback'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPE_CHOICES)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedbacks')
    delivery = models.ForeignKey(Delivery, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedbacks')
    rating = models.IntegerField(null=True, blank=True, help_text="Rating from 1-5 (for delivery/order feedback)")
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    admin_response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_feedback_type_display()} - {self.user.username} - {self.created_at.strftime('%Y-%m-%d')}"
    
    class Meta:
        db_table = 'feedbacks'
        ordering = ['-created_at']
        verbose_name_plural = 'Feedbacks'
