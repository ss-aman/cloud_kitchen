from django.contrib import admin
from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'feedback_type', 'subject', 'rating', 'is_resolved', 'created_at')
    list_filter = ('feedback_type', 'is_resolved', 'rating', 'created_at')
    search_fields = ('user__username', 'subject', 'message')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Feedback Information', {
            'fields': ('user', 'feedback_type', 'order', 'delivery', 'rating')
        }),
        ('Content', {
            'fields': ('subject', 'message')
        }),
        ('Admin Response', {
            'fields': ('is_resolved', 'admin_response')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
