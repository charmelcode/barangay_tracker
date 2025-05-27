from django.shortcuts import render, get_object_or_404, redirect
from .models import Appliance, Category, BorrowRequest
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .forms import BorrowRequestForm, ApplianceForm
from django.contrib import messages
from django.db import transaction
from django.utils import timezone


@login_required
def home(request):
    categories = Category.objects.all()
    borrow_requests = None

    if request.user.is_authenticated and not request.user.is_staff:
        borrow_requests = BorrowRequest.objects.filter(user=request.user).order_by('-id')

        # Show notifications for approved/declined requests not yet notified
        with transaction.atomic():
            for br in borrow_requests:
                if not br.notified:
                    if br.approved:
                        messages.success(request, f"Your borrow request for '{br.appliance.name}' has been approved.")
                        br.notified = True
                        br.save(update_fields=['notified'])
                    elif br.declined:
                        messages.error(request, f"Your borrow request for '{br.appliance.name}' has been declined.")
                        br.notified = True
                        br.save(update_fields=['notified'])

    return render(request, 'appliances/home.html', {'categories': categories, 'borrow_requests': borrow_requests})
@login_required
def category_appliances(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    appliances = category.appliances.all()
    return render(request, 'appliances/category_list.html', {
        'category': category,
        'appliances': appliances
    })

@login_required
def borrow_appliance(request, appliance_id):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('home')

    appliance = get_object_or_404(Appliance, id=appliance_id)

    if request.method == 'POST':
        form = BorrowRequestForm(request.POST, appliance=appliance)
        if form.is_valid():
            borrow_request = form.save(commit=False)
            borrow_request.user = request.user
            borrow_request.appliance = appliance
            borrow_request.status = 'pending'
            borrow_request.save()
            
            messages.success(
                request, 
                'Your borrow request has been submitted successfully. Please wait for admin approval.'
            )
            return redirect('my_borrow_requests')
    else:
        initial_data = {
            'full_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
        }
        form = BorrowRequestForm(appliance=appliance, initial=initial_data)

    return render(request, 'appliances/borrow_form.html', {
        'form': form,
        'appliance': appliance,
    })

@login_required
def borrow_success(request):
    return render(request, 'appliances/borrow_success.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# Admin check function
def is_admin(user):
    return user.is_staff or user.is_superuser

# Admin view: list pending borrow requests
@user_passes_test(is_admin)
def borrow_requests_list(request):
    requests = BorrowRequest.objects.filter(approved=False)
    return render(request, 'appliances/borrow_requests_list.html', {'requests': requests})

# Admin view: approve a request
@user_passes_test(is_admin)
def approve_borrow_request(request, request_id):
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)
    
    if request.method == 'POST':
        appliance = borrow_request.appliance
        
        # Check if there's enough quantity available
        if appliance.quantity >= borrow_request.quantity:
            with transaction.atomic():
                # Decrease the appliance quantity
                appliance.quantity -= borrow_request.quantity
                appliance.save()
                
                # Approve the request
                borrow_request.approved = True
                borrow_request.declined = False
                borrow_request.notified = False
                borrow_request.save()
                
                messages.success(request, f"Request to borrow '{appliance.name}' was approved and quantity updated.")
        else:
            messages.error(request, f"Cannot approve request. Not enough {appliance.name} available.")
        
        return redirect('borrow_requests_list')
    
    return render(request, 'appliances/approve_borrow_request.html', {
        'borrow_request': borrow_request
    })

@user_passes_test(is_admin)
def decline_borrow_request(request, request_id):
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)

    if request.method == 'POST':
        borrow_request.declined = True
        borrow_request.approved = False  # Clear approved flag
        borrow_request.notified = False  # So user gets notified next time
        borrow_request.save()
        messages.error(request, f"Your borrow request for '{borrow_request.appliance.name}' has been declined.")
        return redirect('borrow_requests_list')

    return render(request, 'appliances/decline_borrow_request.html', {
        'borrow_request': borrow_request
    })

@user_passes_test(is_admin)
def add_appliance(request):
    if request.method == 'POST':
        form = ApplianceForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')  # Or wherever you want to go after
    else:
        form = ApplianceForm()
    
    return render(request, 'appliances/add_appliance.html', {'form': form})

