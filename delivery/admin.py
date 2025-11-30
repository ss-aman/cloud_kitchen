from django.contrib import admin
from .models import Delivery

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('order', 'provider_name', 'tracking_id', 'status', 'driver_name', 'created_at')
    list_filter = ('status', 'provider_name', 'created_at')
    search_fields = ('tracking_id', 'order__public_id', 'driver_name')
    readonly_fields = ('created_at', 'updated_at')