from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import Feedback
from orders.models import Order
from delivery.models import Delivery

@login_required
def feedback_form(request):
    """Display feedback form"""
    feedback_type = request.GET.get('type', 'idea')
    order_id = request.GET.get('order_id')
    
    context = {
        'feedback_type': feedback_type,
        'order_id': order_id,
    }
    
    if order_id:
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            context['order'] = order
            if hasattr(order, 'delivery'):
                context['delivery'] = order.delivery
        except Order.DoesNotExist:
            pass
    
    return render(request, 'feedback/feedback_form.html', context)

@login_required
def submit_feedback(request):
    """Handle feedback submission"""
    if request.method == 'POST':
        feedback_type = request.POST.get('feedback_type')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        rating = request.POST.get('rating')
        order_id = request.POST.get('order_id')
        
        # Validation
        if not subject or not message:
            return JsonResponse({'error': 'Subject and message are required'}, status=400)
        
        # Create feedback
        feedback = Feedback.objects.create(
            user=request.user,
            feedback_type=feedback_type,
            subject=subject,
            message=message,
            rating=int(rating) if rating else None
        )
        
        # Associate with order/delivery if provided
        if order_id:
            try:
                order = Order.objects.get(id=order_id, user=request.user)
                feedback.order = order
                if hasattr(order, 'delivery') and feedback_type == 'delivery':
                    feedback.delivery = order.delivery
                feedback.save()
            except Order.DoesNotExist:
                pass
        
        return JsonResponse({'status': 'success', 'message': 'Thank you for your feedback!'})
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def my_feedback(request):
    """Display user's feedback history"""
    feedbacks = Feedback.objects.filter(user=request.user)
    return render(request, 'feedback/my_feedback.html', {'feedbacks': feedbacks})

@login_required
def feedback_success(request):
    """Feedback success page"""
    return render(request, 'feedback/feedback_success.html')