@login_required
def my_borrow_requests(request):
    user_requests = BorrowRequest.objects.filter(user=request.user).order_by('-borrow_date')
    return render(request, 'appliances/my_borrow_requests.html', {'requests': user_requests})

@user_passes_test(is_admin)
def borrow_requests_list(request):
    requests = BorrowRequest.objects.filter(approved=False, declined=False)
    return render(request, 'appliances/borrow_requests_list.html', {'requests': requests})

@user_passes_test(is_admin)
def edit_appliance(request, appliance_id):
    appliance = get_object_or_404(Appliance, id=appliance_id)
    
    if request.method == 'POST':
        form = ApplianceForm(request.POST, request.FILES, instance=appliance)
        if form.is_valid():
            form.save()
            messages.success(request, f"'{appliance.name}' has been updated successfully.")
            return redirect('category_appliances', category_id=appliance.category.id)
    else:
        form = ApplianceForm(instance=appliance)
    
    return render(request, 'appliances/edit_appliance.html', {
        'form': form,
        'appliance': appliance
    })

@user_passes_test(is_admin)
def delete_appliance(request, appliance_id):
    appliance = get_object_or_404(Appliance, id=appliance_id)
    category_id = appliance.category.id
    
    if request.method == 'POST':
        appliance_name = appliance.name
        appliance.delete()
        messages.success(request, f"'{appliance_name}' has been deleted successfully.")
        return redirect('category_appliances', category_id=category_id)
    
    return render(request, 'appliances/delete_appliance.html', {
        'appliance': appliance
    })

@login_required
def return_appliance(request, request_id):
    borrow_request = get_object_or_404(BorrowRequest, id=request_id, approved=True, user=request.user)
    
    if request.method == 'POST':
        with transaction.atomic():
            appliance = borrow_request.appliance
            total_unreturned = borrow_request.unreturned_quantity
            
            if 'all_good' in request.POST:
                # All items are in good condition
                appliance.quantity += total_unreturned
                appliance.save()
                
                # Update the borrow request
                borrow_request.returned_quantity += total_unreturned
                borrow_request.unreturned_quantity = 0
                borrow_request.return_date = timezone.now()
                
                # Record all items as good condition
                borrow_request.resolution_status = {
                    'damaged_count': 0,
                    'resolution': None,
                    'notes': ''
                }
                
                messages.success(
                    request, 
                    f"All {total_unreturned} items returned successfully in good condition."
                )
            else:
                # Some items are damaged/lost
                damaged_count = int(request.POST.get('damaged_count', 0))
                good_count = total_unreturned - damaged_count
                
                if damaged_count > total_unreturned:
                    messages.error(request, "Number of damaged items cannot exceed total unreturned items.")
                    return redirect('return_appliance', request_id=request_id)
                
                # Update appliance quantity for good items
                if good_count > 0:
                    appliance.quantity += good_count
                    appliance.save()
                
                resolution = request.POST.get('damage_resolution')
                damage_notes = request.POST.get('damage_notes', '')
                
                # Store resolution status
                borrow_request.resolution_status = {
                    'damaged_count': damaged_count,
                    'resolution': resolution,
                    'notes': damage_notes
                }
                
                # Update borrow request
                borrow_request.returned_quantity += total_unreturned
                borrow_request.unreturned_quantity = 0
                borrow_request.unreturned_status = 'damaged'
                borrow_request.unreturned_reason = f"{damaged_count} items damaged/lost - {resolution}. Notes: {damage_notes}"
                borrow_request.return_date = timezone.now()
                
                messages.success(
                    request, 
                    f"Return processed: {good_count} items in good condition, {damaged_count} items damaged/lost."
                )
                if resolution:
                    messages.info(request, f"Resolution for damaged items: {resolution}")
            
            borrow_request.save()
        
        return redirect('my_borrow_requests')
    
    # For GET request, prepare the context
    return render(request, 'appliances/return_appliance.html', {
        'borrow_request': borrow_request,
        'remaining_items': range(borrow_request.unreturned_quantity)
    })

@user_passes_test(is_admin)
def borrowers_list(request):
    # Get all approved borrow requests
    borrow_requests = BorrowRequest.objects.filter(
        approved=True
    ).order_by('-borrow_date')
    
    return render(request, 'appliances/borrowers_list.html', {
        'borrow_requests': borrow_requests
    })
