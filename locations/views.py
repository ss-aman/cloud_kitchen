from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Address, ServingBuilding

@login_required
def manage_addresses(request):
    """View to manage user addresses"""
    addresses = Address.objects.filter(user=request.user)
    buildings = ServingBuilding.objects.filter(is_active=True)
    
    context = {
        'addresses': addresses,
        'buildings': buildings
    }
    return render(request, 'locations/manage_addresses.html', context)

@login_required
def add_address(request):
    """Add a new address"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            building_id = data.get('building_id')
            flat_number = data.get('flat_number')
            landmark = data.get('landmark', '')
            is_default = data.get('is_default', False)
            
            if not building_id or not flat_number:
                return JsonResponse({'error': 'Building and flat number are required'}, status=400)
            
            building = get_object_or_404(ServingBuilding, id=building_id, is_active=True)
            
            # If setting as default, remove default from other addresses
            if is_default:
                Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
            
            # If this is the first address, make it default
            if not Address.objects.filter(user=request.user).exists():
                is_default = True
            
            address = Address.objects.create(
                user=request.user,
                serving_building=building,
                flat_number=flat_number,
                landmark=landmark,
                is_default=is_default
            )
            
            return JsonResponse({
                'success': True,
                'address_id': address.id,
                'message': 'Address added successfully'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def set_default_address(request, address_id):
    """Set an address as default"""
    if request.method == 'POST':
        try:
            address = get_object_or_404(Address, id=address_id, user=request.user)
            
            # Remove default from all addresses
            Address.objects.filter(user=request.user).update(is_default=False)
            
            # Set this address as default
            address.is_default = True
            address.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Default address updated'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def delete_address(request, address_id):
    """Delete an address"""
    if request.method == 'POST':
        try:
            address = get_object_or_404(Address, id=address_id, user=request.user)
            was_default = address.is_default
            address.delete()
            
            # If deleted address was default, set another as default
            if was_default:
                first_address = Address.objects.filter(user=request.user).first()
                if first_address:
                    first_address.is_default = True
                    first_address.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Address deleted successfully'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def get_user_addresses(request):
    """Get all user addresses as JSON"""
    addresses = Address.objects.filter(user=request.user).select_related('serving_building')
    
    addresses_data = [{
        'id': addr.id,
        'building_name': addr.serving_building.name,
        'building_address': addr.serving_building.address,
        'flat_number': addr.flat_number,
        'landmark': addr.landmark,
        'is_default': addr.is_default
    } for addr in addresses]
    
    return JsonResponse({'addresses': addresses_data})