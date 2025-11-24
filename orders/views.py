from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def order_page(request):
    return render(request, 'orders/order_page.html')

@login_required
def order_history(request):
    return render(request, 'orders/order_history.html')

@login_required
def order_success(request, order_id):
    return render(request, 'orders/order_success.html')